"""
Custom exceptions for the BusBidder application.
"""

class BusBidderError(Exception):
    """Base class for all BusBidder exceptions."""

class DataValidationError(BusBidderError, ValueError):
    """A data record has missing, invalid or inconsistent fields."""    

class BookingError(BusBidderError):
    """An error occurred during the booking process."""