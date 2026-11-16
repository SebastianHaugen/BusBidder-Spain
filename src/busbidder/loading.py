"""
Load and validate BusBidder data files.

Reads companies, destinations and traveller profiles from JSON and offers
from CSV, converting each record into model objects. Invalid records are
rejected individually and logged with the reason. A missing or unreadable
data file raises DataValidationError.
"""

import csv
import json
import logging
from datetime import datetime, time
from pathlib import Path

from busbidder.exceptions import DataValidationError
from busbidder.models import Company, FareConditions, Offer, TravellerProfile

COMPANY_DATA_FILE = Path("data/companies.json")
OFFER_DATA_FILE = Path("data/offers.csv")
PROFILE_DATA_FILE = Path("config/profiles.json")
DESTINATION_DATA_FILE = Path("data/destinations.json")

RATING_MIN = 0.0
RATING_MAX = 5.0

logger = logging.getLogger(__name__)

# Helper function to read JSON files and validate their structure
def _read_json_file(path: Path) -> list[dict]:
    """Read a JSON file whose top level is a list, raising DataValidationError on failure."""
    if not path.exists():
        logger.error(f"Data file {path} does not exist.")
        raise DataValidationError(f"Data file {path} does not exist.")

    try:
        with open(path, "r", encoding="utf-8") as f:
            data = json.load(f)
    except json.JSONDecodeError as e:
        logger.error(f"Error decoding JSON from {path}: {e}")
        raise DataValidationError(f"Invalid JSON in {path}: {e}") from e

    if not isinstance(data, list):
        logger.error(f"Expected a list in {path}, got {type(data).__name__}")
        raise DataValidationError(f"Expected a list in {path}, got {type(data).__name__}")

    return data

def load_companies(path: Path = COMPANY_DATA_FILE) -> dict[str, Company]:
    """
    Load company data from a JSON file.

    Each record must contain name, profile_desc and rating. Records with
    missing fields, invalid ratings or duplicate names are rejected.

    Returns:
        A dict mapping company name to Company object.
    """
    companies: dict[str, Company] = {}
    data = _read_json_file(path)

    for record in data:
        try:
            name = record["name"]
            profile_desc = record["profile_desc"]
            rating = float(record["rating"])

            if not (RATING_MIN <= rating <= RATING_MAX):
                raise DataValidationError(f"rating {rating} outside {RATING_MIN}-{RATING_MAX}")
            if name in companies:
                raise DataValidationError(f"duplicate company name {name!r}")

            companies[name] = Company(name, profile_desc, rating)

        except KeyError as e:
            logger.error(f"Rejected company record, missing field {e}: {record}")
        except (ValueError, TypeError) as e:
            logger.error(f"Rejected company record ({e}): {record}")

    logger.info(f"Loaded {len(companies)} companies from {path}.")
    return companies


def load_offers(companies: dict[str, Company], destinations: set[str],
                path: Path = OFFER_DATA_FILE) -> list[Offer]:
    """
    Load offer data from a CSV file.

    Records with missing fields, invalid values, unknown companies or
    destinations, or duplicate IDs are rejected.

    Returns:
        A list of valid Offer objects.
    """
    if not path.exists():
        logger.error(f"Data file {path} does not exist.")
        raise DataValidationError(f"Data file {path} does not exist.")

    offers: list[Offer] = []
    seen_ids: set[int] = set()

    with open(path, "r", encoding="utf-8", newline="") as f:
        reader = csv.DictReader(f)

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
                    baggage_limit=int(record["baggage_limit"]),
                )

                if company_name not in companies:
                    raise DataValidationError(f"company {company_name!r} not found")
                if price <= 0:
                    raise DataValidationError(f"price {price} must be positive")
                if arrival <= departure:
                    raise DataValidationError(f"arrival {arrival} must be after departure {departure}")
                if seats_available < 0:
                    raise DataValidationError(f"seats_available {seats_available} cannot be negative")
                if transfers < 0:
                    raise DataValidationError(f"transfers {transfers} cannot be negative")
                if offer_id in seen_ids:
                    raise DataValidationError(f"duplicate offer_id {offer_id}")
                if destination not in destinations:
                    raise DataValidationError(f"unknown destination {destination!r}")

                offer = Offer(
                    offer_id, companies[company_name], price, departure, arrival,
                    destination, transfers, seats_available, fare_conditions,
                )

                seen_ids.add(offer_id)
                offers.append(offer)

            except KeyError as e:
                logger.error(f"Rejected offer record, missing field {e}: {record}")
            except (ValueError, TypeError, AttributeError) as e:
                logger.error(f"Rejected offer record ({e}): {record}")

    logger.info(f"Loaded {len(offers)} offers from {path}.")
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
    data = _read_json_file(path)

    for record in data:
        try:
            name = record["name"]
            preferred = time.fromisoformat(record["preferred_departure"])
            weights = {k: float(v) for k, v in record["weights"].items()}

            if name in profiles:
                raise DataValidationError(f"duplicate profile name {name!r}")

            profiles[name] = TravellerProfile(name, preferred, weights)

        except KeyError as e:
            logger.error(f"Rejected profile record, missing field {e}: {record}")
        except (ValueError, TypeError, AttributeError) as e:
            logger.error(f"Rejected profile record ({e}): {record}")

    logger.info(f"Loaded {len(profiles)} traveller profiles from {path}.")
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
    data = _read_json_file(path)

    for record in data:
        try:
            name = record["city"].strip()

            if not name:
                raise DataValidationError("empty destination name")
            if name in destinations:
                raise DataValidationError(f"duplicate destination name {name!r}")

            destinations.add(name)

        except KeyError as e:
            logger.error(f"Rejected destination record, missing field {e}: {record}")
        except (ValueError, TypeError, AttributeError) as e:
            logger.error(f"Rejected destination record ({e}): {record}")

    logger.info(f"Loaded {len(destinations)} destinations from {path}.")
    return destinations