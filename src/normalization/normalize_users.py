"""
Normalize user identifiers.
*For future enterprise data integration*
"""

import pandas as pd


def normalize_user(value):
    """
    Normalize usernames into lowercase account identifiers.

    Examples:
    - John.Smith@company.com -> john.smith
    - COMPANY\\JSmith -> jsmith
    - JSMITH -> jsmith
    """
    if pd.isna(value):
        return None

    value = str(value).strip().lower()

    # Remove email domain
    if "@" in value:
        value = value.split("@")[0]

    # Remove Windows domain prefix
    if "\\" in value:
        value = value.split("\\")[-1]

    return value