from datetime import datetime

"""
This file creates 2 models, 1 for the company and 1 for the offer
"""
class Company:
    def __init__(self, name, profile_desc, rating):
        self.name = name
        self.profile_desc = profile_desc
        self.rating = rating

    # This method is used to represent the company object as a string
    def __repr__(self):
        return f"Company({self.name!r}, rating={self.rating})"

# This class represents an offer made by a company for a bus trip
class Offer:
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

    # This method is used to calculate the duration of the offer in minutes
    @property
    def duration_minutes(self):
        return int((self.arrival - self.departure).total_seconds() // 60)
    
    # This method is used to represent the offer object as a string
    def __repr__(self):
        return (f"Offer({self.company.name}, €{self.price}, ")
    
class FareConditions:
    def __init__(self, changeable, refundable, baggage_limit):
        self.changeable = changeable
        self.refundable = refundable
        self.baggage_limit = baggage_limit