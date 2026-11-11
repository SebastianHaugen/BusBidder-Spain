"""
Weighted ranking of filtered offers.

Combines the registered scoring criteria into one total per offer,
using the weights from the traveller's profile.
"""

import busbidder.scoring.criteria # I need this for registering the criteria functions
from busbidder.scoring.registry import CRITERIA

def rank_offers(offers, request, profile):
    """
    Rank offers using a weighted sum of criterion scores.

    Each registered criterion scores an offer from 0 to 100, where higher
    is better. The total is the sum of each score multiplied by its weight
    in the traveller profile. Weights sum to 1.0, so totals are also 0-100.

    Args:
        offers: Offer objects that passed filtering.
        request: TravelRequest with the traveller's hard constraints.
        profile: TravellerProfile with the preferred departure time and weights.

    Returns:
        List of (offer, total, scores) tuples, highest total first, where
        scores maps each criterion name to its 0-100 score.
        Ties are broken by offer ID.
        
    Raises:
        RuntimeError: If no criteria are registered.
        ValueError: If the profile weights don't match the registered criteria.
    """
    
    if not CRITERIA:
        raise RuntimeError("No scoring criteria registered. Did you import busbidder.scoring.criteria?")
    
    if set(profile.weights) != set(CRITERIA):
        raise ValueError("Profile weights do not match registered criteria.")

    scored_offers = []
        
    for offer in offers:
        scores = {name: func(offer, offers, request, profile)
            for name, func in CRITERIA.items()}
        total = sum(profile.weights[name] * scores[name] for name in scores)
        scored_offers.append((offer, total, scores))
        

    return sorted(scored_offers, key=lambda x: (-x[1], x[0].offer_id))