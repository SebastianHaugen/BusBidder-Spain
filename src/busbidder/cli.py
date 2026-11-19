"""
Command line interafce for busbidder Spain.
"""
import sys
from functools import wraps
from datetime import date

from busbidder.loading import load_destinations, load_profiles, load_offers, load_companies
from busbidder.models import TravelRequest
from busbidder.booking import book_offer, load_bookings, save_bookings
from busbidder.filtering import filter_offers
from busbidder.scoring.ranker import rank_offers
from busbidder.scoring.explain import explain_offer
from busbidder.exceptions import BookingError, BusBidderError
from busbidder.logging_setup import setup_logging

def ask_int(prompt, min_value, max_value):
    # Ask until the user enters a valid integer within the specified range.
    while True:
        try:
            value = int(input(prompt))
            if min_value <= value <= max_value:
                return value
            else:
                print(f"Please enter a number between {min_value} and {max_value}.")
        except ValueError:
            print("Invalid input. Please enter a valid integer.")

def choose_destination(destinations):
    print("Available destinations:")
    for number, name in enumerate(destinations, start=1):
        print(f"{number}. {name}")

    choice = ask_int(f"Choose a destination (1-{len(destinations)}): ", 1, len(destinations))
    return destinations[choice - 1]

def ask_date(prompt: str) -> date:
    """Ask until the user enters a valid date in YYYY-MM-DD format."""
    while True:
        text = input(prompt).strip()
        try:
            return date.fromisoformat(text)
        except ValueError:
            print("Invalid date. Please use the format YYYY-MM-DD, e.g. 2026-07-12.")
            
def ask_price(prompt, min_value, max_value):
    # Ask until the user enters a valid float within the specified range.
    while True:
        try:
            value = float(input(prompt))
            if min_value <= value <= max_value:
                return value
            else:
                print(f"Please enter a price between {min_value} and {max_value}.")
        except ValueError:
            print("Invalid input. Please enter a valid number.")

def ask_yes_no(prompt):
    # Ask until the user enters 'y' or 'n', returning True for 'y' and False for 'n'.
    while True:
        answer = input(prompt + " (y/n): ").strip().lower()
        if answer == 'y':
            return True
        elif answer == 'n':
            return False
        else:
            print("Invalid input. Please enter 'y' for yes or 'n' for no.")

def ask_travel_profile(profiles):
    print("Available travel profiles:")
    # Print each profile with its preferences and weights
    for number, profile in enumerate(profiles.values(), start=1):
        w = profile.weights
        print(f"{number}. {profile.name:<29} prefers {profile.preferred_departure:%H:%M} | "
              f"price {w['price']:.0%}, duration {w['duration']:.0%}, "
              f"time {w['departure_time']:.0%}, flexibility {w['flexibility']:.0%}")

    # Ask the user to choose a profile by number
    choice = ask_int(f"Choose a travel profile (1-{len(profiles)}): ", 1, len(profiles))
    return list(profiles.values())[choice - 1]

def show_ranking(ranked):
    """Print the ranked offers as an aligned table with criterion scores."""
    print("\nRanking")
    print(f"{'':<2}  {'':<15} {'':<16} {'Offer':^15}  {'Scores (0-100)':^23}  {'':>5}")
    print(f"{'#':>2}  {'Company':<15} {'Departs':<16} {'Price':>7} {'Dur.':>6}  "
          f"{'Price':>5} {'Dur.':>5} {'Time':>5} {'Flex':>5}  {'Total':>5}")
    print("-" * 88)

    # Print each ranked offer with its scores and total score
    for rank, (offer, total, scores) in enumerate(ranked, start=1):
        h, m = divmod(offer.duration_minutes, 60)
        print(
            f"{rank:>2}  {offer.company.name:<15} "
            f"{offer.departure:%Y-%m-%d %H:%M} "
            f"€{offer.price:>6.2f} {h:>2}h{m:02d}  "
            f"{scores['price']:>5.0f} {scores['duration']:>5.0f} "
            f"{scores['departure_time']:>5.0f} {scores['flexibility']:>5.0f}  "
            f"{total:>5.1f}"
        )
    
    # Explain the scoring system to the user
    print("-" * 88)
    print("Scores: 0-100 per criterion, higher is better. "
          "Total = weighted sum using your profile's weights.")

def show_rejected(rejected, destination):
    """Print rejected offers for the chosen destination, and count the rest."""
    relevant = [(o, r) for o, r in rejected if o.destination == destination]
    other = len(rejected) - len(relevant)

    print(f"\nRejected offers to {destination}")
    print(f"{'Company':<15} {'Departs':<16} {'Price':>7} {'Dur.':>6}  Reasons")
    print("-" * 88)
    for offer, reasons in relevant:
        h, m = divmod(offer.duration_minutes, 60)
        print(f"{offer.company.name:<15} {offer.departure:%Y-%m-%d %H:%M} "
              f"€{offer.price:>6.2f} {h:>2}h{m:02d}  {'; '.join(reasons)}")

    if other:
        print(f"({other} offers to other destinations not shown.)")

