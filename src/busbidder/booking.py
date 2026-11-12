"""
All logic related to booking an offer.
"""

import string
import random
import re

REFERENCE_PATTERN = re.compile(r"^\d+-\d+-[A-Z0-9]{5}$")

def generate_reference(offer_id: int, seats: int, existing: set[str]) -> str:
    """Generate a unique booking reference based on the offer ID and number of seats."""
    
    while True:
        code = random.choices(string.ascii_uppercase + string.digits, k=5)
        reference = f"{offer_id}-{seats}-" + ''.join(code)
        if reference not in existing:
            return reference
    
def validate_reference(reference: str) -> bool:
    """ 
    Validate the format of a booking refence. It should be in the format OFFERID-SEATS-CODE, 
    where OFFERID and SEATS are integers and CODE is a 5-character alphanumeric string.
    """
    return REFERENCE_PATTERN.fullmatch(reference) is not None
        


