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
        return (f"Offer({self.offer_id}, {self.company.name}, €{self.price}, "
                f"{self.departure:%Y-%m-%d %H:%M})")
    
class FareConditions:
    """Ticket terms for an offer: changeability, refundability and baggage allowance."""
    def __init__(self, changeable, refundable, baggage_limit):
        self.changeable = changeable
        self.refundable = refundable
        self.baggage_limit = baggage_limit
        
class TravelRequest:
    """Hard constraints for a trip from Madrid, used to filter offers."""
    def __init__(self, destination, earliest_date, latest_date, max_price, max_transfers, requires_changeable, seats_needed=1):
        self.destination = destination
        self.earliest_date = earliest_date
        self.latest_date = latest_date
        self.max_price = max_price
        self.max_transfers = max_transfers
        self.requires_changeable = requires_changeable
        self.seats_needed = seats_needed
        
        if latest_date < earliest_date:
            raise ValueError("latest_date cannot be earlier than earliest_date")
        
        if max_price <= 0:
            raise ValueError("max_price must be positive")
        
        if max_transfers < 0:
            raise ValueError("max_transfers cannot be negative")
        
        if seats_needed <= 0:
            raise ValueError("seats_needed must be positive")
        
        if not isinstance(requires_changeable, bool):
            raise TypeError("requires_changeable must be a boolean")