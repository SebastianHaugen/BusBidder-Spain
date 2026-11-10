"""
Registry for scoring functions.

Scores one offer on a 0 - 100 scale.
"""

CRITERIA = {}

def criterion(name):
    """ Register the decorated function as a scoring criterion under 'name' """
    def decorator(func):
        if name in CRITERIA:
            raise ValueError(f"Duplicate scoring criterion name: {name}")
        CRITERIA[name] = func
        return func
    return decorator