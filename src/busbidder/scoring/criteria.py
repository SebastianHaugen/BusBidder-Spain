"""
Scoring criteria for ranking bus offers.

Each criterion scores one offer from 0 to 100, where higher is better.
All criteria share the signature (offer, offers, request, profile) so the
ranker can call them the same way.
"""

from busbidder.scoring.registry import criterion

PENALTY_PER_HOUR = 10

@criterion("price")
def score_price(offer, offers, request, profile):
    """Min-max score for price: cheapest accepted offer = 100, most expensive = 0."""
    prices = [o.price for o in offers]
    lowest = min(prices)
    highest = max(prices)

    if highest == lowest:
        return 100.0

    return 100 * (highest - offer.price) / (highest - lowest)

@criterion("duration")
def score_duration(offer, offers, request, profile):
    """Min-max score for duration: shortest accepted offer = 100, longest = 0."""
    durations = [o.duration_minutes for o in offers]
    shortest = min(durations)
    longest = max(durations)

    if longest == shortest:
        return 100.0

    return 100 * (longest - offer.duration_minutes) / (longest - shortest)

@criterion("departure_time")
def score_departure_time(offer, offers, request, profile):
    """Fixed penalty score for departure time: 100 at the preferred time, minus PENALTY_PER_HOUR per hour away, minimum 0"""
    preferred_minutes = profile.preferred_departure.hour * 60 + profile.preferred_departure.minute
    offer_minutes = offer.departure.hour * 60 + offer.departure.minute
    gap_hours = abs(offer_minutes - preferred_minutes) / 60
    
    return max(0, 100 - gap_hours * PENALTY_PER_HOUR)  # lose 10 points per hour of difference

@criterion("flexibility")
def score_flexibility(offer, offers, request, profile):
    """Fixed score for flexibility: changeable and refundable = 100, changeable = 50, non-changeable and non refundable = 0."""
    if offer.fare_conditions.changeable and offer.fare_conditions.refundable:
        return 100.0
    elif offer.fare_conditions.changeable or offer.fare_conditions.refundable:
       return 50.0
    else:
        return 0.0
    