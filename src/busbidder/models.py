"""
Data models for BusBidder Spain.

Defines three classes: Company (a bus operator), Offer (a single bookable
bus trip offered by a company) and FareConditions (the ticket terms
attached to an offer).
"""

class Company:
    """A bus company operating on the marketplace."""
    def __init__(self, name, profile_desc, rating):
        self.name = name
        self.profile_desc = profile_desc
        self.rating = rating

    def __repr__(self):
        """Return a short readable representation of the company."""
        return f"Company({self.name!r}, rating={self.rating})"

class Offer:
    """A bus trip offered by a company to a destination at a given time and price."""
    def __init__(self, offer_id, company, price, departure, arrival, destination, transfers, seats_available, fare_conditions):
        self.offer_id = offer_id
        self.company = company
        self.price = price
        self.departure = departure
        self.arrival = arrival
        self.destination = destination
        self.transfers = transfers
        self.seats_available = seats_available
        self.fare_conditions = fare_conditions       

    @property
    def duration_minutes(self):
        """Journey duration in minutes, computed from departure and arrival."""
        return int((self.arrival - self.departure).total_seconds() // 60)
    
    def __repr__(self):
        """Return a short readable representation of the offer."""
        return (f"Offer({self.company.name}, €{self.price}, ")
    
class FareConditions:
    """Ticket terms for an offer: changeability, refundability and baggage allowance."""
    def __init__(self, changeable, refundable, baggage_limit):
        self.changeable = changeable
        self.refundable = refundable
        self.baggage_limit = baggage_limit