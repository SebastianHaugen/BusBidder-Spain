"""
Load and validate BusBidder data files.

Reads company data from JSON and offer data from CSV, creating Company and
Offer objects and validating their contents. Invalid records are rejected
and logged with the reason they failed.
"""

import json
import csv
from datetime import datetime, time 
from pathlib import Path

from busbidder.models import Company, Offer, FareConditions, TravellerProfile

COMPANY_DATA_FILE = Path("data/companies.json")
OFFER_DATA_FILE = Path("data/offers.csv")
PROFILE_DATA_FILE = Path("config/profiles.json")
DESTINATION_DATA_FILE = Path("data/destinations.json")

RATING_MIN = 0.0
RATING_MAX = 5.0

def load_companies(path: Path = COMPANY_DATA_FILE) -> dict[str, Company]:
    """
    Load company data from a JSON file.

    Each record must contain name, profile_desc and rating. Records with
    missing fields, invalid ratings or duplicate names are rejected.

    Args:
        path: Path to the JSON file containing company data.

    Returns:
        A dict mapping company name to Company object.
    """
    companies: dict[str, Company] = {}

    with open(path, "r", encoding="utf-8") as f:
        data = json.load(f)

    for record in data:
        try:
            name = record["name"]
            profile_desc = record["profile_desc"]
            rating = float(record["rating"])

            if not (RATING_MIN <= rating <= RATING_MAX):
                raise ValueError(
                    f"rating {rating} outside {RATING_MIN}-{RATING_MAX}"
                )
            if name in companies:
                raise ValueError(f"duplicate company name {name!r}")

            companies[name] = Company(name, profile_desc, rating)

        except KeyError as e:
            print(f"Rejected company record, missing field {e}: {record}")
        except (ValueError, TypeError) as e:
            print(f"Rejected company record ({e}): {record}")

    return companies

def load_offers(companies: dict[str, Company], destinations: set[str],  path: Path = OFFER_DATA_FILE) -> list[Offer]:
    """
    Load offer data from a CSV file.
    """
    
    with open(path, "r", encoding="utf-8", newline="") as f:
        reader = csv.DictReader(f)
        
        offers: list[Offer] = []
        seen_ids: set[int] = set()
                
        for record in reader:
            try:
                offer_id = int(record["offer_id"])
                company_name = record["company"]
                price = float(record["price"])
                departure = datetime.fromisoformat(record["departure"])
                arrival = datetime.fromisoformat(record["arrival"])
                destination = record["destination"]
                transfers = int(record["transfers"])
                seats_available = int(record["seats_available"])
                
                fare_conditions = FareConditions(
                    changeable=record["changeable"].lower() == "true",
                    refundable=record["refundable"].lower() == "true",
                    baggage_limit=int(record["baggage_limit"])
                )
                
                if company_name not in companies:
                    raise ValueError(f"company {company_name!r} not found")
                
                if price <= 0:
                    raise ValueError(f"price {price} must be positive")
                
                if arrival <= departure:
                    raise ValueError(f"arrival {arrival} must be after departure {departure}")
                
                if seats_available < 0:
                    raise ValueError(f"seats_available {seats_available} cannot be negative")
                
                if transfers < 0:
                    raise ValueError(f"transfers {transfers} cannot be negative")
                
                if offer_id in seen_ids:
                    raise ValueError(f"duplicate offer_id {offer_id}")
                
                if destination not in destinations:
                    raise ValueError(f"unknown destination {destination!r}")
                                                
                company = companies[company_name]
                
                offer = Offer(
                    offer_id, company, price, departure, arrival,
                    destination, transfers, seats_available, fare_conditions
                )
                
                seen_ids.add(offer_id)
                offers.append(offer)
            
            except KeyError as e:
                print(f"Rejected offer record, missing field {e}: {record}")
            except (ValueError, TypeError) as e:
                print(f"Rejected offer record ({e}): {record}")
        
        return offers

def load_profiles(path: Path = PROFILE_DATA_FILE) -> dict[str, TravellerProfile]:
    """
    Load traveller profiles from a JSON file.

    Each record must contain name, preferred_departure ("HH:MM") and weights.
    Weight validation is done by TravellerProfile itself.

    Returns:
        A dict mapping profile name to TravellerProfile object.
    """
    profiles: dict[str, TravellerProfile] = {}

    with open(path, "r", encoding="utf-8") as f:
        data = json.load(f)

    for record in data:
        try:
            name = record["name"]
            preferred = time.fromisoformat(record["preferred_departure"])
            weights = {k: float(v) for k, v in record["weights"].items()}

            if name in profiles:
                raise ValueError(f"duplicate profile name {name!r}")

            profiles[name] = TravellerProfile(name, preferred, weights)

        except KeyError as e:
            print(f"Rejected profile record, missing field {e}: {record}")
        except (ValueError, TypeError, AttributeError) as e:
            print(f"Rejected profile record ({e}): {record}")

    return profiles

def load_destinations(path: Path = DESTINATION_DATA_FILE) -> set[str]:
    """
    Load destination names from a JSON file.

    Each record must contain a city name. Records with a missing or empty
    name, or a duplicate name, are rejected.

    Returns:
        A set of valid destination names.
    """
    destinations: set[str] = set()
    
    with open(path, "r", encoding="utf-8") as f:
        data = json.load(f)
        
    for destination in data:
        try:
            name = destination["city"].strip()
                
            if not name:
                raise ValueError("empty destination name")

            if name in destinations:
                raise ValueError(f"duplicate destination name {name!r}")

            destinations.add(name)
                
        except KeyError as e:
            print(f"Rejected destination record, missing field {e}: {destination}")
        except (ValueError, TypeError) as e:
            print(f"Rejected destination record ({e}): {destination}")
        
    return destinations