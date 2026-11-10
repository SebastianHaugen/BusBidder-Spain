"""
Scoring criteria for ranking bus offers.

Each criterion scores one offer from 0 to 100, where higher is better.
All criteria share the signature (offer, offers, request, profile) so the
ranker can call them the same way.
"""

from busbidder.scoring.registry import criterion


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