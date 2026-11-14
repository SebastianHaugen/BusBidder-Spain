"""
Command line interafce for busbidder Spain.
"""

from datetime import date

from busbidder.loading import load_destinations
from busbidder.models import TravelRequest

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
       
    travel_request = TravelRequest(
        destination=destination,
        earliest_date=earliest_date,
        latest_date=latest_date,
        max_price=price,
        max_transfers=transfers,
        requires_changeable=changeable,
        seats_needed=seats
    )
    
    