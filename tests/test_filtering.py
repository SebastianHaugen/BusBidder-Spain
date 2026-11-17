"""
Tests for the filtering module and that its working correctly.
"""

from datetime import date, datetime

from busbidder.filtering import check_offer
from busbidder.models import Booking, Company, FareConditions, Offer, TravelRequest


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

REQUEST = TravelRequest("Malaga", date(2026, 7, 12), date(2026, 7, 14),
                        max_price=50, max_transfers=1, requires_changeable=True)

def test_valid_offer_passes():
    """A valid offer that meets all the request criteria passes the check."""
    assert check_offer(make_offer(), REQUEST, []) == []

def test_price_exactly_at_budget_passes():
    """An offer with a price exactly equal to the request's max_price passes the check."""
    assert check_offer(make_offer(price=50.0), REQUEST, []) == []
    
def test_price_over_budget_fails():
    """An offer with a price above the request's max_price fails the check."""
    reasons = check_offer(make_offer(price=60.0), REQUEST, [])
    assert any("Price" in reason for reason in reasons)

def test_departure_on_first_and_last_day_passes():
    """Boundary: departures on the first and last day of the window pass."""
    first = make_offer(departure=datetime(2026, 7, 12, 9, 0),
                       arrival=datetime(2026, 7, 12, 15, 0))
    last = make_offer(departure=datetime(2026, 7, 14, 23, 59),
                      arrival=datetime(2026, 7, 15, 6, 0))
    assert check_offer(first, REQUEST, []) == []
    assert check_offer(last, REQUEST, []) == []

def test_departure_outside_window_rejected():
    """Boundary: departures one minute outside the window are rejected."""
    before = make_offer(departure=datetime(2026, 7, 11, 23, 59),
                        arrival=datetime(2026, 7, 12, 6, 0))
    after = make_offer(departure=datetime(2026, 7, 15, 0, 0),
                       arrival=datetime(2026, 7, 15, 6, 0))
    assert any("Departure" in r for r in check_offer(before, REQUEST, []))
    assert any("Departure" in r for r in check_offer(after, REQUEST, []))

def test_too_many_transfers_rejected():
    """An offer with more transfers than the request allows is rejected."""
    reasons = check_offer(make_offer(transfers=2), REQUEST, [])
    assert any("Transfers" in reason for reason in reasons)

def test_not_changeable_rejected_when_required():
    """An offer that is not changeable is rejected if the request requires changeable."""
    reasons = check_offer(make_offer(fare_conditions=FareConditions(changeable=False, refundable=False, baggage_limit=20)), REQUEST, [])
    assert any("changeable" in reason for reason in reasons)
    

def test_last_free_seat_still_passes():
    """ 9 of 10 seats booked leaves exactly the 1 seat requested. """
    bookings = [make_booking(offer_id=1, seats=9)]
    assert check_offer(make_offer(seats_available=10), REQUEST, bookings) == []

def test_fully_booked_offer_rejected():
    """ 10 of 10 seats booked leaves no seats for the request. """
    bookings = [make_booking(offer_id=1, seats=6, reference="1-6-AAAAA"),
                make_booking(offer_id=1, seats=4, reference="1-4-BBBBB")]
    reasons = check_offer(make_offer(seats_available=10), REQUEST, bookings)
    assert any("seats" in reason for reason in reasons)
    
def test_wrong_destination_rejected():
    """An offer with a destination that does not match the request is rejected."""
    reasons = check_offer(make_offer(destination="Barcelona"), REQUEST, [])
    assert any("Destination" in reason for reason in reasons)