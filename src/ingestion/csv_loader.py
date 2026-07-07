"""
csv_loader.py

Loads and normalizes raw CSV files for the Incident Knowledge Graph MVP.
"""

from pathlib import Path
import pandas as pd


REQUIRED_FILES = {
    "assets": "assets.csv",
    "incidents": "incidents.csv",
    "alerts": "alerts.csv",
    "vulnerabilities": "vulnerabilities.csv",
    "threat_intel": "threat_intel.csv",
    "mitre_mapping": "mitre_mapping.csv",
}


def clean_columns(df: pd.DataFrame) -> pd.DataFrame:
    """
    Standardize column names.

    Example:
    'Host Name' -> 'host_name'
    """
    df = df.copy()
    df.columns = (
        df.columns
        .str.strip()
        .str.lower()
        .str.replace(" ", "_", regex=False)
    )
    return df


def normalize_hostname(value):
    """
    Normalize hostnames into a consistent uppercase format.

    Example:
    'fin-laptop-40.company.local' -> 'FIN-LAPTOP-40'
    """
    if pd.isna(value):
        return None

    value = str(value).strip().upper()

    if "." in value:
        value = value.split(".")[0]

    return value


def normalize_text(value):
    """
    Normalize general text fields by stripping extra whitespace.
    """
    if pd.isna(value):
        return None

    return str(value).strip()


def normalize_lower(value):
    """
    Normalize values that should be lowercase, such as domains,
    processes, hashes, and indicators.
    """
    if pd.isna(value):
        return None

    return str(value).strip().lower()


def normalize_bool(value):
    """
    Normalize boolean-like values into True/False.
    """
    if pd.isna(value):
        return False

    if isinstance(value, bool):
        return value

    value = str(value).strip().lower()

    return value in {"true", "yes", "1", "y"}


def normalize_assets(df: pd.DataFrame) -> pd.DataFrame:
    df = clean_columns(df)
    require_columns(
        df,
        {
            "asset_id",
            "hostname",
            "department",
            "asset_type",
            "criticality",
            "internet_facing",
            "operating_system",
            "owner",
        },
        "assets",
    )
    df["asset_id"] = df["asset_id"].apply(normalize_text)
    df["hostname"] = df["hostname"].apply(normalize_hostname)
    df["department"] = df["department"].apply(normalize_text)
    df["asset_type"] = df["asset_type"].apply(normalize_text)
    df["criticality"] = df["criticality"].apply(normalize_text)
    df["internet_facing"] = df["internet_facing"].apply(normalize_bool)
    df["operating_system"] = df["operating_system"].apply(normalize_text)
    df["owner"] = df["owner"].apply(normalize_text)
    


    return df.drop_duplicates()


def normalize_incidents(df: pd.DataFrame) -> pd.DataFrame:
    df = clean_columns(df)

    df["incident_id"] = df["incident_id"].apply(normalize_text)
    df["title"] = df["title"].apply(normalize_text)
    df["severity"] = df["severity"].apply(normalize_text)
    df["status"] = df["status"].apply(normalize_text)
    df["asset_id"] = df["asset_id"].apply(normalize_text)
    df["hostname"] = df["hostname"].apply(normalize_hostname)
    df["summary"] = df["summary"].apply(normalize_text)

    df["created_at"] = pd.to_datetime(df["created_at"], errors="coerce")

    return df


def normalize_alerts(df: pd.DataFrame) -> pd.DataFrame:
    df = clean_columns(df)

    df["alert_id"] = df["alert_id"].apply(normalize_text)
    df["incident_id"] = df["incident_id"].apply(normalize_text)
    df["asset_id"] = df["asset_id"].apply(normalize_text)
    df["hostname"] = df["hostname"].apply(normalize_hostname)
    df["alert_name"] = df["alert_name"].apply(normalize_text)
    df["source"] = df["source"].apply(normalize_text)
    df["severity"] = df["severity"].apply(normalize_text)
    df["process"] = df["process"].apply(normalize_lower)
    df["ip"] = df["ip"].apply(normalize_text)
    df["domain"] = df["domain"].apply(normalize_lower)
    df["file_hash"] = df["file_hash"].apply(normalize_lower)
    df["mitre_id"] = df["mitre_id"].apply(
    lambda x: normalize_text(x).upper() if normalize_text(x) else None)

    df["timestamp"] = pd.to_datetime(df["timestamp"], errors="coerce")

    return df


def normalize_vulnerabilities(df: pd.DataFrame) -> pd.DataFrame:
    df = clean_columns(df)

    df["asset_id"] = df["asset_id"].apply(normalize_text)
    df["hostname"] = df["hostname"].apply(normalize_hostname)
    df["cve_id"] = df["cve_id"].apply(normalize_text)
    df["severity"] = df["severity"].apply(normalize_text)
    df["kev_status"] = df["kev_status"].apply(normalize_bool)
    df["description"] = df["description"].apply(normalize_text)

    df["cvss_score"] = pd.to_numeric(df["cvss_score"], errors="coerce")

    return df


def normalize_threat_intel(df: pd.DataFrame) -> pd.DataFrame:
    df = clean_columns(df)

    df["indicator"] = df["indicator"].apply(normalize_lower)
    df["indicator_type"] = df["indicator_type"].apply(normalize_lower)
    df["reputation"] = df["reputation"].apply(normalize_text)
    df["confidence"] = df["confidence"].apply(normalize_text)
    df["source"] = df["source"].apply(normalize_text)
    df["malware_family"] = df["malware_family"].apply(normalize_text)

    return df


def normalize_mitre_mapping(df: pd.DataFrame) -> pd.DataFrame:
    df = clean_columns(df)

    df["observable"] = df["observable"].apply(normalize_lower)
    df["technique_id"] = df["technique_id"].apply(
    lambda x: normalize_text(x).upper() if normalize_text(x) else None)
    df["technique_name"] = df["technique_name"].apply(normalize_text)
    df["tactic"] = df["tactic"].apply(normalize_text)
    

    return df


def load_raw_csvs(data_dir: Path) -> dict[str, pd.DataFrame]:
    """
    Load all required raw CSV files from data/raw.
    """
    datasets = {}

    for name, filename in REQUIRED_FILES.items():
        path = data_dir / filename

        if not path.exists():
            raise FileNotFoundError(f"Missing required file: {path}")

        datasets[name] = pd.read_csv(path)

    return datasets


def normalize_datasets(raw: dict[str, pd.DataFrame]) -> dict[str, pd.DataFrame]:
    """
    Normalize all loaded datasets.
    """
    return {
        "assets": normalize_assets(raw["assets"]),
        "incidents": normalize_incidents(raw["incidents"]),
        "alerts": normalize_alerts(raw["alerts"]),
        "vulnerabilities": normalize_vulnerabilities(raw["vulnerabilities"]),
        "threat_intel": normalize_threat_intel(raw["threat_intel"]),
        "mitre_mapping": normalize_mitre_mapping(raw["mitre_mapping"]),
    }


def load_and_normalize(data_dir: Path) -> dict[str, pd.DataFrame]:
    """
    Main function used by the pipeline.

    Loads raw CSVs and returns normalized DataFrames.
    """
    raw = load_raw_csvs(data_dir)
    return normalize_datasets(raw)


def require_columns(df: pd.DataFrame, required: set[str], dataset_name: str) -> None:
    missing = required - set(df.columns)

    if missing:
        raise ValueError(
            f"{dataset_name} is missing required columns: {sorted(missing)}"
        )