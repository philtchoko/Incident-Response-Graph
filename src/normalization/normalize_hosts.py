"""
Normalize host and asset names.
*For future enterprise data integration*
"""

import pandas as pd


def normalize_hostname(value):
    """
    Convert hostnames into a consistent format.

    Examples:
    - fin-laptop-22.company.local -> FIN-LAPTOP-22
    - fin-laptop-22 -> FIN-LAPTOP-22
    - WEB01 -> WEB01
    """
    if pd.isna(value):
        return None

    value = str(value).strip().upper()

    # Remove domain suffix from FQDNs
    if "." in value:
        value = value.split(".")[0]

    # Replace spaces with hyphens
    value = value.replace(" ", "-")

    return value