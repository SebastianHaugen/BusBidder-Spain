"""
Generate test data for the BusBidder application.
"""

import csv
from datetime import datetime, timedelta
import random

# For reproducibility of random data generation
random.seed(42)  

# Company-specific rules for generating offers
COMPANY_RULES = {
    "SolRuta": {                       
        "departure_hours": range(7, 17),
        "duration_factor": 1.05,      
        "price_factor": 0.75,         
        "transfer_choices": [0, 0, 1],
        "changeable_prob": 0.3,
        "refundable_prob": 0.05,
        "baggage_kg": 15,
        "seats_range": (20, 40),
    },
    "Camino Express": {               
        "departure_hours": range(6, 12),
        "duration_factor": 0.85,      
        "price_factor": 1.35,          
        "transfer_choices": [0],
        "changeable_prob": 0.9,
        "refundable_prob": 0.6,
        "baggage_kg": 25,
        "seats_range": (8, 20),
    },
    "CostaLink": {                    
        "departure_hours": range(8, 19),
        "duration_factor": 1.1,        
        "price_factor": 0.95,
        "transfer_choices": [0, 1, 1],
        "changeable_prob": 0.7,
        "refundable_prob": 0.3,
        "baggage_kg": 23,
        "seats_range": (15, 30),
    },
    "VerdeBus": {                      
        "departure_hours": range(7, 19),
        "duration_factor": 1.0,
        "price_factor": 1.15,
        "transfer_choices": [0, 0, 1],
        "changeable_prob": 0.85,
        "refundable_prob": 0.7,
        "baggage_kg": 30,
        "seats_range": (10, 25),
    },
    "NocheVia": {                      
        "departure_hours": range(21, 24),
        "duration_factor": 1.25,       
        "price_factor": 0.7,          
        "transfer_choices": [0, 0, 1],
        "changeable_prob": 0.5,
        "refundable_prob": 0.1,
        "baggage_kg": 20,
        "seats_range": (20, 40),
    },
}

# Destinations and their approximate travel times in hours from Madrid
DESTINATION_HOURS = {
    "Toledo": 1.0, "Salamanca": 2.75, "Zaragoza": 3.5, "Cordoba": 4.5,
    "Valencia": 4.25, "Murcia": 5.0, "Bilbao": 4.75, "Granada": 5.0,
    "Alicante": 5.25, "Seville": 6.0, "San Sebastian": 5.75, "Malaga": 6.0,
    "Barcelona": 7.5, "Cadiz": 7.5, "Santiago de Compostela": 8.0,
}

# Destinations considered coastal for discount purposes
COASTAL = {"Malaga", "Alicante", "Cadiz", "Valencia", "Barcelona", "San Sebastian", "Murcia"}

# Constants for generation
COASTAL_DISCOUNT = 0.85   
PRICE_PER_HOUR = 7.0  
BASE_FARE = 8

# Function to generate a single offer based on the company and destination rules
def generate_offer(offer_id, company_name, destination, departure_date):
    """Generate a realistic bus offer based on company rules and destination."""
    rules = COMPANY_RULES[company_name]
    
    # Randomly select a departure hour within the company's allowed range
    departure_hour = random.choice(rules["departure_hours"])
    departure_time = departure_date.replace(hour=departure_hour, minute=0)
    
    # Calculate base duration and apply company-specific factor
    base_duration = DESTINATION_HOURS[destination] * COMPANY_RULES[company_name]["duration_factor"] * random.uniform(0.95, 1.05)
    
    # Calculate price with company-specific factor and coastal discount if applicable
    price = (BASE_FARE + base_duration * PRICE_PER_HOUR) * rules["price_factor"]
    if destination in COASTAL and company_name == "CostaLink":
        price *= COASTAL_DISCOUNT
    
    # Randomly determine number of transfers, seats available, and fare conditions
    transfers = random.choice(rules["transfer_choices"])
    seats_available = random.randint(*rules["seats_range"])
    changeable = random.random() < rules["changeable_prob"]
    refundable = random.random() < rules["refundable_prob"]
    arrival_time = departure_time + timedelta(minutes=round(base_duration * 60))
    
    ## Return one row of CSV data as a dictionary
    return {
        "offer_id": offer_id,
        "company": company_name,
        "destination": destination,
        "departure": departure_time.isoformat(),
        "arrival": arrival_time.isoformat(),
        "price": round(price, 2),
        "transfers": transfers,
        "seats_available": seats_available,
        "changeable": str(changeable).lower(),
        "refundable": str(refundable).lower(),
        "baggage_limit": rules["baggage_kg"],
    }

OUTPUT_FILE = "data/offers_full.csv"
FIELDNAMES = [
    "offer_id", "company", "destination", "departure", "arrival", "price",
    "transfers", "seats_available", "changeable", "refundable", "baggage_limit",
]

def main():
    """Generate one offer per company, destination and day (12-14 July 2026)."""
    offer_id = 1

    with open(OUTPUT_FILE, "w", encoding="utf-8", newline="") as f:
        writer = csv.DictWriter(f, fieldnames=FIELDNAMES)
        writer.writeheader()

        for company_name in COMPANY_RULES:
            for destination in DESTINATION_HOURS:
                for day in (12, 13, 14):
                    departure_date = datetime(2026, 7, day)
                    writer.writerow(generate_offer(offer_id, company_name, destination, departure_date))
                    offer_id += 1

    print(f"Wrote {offer_id - 1} offers to {OUTPUT_FILE}")


if __name__ == "__main__":
    main()