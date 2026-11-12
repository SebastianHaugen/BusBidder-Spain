"""
All logic related to booking an offer.
"""

from datetime import datetime
import string
import random
import re

from busbidder.models import Booking, Offer
from busbidder.exceptions import BookingError

REFERENCE_PATTERN = re.compile(r"^\d+-\d+-[A-Z0-9]{5}$")

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
    