def show_confirmation(booking, offer):
    """Print a clear confirmation for a completed booking."""
    fare = booking.fare_conditions
    fare_text = ", ".join([
        "changeable" if fare.changeable else "not changeable",
        "refundable" if fare.refundable else "non-refundable",
        f"{fare.baggage_limit} kg baggage",
    ])
    total_price = offer.price * booking.seats

    print("\nBooking confirmed")
    print("-" * 40)
    print(f"{'Reference:':<14}{booking.reference}")
    print(f"{'Company:':<14}{offer.company.name}")
    print(f"{'Route:':<14}Madrid -> {offer.destination}")
    print(f"{'Departure:':<14}{offer.departure:%Y-%m-%d %H:%M}")
    print(f"{'Arrival:':<14}{offer.arrival:%Y-%m-%d %H:%M}")
    print(f"{'Seats:':<14}{booking.seats}")
    print(f"{'Total price:':<14}€{total_price:.2f}")
    print(f"{'Fare:':<14}{fare_text}")
    print(f"{'Payment:':<14}{booking.payment_status} (simulated, no real payment taken)")
    print("-" * 40)

def choose_offer(ranked):
    """Ask the user to choose an offer from the ranked list."""
    while True:
        choice = ask_int(f"Choose an offer to book (1-{len(ranked)}), or 0 to exit: ", 0, len(ranked))
        if choice == 0:
            return None
        else:
            return ranked[choice - 1][0]  # Return the Offer object

def graceful_exit(func):
    """Run func, turning user cancellation and expected app errors into clean exits.

    Ctrl+C / end-of-input and BusBidder errors print a short message instead
    of a traceback. Unexpected exceptions are not caught, so real bugs still
    show a full traceback.
    """
    @wraps(func)
    def wrapper(*args, **kwargs): 
        try:
            return func(*args, **kwargs)
        except (KeyboardInterrupt, EOFError):
            print("\nOperation cancelled by user. Exiting.")
            sys.exit(130)
        except BusBidderError as e:
            print(f"\nError: {e}")
            sys.exit(1)
    return wrapper

@graceful_exit
def main() -> None:
    """ Run the interactive BusBidder program """   
    setup_logging()
    destinations = sorted(load_destinations())
    
    # Welcome the user and ask for their travel preferences
    print("Welcome to BusBidder Spain!")
    destination = choose_destination(destinations)
    earliest_date = ask_date("Enter the earliest departure date (YYYY-MM-DD): ")
    
    # Ensure that the latest date is not earlier than the earliest date
    while True:
        latest_date = ask_date("Enter the latest departure date (YYYY-MM-DD): ")
        if latest_date >= earliest_date:
            break
        print("Latest departure date must be on or after the earliest departure date.")
    
    # Ask the user for the number of seats, maximum price, changeable requirement, and number of transfers
    seats = ask_int("Enter the number of seats needed (1-10): ", 1, 10)
    price = ask_price("Enter the maximum price per seat you are willing to pay: ", 0.01, 1000.00)
    changeable = ask_yes_no("Do you require a changeable ticket?")
    transfers = ask_int("Enter the number of transfers you are willing to make (0-5): ", 0, 5)
    travel_profile = ask_travel_profile(load_profiles())    
    
    # Print a summary of the user's choices
    print(f"\nSearching: {destination}, {earliest_date} to {latest_date}, "
          f"{seats} seat(s), max €{price:.2f}, "
          f"{'changeable required' if changeable else 'any fare'}, "
          f"max {transfers} transfer(s), {travel_profile.name}")
    
    # Create a TravelRequest object based on the user's input       
    travel_request = TravelRequest(
        destination=destination,
        earliest_date=earliest_date,
        latest_date=latest_date,
        max_price=price,
        max_transfers=transfers,
        requires_changeable=changeable,
        seats_needed=seats
    )
    
    # Load offers and filter them based on the travel request 
    offers = load_offers(load_companies(), set(destinations))
    bookings = load_bookings()
    accepted, rejected = filter_offers(offers, travel_request, bookings)
    show_rejected(rejected, destination) 

    # If no offers were accepted, inform the user and exit
    if not accepted:
        print("No offers match your requirements.")
        return

    # Rank the accepted offers based on the travel profile and show the ranking
    ranked = rank_offers(accepted, travel_request, travel_profile)
    show_ranking(ranked)
    
    # Explain the top-ranked offer to the user
    top_offer, top_total, top_scores = ranked[0]
    print()
    print(explain_offer(top_offer, top_total, top_scores, travel_profile)) #Explain the top-ranked offer
    
    # Ask the user to choose an offer to book
    book_offer_choice = choose_offer(ranked)
    if book_offer_choice:
        try: 
            booked = book_offer(book_offer_choice, seats, bookings)
            save_bookings(bookings)
            show_confirmation(booked, book_offer_choice)
        except (BookingError) as e:
            print(f"Error booking offer: {e}")
            return