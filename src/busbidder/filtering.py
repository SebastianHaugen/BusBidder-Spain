"""
Filtering logic for the travelers hard constraints

Any offer that violate any mandatory constraint are removed before ranking. 
Each rejected offer is returned with the reason it failed, so the user can see why.
"""

from busbidder.models import Offer, TravelRequest

def check_offer(offer: Offer, request: TravelRequest) -> list[str]:
    """ reutrn a list of reasons the offer fails the request. Empty means it passes"""
    reasons = []
    
    if offer.destination != request.destination:
        reasons.append(f"Destination {offer.destination} does not match requested {request.destination}")
    
    if offer.departure.date() < request.earliest_date:
       reasons.append(f"Departure {offer.departure.date()} is before earliest date {request.earliest_date}")

    if offer.departure.date() > request.latest_date:
       reasons.append(f"Departure {offer.departure.date()} is after latest date {request.latest_date}")
        
    if offer.price > request.max_price:
        reasons.append(f"Price {offer.price} exceeds requested max {request.max_price}")
    
    if offer.transfers > request.max_transfers:
        reasons.append(f"Transfers {offer.transfers} exceeds requested max {request.max_transfers}")
    
    if request.requires_changeable and not offer.fare_conditions.changeable:
        reasons.append("Offer is not changeable, but requested changeable")
    
    if offer.seats_available < request.seats_needed:
        reasons.append(f"Offer has {offer.seats_available} seats available, but requested {request.seats_needed}")
    
    return reasons

def filter_offers(offers: list[Offer], request: TravelRequest):
    """ splits offers into accepeted and rejected with the reasons"""
    accepted = []
    rejected = []
    
    for offer in offers:
        reasons =check_offer(offer, request)
        if reasons:
            rejected.append((offer, reasons))
        else:
            accepted.append(offer)
    
    return accepted, rejected