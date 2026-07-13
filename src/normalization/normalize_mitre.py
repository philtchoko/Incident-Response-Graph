"""
Normalize MITRE ATT&CK technique values.
*For future enterprise data integration*
"""

import pandas as pd


def normalize_mitre_id(value):
    """
    Normalize MITRE ATT&CK technique IDs.

    Examples:
    - t1059 -> T1059
    - T1059.001 -> T1059.001
    """
    if pd.isna(value):
        return None

    return str(value).strip().upper()


def normalize_mitre_name(value):
    """
    Normalize MITRE technique names.
    """
    if pd.isna(value):
        return None

    return str(value).strip()