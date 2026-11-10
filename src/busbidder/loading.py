"""
Load and validate BusBidder data files.

Reads company data from JSON and offer data from CSV, creating Company and
Offer objects and validating their contents. Invalid records are rejected
and logged with the reason they failed.
"""

import json
from pathlib import Path

from busbidder.models import Company, Offer, FareConditions

COMPANY_DATA_FILE = Path("data/companies.json")
OFFER_DATA_FILE = Path("data/offers.csv")

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