"""
Command line interafce for busbidder Spain.
"""

from datetime import date

from busbidder.loading import load_destinations, load_profiles, load_offers, load_companies
from busbidder.models import TravelRequest
from busbidder.booking import book_offer, seats_left, load_bookings, save_bookings
from busbidder.filtering import filter_offers
from busbidder.scoring.ranker import rank_offers

def ask_int(prompt, min_value, max_value):
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
            
def ask_seats(prompt, min_value, max_value):
    return ask_int(prompt, min_value, max_value)

def ask_price(prompt, min_value, max_value):
    while True:
        try:
            value = float(input(prompt))
            if min_value <= value <= max_value:
                return value
            else:
                print(f"Please enter a price between {min_value} and {max_value}.")
        except ValueError:
            print("Invalid input. Please enter a valid number.")
            
def ask_transfers(prompt, min_value, max_value):
    return ask_int(prompt, min_value, max_value)

def ask_yes_no(prompt):
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
    for number, profile in enumerate(profiles.values(), start=1):
        print(f"{number}. {profile.name}")

    choice = ask_int(f"Choose a travel profile (1-{len(profiles)}): ", 1, len(profiles))
    return list(profiles.values())[choice - 1]

def show_ranking(ranked):
    """Print the ranked offers as an aligned table with criterion scores."""
    print("\nRanking")
    print(f"{'':<2}  {'':<15} {'':<16} {'Offer':^15}  {'Scores (0-100)':^23}  {'':>5}")
    print(f"{'#':>2}  {'Company':<15} {'Departs':<16} {'Price':>7} {'Dur.':>6}  "
          f"{'Price':>5} {'Dur.':>5} {'Time':>5} {'Flex':>5}  {'Total':>5}")
    print("-" * 88)

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

    print("-" * 88)
    print("Scores: 0-100 per criterion, higher is better. "
          "Total = weighted sum using your profile's weights.")


def show_rejected(rejected):
    """Print the rejected offers as an aligned table with rejection reasons."""
    print("\nRejected Offers")
    print(f"{'Company':<15} {'Departs':<16} {'Price':>7} {'Dur.':>6}  "
          f"{'Reasons'}")
    print("-" * 88)

    for offer, reasons in rejected:
        h, m = divmod(offer.duration_minutes, 60)
        print(
            f"{offer.company.name:<15} "
            f"{offer.departure:%Y-%m-%d %H:%M} "
            f"€{offer.price:>6.2f} {h:>2}h{m:02d}  "
            f"{'; '.join(reasons)}"
        )

def main() -> None:
    """ Run the interactive BusBidder program """
    destinations = sorted(load_destinations())
    
    print("Welcome to BusBidder Spain!")
    destination = choose_destination(destinations)
    print(f"You have chosen: {destination}")
    earliest_date = ask_date("Enter the earliest departure date (YYYY-MM-DD): ")
    
    while True:
        latest_date = ask_date("Enter the latest departure date (YYYY-MM-DD): ")
        if latest_date >= earliest_date:
            break
        print("Latest departure date must be on or after the earliest departure date.")
    
    print(f"Earliest departure date: {earliest_date} ")
    print(f"Latest departure date: {latest_date} ")
    seats = ask_seats("Enter the number of seats needed (1-10): ", 1, 10)
    print(f"Number of seats needed: {seats} ")
    price = ask_price("Enter the maximum price you are willing to pay: ", 0.01, 1000.00)
    print(f"Maximum price: {price} ")
    changeable = ask_yes_no("Do you require a changeable ticket?")
    print(f"Changeable ticket: {changeable} ")
    transfers = ask_transfers("Enter the number of transfers you are willing to make (0-5): ", 0, 5)
    print(f"Number of transfers: {transfers} ")
    travel_profile = ask_travel_profile(load_profiles())    
    
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
    accepted, rejected = filter_offers(offers, travel_request)
    show_rejected(rejected)

    if not accepted:
        print("No offers match your requirements.")
        return

    ranked = rank_offers(accepted, travel_request, travel_profile)
    show_ranking(ranked)
    
    
    