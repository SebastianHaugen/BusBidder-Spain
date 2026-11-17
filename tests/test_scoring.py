"""
Tests for the scoring criteria and ranking.
"""

from datetime import datetime, time

import pytest

from busbidder.models import Company, FareConditions, Offer, TravellerProfile
from busbidder.scoring.ranker import rank_offers
from busbidder.scoring.criteria import score_price, score_departure_time, score_flexibility


def make_offer(**changes):
    """Build a valid Malaga offer, override any field via keyword arguments."""
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


PROFILE = TravellerProfile(
    "Balanced traveller",
    time(9, 0),
    {"price": 0.4, "duration": 0.25, "departure_time": 0.15, "flexibility": 0.2},
)

def test_cheapest_offer_gets_price_score_100():
    """The cheapest offer among a set of offers gets a price score of 100, the most expensive gets 0."""
    cheap = make_offer(offer_id=1, price=20.0)
    dear = make_offer(offer_id=2, price=40.0)
    offers = [cheap, dear]

    assert score_price(cheap, offers, None, PROFILE) == 100
    assert score_price(dear, offers, None, PROFILE) == 0

def test_equal_prices_all_score_100():     
    """If all offers have the same price, they all get a score of 100."""
    equal1 = make_offer(offer_id=1, price=40.0)
    equal2 = make_offer(offer_id=2, price=40.0)
    offers = [equal1, equal2]
    
    assert score_price(equal1, offers, None, PROFILE) == 100
    assert score_price(equal2, offers, None, PROFILE) == 100

def test_departure_penalty_per_hour():
    """Departure time score is 100 at the preferred time, minus 10 points per hour away, minimum 0."""
    on_time = make_offer(offer_id=1, departure=datetime(2026, 7, 12, 9, 0))
    two_hours_late = make_offer(offer_id=2, departure=datetime(2026, 7, 12, 11, 0),
                                arrival=datetime(2026, 7, 12, 17, 0))
    offers = [on_time, two_hours_late]

    assert score_departure_time(on_time, offers, None, PROFILE) == 100   # exact preferred time
    assert score_departure_time(two_hours_late, offers, None, PROFILE) == 80  # 2 h × 10 points penalty
    
def test_departure_score_never_below_zero():   
    """Departure time score should never go below 0, even if the offer is very late."""
    very_late = make_offer(offer_id=1,
                           departure=datetime(2026, 7, 12, 23, 0),
                           arrival=datetime(2026, 7, 13, 6, 0))
    offers = [very_late]
    
    assert score_departure_time(very_late, offers, None, PROFILE) == 0  

def test_flexibility_categories():   
    """Flexibility score is 100 for changeable and refundable, 50 for one of them, 0 for neither."""
    flexible = make_offer(offer_id=1, fare_conditions=FareConditions(changeable=True, refundable=True, baggage_limit=20))
    inflexible = make_offer(offer_id=2, fare_conditions=FareConditions(changeable=False, refundable=False, baggage_limit=20))
    partial = make_offer(offer_id=3, fare_conditions=FareConditions(changeable=True, refundable=False, baggage_limit=20))
    offers = [flexible, inflexible, partial]
    
    assert score_flexibility(flexible, offers, None, PROFILE) == 100
    assert score_flexibility(inflexible, offers, None, PROFILE) == 0
    assert score_flexibility(partial, offers, None, PROFILE) == 50
    
def test_weights_missing_criteria_rejected():  
    """If the traveller profile is missing weights for any of the criteria, ranking raises a ValueError."""
    bad_profile = TravellerProfile(
        "Bad weights",
        time(9, 0),
        {"price": 0.5, "duration": 0.5},  
    )
    
    offer1 = make_offer(offer_id=1, price=20.0)
    offer2 = make_offer(offer_id=2, price=40.0)
    
    offers = [offer1, offer2]
    with pytest.raises(ValueError):
        rank_offers(offers, None, bad_profile)

def test_shorter_journey_ranks_higher(): 
    """Among offers with equal price, the shorter journey ranks higher."""
    offer1 = make_offer(offer_id=1, price=20.0, departure=datetime(2026, 7, 12, 8, 0), arrival=datetime(2026, 7, 12, 15, 0))  
    offer2 = make_offer(offer_id=2, price=20.0, departure=datetime(2026, 7, 12, 10, 0), arrival=datetime(2026, 7, 12, 15, 0))  
    offers = [offer1, offer2]
    
    ranked = rank_offers(offers, None, PROFILE)
    
    assert ranked[0][0] == offer2  
    assert ranked[1][0] == offer1 

def test_tie_broken_by_lower_offer_id():
    """If two offers have the same total score, the one with the lower offer_id ranks higher."""
    first = make_offer(offer_id=1)
    second = make_offer(offer_id=2)

    ranked = rank_offers([second, first], None, PROFILE)

    assert ranked[0][1] == ranked[1][1]                 # totals really are equal
    assert [r[0].offer_id for r in ranked] == [1, 2]    # lower ID wins the tie  