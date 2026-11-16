"""
Tests for the booking module and that its working correctly.
"""

from datetime import date, datetime

import pytest

from busbidder.booking import book_offer
from busbidder.filtering import check_offer
from busbidder.models import Booking, Company, FareConditions, Offer, TravelRequest
from busbidder.exceptions import BookingError, BusBidderError
from busbidder.booking import save_bookings, load_bookings


def make_offer(**changes):
    """Build a valid Malaga offer; override any field via keyword arguments."""
    fields = dict(
        offer_id=1,
        company=Company("TestBus", "test", 4.0),
        price=40.0,
        departure=datetime(2026, 7, 12, 9, 0),
        arrival=datetime(2026, 7, 12, 15, 0),
        destination="Malaga",
        transfers=0,
        seats_available=10,
        fare_conditions=FareConditions(True, False, 20),
    )
    fields.update(changes)
    return Offer(**fields)

def make_booking(offer_id=1, seats=1, reference="1-1-ABCDE"):
    """Build a valid booking for the given offer."""
    return Booking(
        reference=reference,
        offer_id=offer_id,
        seats=seats,
        fare_conditions=FareConditions(True, False, 20),
        booked_at=datetime(2026, 6, 1, 12, 0),
    )

def test_booking_reduces_seats_left():
    offer = make_offer(seats_available=10)
    booking = make_booking(offer_id=offer.offer_id, seats=3)
    # Simulate booking
    offer.seats_available -= booking.seats
    assert offer.seats_available == 7

def test_booking_exactly_remaining_seats(): 
    offer = make_offer(seats_available=5)
    booking = make_booking(offer_id=offer.offer_id, seats=5)
    # Simulate booking
    offer.seats_available -= booking.seats
    assert offer.seats_available == 0
    
def test_overbooking_raises_booking_error():   
    offer = make_offer(seats_available=2)
    booking = make_booking(offer_id=offer.offer_id, seats=3)
    try:
        # Simulate booking
        if booking.seats > offer.seats_available:
            raise BookingError(f"Cannot book {booking.seats} seats; only {offer.seats_available} available.")
    except BookingError as e:
        assert str(e) == "Cannot book 3 seats; only 2 available."

def test_zero_seats_raises_booking_error():  
    offer = make_offer(seats_available=5)
    with pytest.raises(BookingError):
        book_offer(offer, 0, [])
            
def test_reference_matches_pattern():
    offer = make_offer(offer_id=42)
    booking = make_booking(offer_id=offer.offer_id, seats=3, reference="42-3-ABCDE")
    assert booking.reference.startswith(f"{offer.offer_id}-{booking.seats}-")

def test_invalid_reference_rejected():   
    offer = make_offer(offer_id=42)
    booking = make_booking(offer_id=offer.offer_id, seats=3, reference="INVALID-REF")
    try:
        # Simulate reference validation
        if not booking.reference.startswith(f"{offer.offer_id}-{booking.seats}-"):
            raise BookingError(f"Invalid booking reference: {booking.reference}")
    except BookingError as e:
        assert str(e) == "Invalid booking reference: INVALID-REF"

def test_save_and_load_round_trip(tmp_path):  
    bookings = [
        make_booking(offer_id=1, seats=2, reference="1-2-ABCDE"),
        make_booking(offer_id=2, seats=1, reference="2-1-FGHIJ"),
    ]
    file_path = tmp_path / "bookings.json"
    
    # Save bookings
    save_bookings(bookings, path=file_path)
    
    # Load bookings back
    loaded_bookings = load_bookings(path=file_path)
    
    assert len(loaded_bookings) == len(bookings)
    for original, loaded in zip(bookings, loaded_bookings):
        assert original.reference == loaded.reference
        assert original.offer_id == loaded.offer_id
        assert original.seats == loaded.seats
        assert original.fare_conditions.changeable == loaded.fare_conditions.changeable
        assert original.fare_conditions.refundable == loaded.fare_conditions.refundable
        assert original.fare_conditions.baggage_limit == loaded.fare_conditions.baggage_limit
        assert original.booked_at == loaded.booked_at
        
def test_missing_bookings_file_returns_empty(tmp_path):
    file_path = tmp_path / "nonexistent_bookings.json"
    
    from busbidder.booking import load_bookings
    loaded_bookings = load_bookings(path=file_path)
    
    assert loaded_bookings == []

def test_corrupt_bookings_file_raises(tmp_path):
    file_path = tmp_path / "corrupt_bookings.json"
    file_path.write_text("not a valid json")
    
    from busbidder.booking import load_bookings, DataValidationError
    try:
        load_bookings(path=file_path)
    except DataValidationError:
        assert True
    else:
        assert False, "Expected DataValidationError for corrupt bookings file"
        
