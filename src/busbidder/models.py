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
    def __init__(self, company, price, departure, arrival):
        self.company = company
        self.price = price
        self.departure = departure
        self.arrival = arrival

    # This method is used to calculate the duration of the offer in minutes
    @property
    def duration_minutes(self):
        return int((self.arrival - self.departure).total_seconds() // 60)
    
    # This method is used to represent the offer object as a string
    def __repr__(self):
        return (f"Offer({self.company.name}, €{self.price}, ")