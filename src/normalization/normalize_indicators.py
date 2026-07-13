"""
Normalize indicators of compromise and general values.
*For future enterprise data integration*

"""

import pandas as pd


def normalize_text(value):
    """
    Strip whitespace and convert missing values to None.
    """
    if pd.isna(value):
        return None

    return str(value).strip()


def normalize_lower(value):
    """
    Normalize values that should be lowercase.
    Useful for domains, processes, hashes, and indicators.
    """
    if pd.isna(value):
        return None

    return str(value).strip().lower()


def normalize_bool(value):
    """
    Convert common boolean-like values into True/False.
    """
    if pd.isna(value):
        return False

    if isinstance(value, bool):
        return value

    value = str(value).strip().lower()

    return value in {"true", "yes", "1", "y"}


def normalize_domain(value):
    """
    Normalize URLs/domains into a clean lowercase domain.

    Examples:
    - https://bad-domain.com/login -> bad-domain.com
    - BAD-DOMAIN.COM -> bad-domain.com
    """
    value = normalize_lower(value)

    if not value:
        return None

    for prefix in ["https://", "http://"]:
        if value.startswith(prefix):
            value = value.removeprefix(prefix)

    # Remove path after domain
    value = value.split("/")[0]

    return value


def normalize_hash(value):
    """
    Normalize file hashes.
    """
    return normalize_lower(value)


def normalize_ip(value):
    """
    Normalize IP address text.

    For now, this only strips whitespace.
    IP validation can be added later.
    """
    return normalize_text(value)