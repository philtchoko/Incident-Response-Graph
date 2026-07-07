"""
extract_entities.py

Creates canonical entity records from normalized datasets.
"""

import pandas as pd


def make_entity(entity_id: str, entity_type: str, value: str, source: str) -> dict:
    """
    Create one standardized entity record.
    """
    return {
        "entity_id": entity_id,
        "entity_type": entity_type,
        "value": value,
        "source": source,
    }


def extract_entities(datasets: dict[str, pd.DataFrame]) -> pd.DataFrame:
    """
    Extract unique graph entities from all normalized datasets.

    Returns a DataFrame with:
    - entity_id
    - entity_type
    - value
    - source
    """

    entities = []

    # Assets
    for _, row in datasets["assets"].iterrows():
        entities.append(
            make_entity(
                entity_id=f"asset:{row['asset_id']}",
                entity_type="Asset",
                value=row["hostname"],
                source="assets",
            )
        )

    # Incidents
    for _, row in datasets["incidents"].iterrows():
        entities.append(
            make_entity(
                entity_id=f"incident:{row['incident_id']}",
                entity_type="Incident",
                value=row["title"],
                source="incidents",
            )
        )

    # Alerts
    for _, row in datasets["alerts"].iterrows():
        entities.append(
            make_entity(
                entity_id=f"alert:{row['alert_id']}",
                entity_type="Alert",
                value=row["alert_name"],
                source="alerts",
            )
        )

        if pd.notna(row.get("process")):
            entities.append(
                make_entity(
                    entity_id=f"process:{row['process']}",
                    entity_type="Process",
                    value=row["process"],
                    source="alerts",
                )
            )

        if pd.notna(row.get("ip")):
            entities.append(
                make_entity(
                    entity_id=f"ip:{row['ip']}",
                    entity_type="IP",
                    value=row["ip"],
                    source="alerts",
                )
            )

        if pd.notna(row.get("domain")):
            entities.append(
                make_entity(
                    entity_id=f"domain:{row['domain']}",
                    entity_type="Domain",
                    value=row["domain"],
                    source="alerts",
                )
            )

        if pd.notna(row.get("file_hash")):
            entities.append(
                make_entity(
                    entity_id=f"hash:{row['file_hash']}",
                    entity_type="Hash",
                    value=row["file_hash"],
                    source="alerts",
                )
            )

        if pd.notna(row.get("mitre_id")):
            entities.append(
                make_entity(
                    entity_id=f"mitre:{row['mitre_id']}",
                    entity_type="MITRETechnique",
                    value=row["mitre_id"],
                    source="alerts",
                )
            )

    # Vulnerabilities / CVEs
    for _, row in datasets["vulnerabilities"].iterrows():
        entities.append(
            make_entity(
                entity_id=f"cve:{row['cve_id']}",
                entity_type="CVE",
                value=row["cve_id"],
                source="vulnerabilities",
            )
        )

    # Threat intelligence indicators
    for _, row in datasets["threat_intel"].iterrows():
        entities.append(
            make_entity(
                entity_id=f"indicator:{row['indicator']}",
                entity_type="ThreatIndicator",
                value=row["indicator"],
                source="threat_intel",
            )
        )

    # MITRE mapping table
    for _, row in datasets["mitre_mapping"].iterrows():
        entities.append(
            make_entity(
                entity_id=f"mitre:{row['technique_id']}",
                entity_type="MITRETechnique",
                value=row["technique_name"],
                source="mitre_mapping",
            )
        )

    entity_df = pd.DataFrame(entities)

    entity_df = (
        entity_df
        .dropna(subset=["entity_id", "value"])
        .drop_duplicates(subset=["entity_id"])
        .sort_values(["entity_type", "entity_id"])
        .reset_index(drop=True)
    )

    return entity_df