"""
Tests for the loading module.
"""

import pytest

from busbidder.exceptions import DataValidationError
from busbidder.loading import load_offers, load_companies
from busbidder.models import Company

def test_valid_offers_load(tmp_path): 
    """Two valid offers are loaded correctly from a CSV file."""
    csv_content = """offer_id,company,destination,departure,arrival,price,transfers,seats_available,changeable,refundable,baggage_limit
1,CostaLink,Malaga,2026-07-13T10:00,2026-07-13T17:00,38.00,1,12,true,false,23
2,SolRuta,Malaga,2026-07-12T09:00,2026-07-12T15:00,30.00,0,10,true,false,20"""

    csv_file = tmp_path / "offers.csv"
    csv_file.write_text(csv_content)
    
    temp_companies = {
        "CostaLink": Company("CostaLink", "costa", 4.5),
        "SolRuta": Company("SolRuta", "sol", 4.0),
    }
    
    temp_destinations = {"Malaga", "Barcelona", "Madrid"}
    
    offers = load_offers(temp_companies, temp_destinations, path=csv_file)
    
    assert len(offers) == 2
    
def test_negative_price_rejected(tmp_path):
    """An offer with a negative price is rejected, the valid offer is kept."""
    csv_content = """offer_id,company,destination,departure,arrival,price,transfers,seats_available,changeable,refundable,baggage_limit
1,CostaLink,Malaga,2026-07-13T10:00,2026-07-13T17:00,38.00,1,12,true,false,23
2,CostaLink,Malaga,2026-07-13T12:00,2026-07-13T18:00,-38.00,1,12,true,false,23"""


    csv_file = tmp_path / "offers.csv"
    csv_file.write_text(csv_content)
    
    temp_companies = {
        "CostaLink": Company("CostaLink", "costa", 4.5),
    }
    
    temp_destinations = {"Malaga", "Barcelona", "Madrid"}
    
    offers = load_offers(temp_companies, temp_destinations, path=csv_file)
    
    assert len(offers) == 1
    assert offers[0].offer_id == 1

def test_unknown_destination_rejected(tmp_path): 
    """An offer with an unknown destination is rejected, the valid offer is kept."""
    csv_content = """offer_id,company,destination,departure,arrival,price,transfers,seats_available,changeable,refundable,baggage_limit
1,CostaLink,Malaga,2026-07-13T10:00,2026-07-13T17:00,38.00,1,12,true,false,23
2,CostaLink,UnknownCity,2026-07-13T12:00,2026-07-13T18:00,38.00,1,12,true,false,23"""

    csv_file = tmp_path / "offers.csv"
    csv_file.write_text(csv_content)
    
    temp_companies = {
        "CostaLink": Company("CostaLink", "costa", 4.5),
        "SolRuta": Company("SolRuta", "sol", 4.0)
    }
    
    temp_destinations = {"Malaga", "Barcelona", "Madrid"}
    
    offers = load_offers(temp_companies, temp_destinations, path=csv_file)
    
    assert len(offers) == 1
    assert offers[0].offer_id == 1
            
def test_missing_field_rejected(tmp_path):
    """Missing data: a row with an empty departure is rejected, the valid row is kept."""
    csv_content = """offer_id,company,destination,departure,arrival,price,transfers,seats_available,changeable,refundable,baggage_limit
1,CostaLink,Malaga,2026-07-13T10:00,2026-07-13T17:00,38.00,1,12,true,false,23
2,CostaLink,Malaga,,2026-07-13T18:00,38.00,1,12,true,false,23"""

    csv_file = tmp_path / "offers.csv"
    csv_file.write_text(csv_content)

    companies = {"CostaLink": Company("CostaLink", "costa", 4.5)}
    destinations = {"Malaga"}

    offers = load_offers(companies, destinations, path=csv_file)

    assert len(offers) == 1
    assert offers[0].offer_id == 1 

def test_missing_file_raises(tmp_path): 
    """Loading from a non-existent file raises DataValidationError."""
    missing_file = tmp_path / "nonexistent_offers.csv"

    with pytest.raises(DataValidationError):
        load_offers({}, set(), path=missing_file)
    
def test_invalid_json_raises(tmp_path):
    """Loading companies from a file with invalid JSON raises DataValidationError."""
    bad_file = tmp_path / "companies.json"
    bad_file.write_text("{invalid json}")
   
    with pytest.raises(DataValidationError):
        load_companies(path=bad_file)