"""
All logic related to booking an offer.
"""

import json
import random
import re
import string
from datetime import datetime
from pathlib import Path

from busbidder.models import Booking, FareConditions, Offer
from busbidder.exceptions import BookingError, DataValidationError

REFERENCE_PATTERN = re.compile(r"^\d+-\d+-[A-Z0-9]{5}$")
BOOKINGS_FILE = Path("output/bookings.json")

def generate_reference(offer_id: int, seats: int, existing: set[str]) -> str:
    """Generate a unique booking reference based on the offer ID and number of seats."""
    
    while True:
        code = random.choices(string.ascii_uppercase + string.digits, k=5)
        reference = f"{offer_id}-{seats}-" + ''.join(code)
        if reference not in existing:
            return reference
    
def validate_reference(reference: str) -> bool:
    """ 
    Validate the format of a booking refence. It should be in the format OFFERID-SEATS-CODE, 
    where OFFERID and SEATS are integers and CODE is a 5-character alphanumeric string.
    """
    return REFERENCE_PATTERN.fullmatch(reference) is not None
        
def seats_left(offer: Offer, bookings: list[Booking]) -> int:
    """Calculate the number of seats left for an offer."""
    booked = sum(b.seats for b in bookings if b.offer_id == offer.offer_id)
    return offer.seats_available - booked

def book_offer(offer: Offer, seats: int, bookings: list[Booking]) -> Booking:
    """Book seats on an offer, add the booking to the list and return it."""
    if seats <= 0:
        raise BookingError(f"seats must be positive, got {seats}")        
    
    available = seats_left(offer, bookings)
    if available < seats:
        raise BookingError(
            f"only {available} seat(s) left on offer {offer.offer_id}, "
            f"requested {seats}"
        )

    reference = generate_reference(
        offer.offer_id, seats, {b.reference for b in bookings}
    )

    new_booking = Booking(
        reference=reference,
        offer_id=offer.offer_id,
        seats=seats,
        fare_conditions=offer.fare_conditions,
        booked_at=datetime.now(),
    )

    bookings.append(new_booking)
    return new_booking
    
def save_bookings(bookings: list[Booking], path: Path = BOOKINGS_FILE) -> None:
    """ save booking as a JSON file to the given path """    
    bookings_data = {
        "bookings": [
            {
                "reference": b.reference,
                "offer_id": b.offer_id,
                "seats": b.seats,
                "booked_at": b.booked_at.isoformat(),
                "payment_status": b.payment_status,
                "fare_conditions": {
                    "changeable": b.fare_conditions.changeable,
                    "refundable": b.fare_conditions.refundable,
                    "baggage_limit": b.fare_conditions.baggage_limit
                }
            }
            for b in bookings
        ]   
    }
    
    path.parent.mkdir(parents=True, exist_ok=True)
    
    with open(path, 'w', encoding="utf-8") as f:
        json.dump(bookings_data, f, indent=2)

def load_bookings(path: Path = BOOKINGS_FILE) -> list[Booking]:
    """
    Load bookings from a JSON file.

    A missing file means no bookings have been made yet, so an empty list
    is returned. Invalid records are rejected individually.
    """
    if not path.exists():
        return []

    with open(path, "r", encoding="utf-8") as f:
        data = json.load(f)

    bookings: list[Booking] = []
    seen: set[str] = set()

    for record in data.get("bookings", []):
        try:
            reference = record["reference"]

            if not validate_reference(reference):
                raise DataValidationError(f"invalid reference format {reference!r}")
            if reference in seen:
                raise DataValidationError(f"duplicate reference {reference!r}")

            fc = record["fare_conditions"]
            booking = Booking(
                reference=reference,
                offer_id=int(record["offer_id"]),
                seats=int(record["seats"]),
                fare_conditions=FareConditions(
                    fc["changeable"], fc["refundable"], fc["baggage_limit"]
                ),
                booked_at=datetime.fromisoformat(record["booked_at"]),
                payment_status=record.get("payment_status", "SIMULATED_PAID"),
            )

            seen.add(reference)
            bookings.append(booking)

        except KeyError as e:
            print(f"Rejected booking record, missing field {e}: {record}")
        except (ValueError, TypeError) as e:
            print(f"Rejected booking record ({e}): {record}")

    return bookings