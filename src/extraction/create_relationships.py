"""
create_relationships.py

Creates graph relationships between canonical entities.
"""

import pandas as pd


def make_relationship(source: str, relationship: str, target: str, evidence: str) -> dict:
    """
    Create one standardized relationship record.
    """
    return {
        "source": source,
        "relationship": relationship,
        "target": target,
        "evidence": evidence,
    }


def create_relationships(datasets: dict[str, pd.DataFrame]) -> pd.DataFrame:
    """
    Create relationships between graph entities.

    Returns a DataFrame with:
    - source
    - relationship
    - target
    - evidence
    """

    relationships = []

    # Incident -> Asset
    for _, row in datasets["incidents"].iterrows():
        relationships.append(
            make_relationship(
                source=f"incident:{row['incident_id']}",
                relationship="INVOLVES_ASSET",
                target=f"asset:{row['asset_id']}",
                evidence="incidents",
            )
        )

    # Incident -> Alert
    for _, row in datasets["alerts"].iterrows():
        relationships.append(
            make_relationship(
                source=f"incident:{row['incident_id']}",
                relationship="HAS_ALERT",
                target=f"alert:{row['alert_id']}",
                evidence="alerts",
            )
        )

        # Alert -> Asset
        relationships.append(
            make_relationship(
                source=f"alert:{row['alert_id']}",
                relationship="OBSERVED_ON_ASSET",
                target=f"asset:{row['asset_id']}",
                evidence="alerts",
            )
        )

        # Alert -> Process
        if pd.notna(row.get("process")):
            relationships.append(
                make_relationship(
                    source=f"alert:{row['alert_id']}",
                    relationship="EXECUTED_PROCESS",
                    target=f"process:{row['process']}",
                    evidence="alerts",
                )
            )

        # Alert -> IP
        if pd.notna(row.get("ip")):
            relationships.append(
                make_relationship(
                    source=f"alert:{row['alert_id']}",
                    relationship="CONTACTED_IP",
                    target=f"ip:{row['ip']}",
                    evidence="alerts",
                )
            )

        # Alert -> Domain
        if pd.notna(row.get("domain")):
            relationships.append(
                make_relationship(
                    source=f"alert:{row['alert_id']}",
                    relationship="CONTACTED_DOMAIN",
                    target=f"domain:{row['domain']}",
                    evidence="alerts",
                )
            )

        # Alert -> File hash
        if pd.notna(row.get("file_hash")):
            relationships.append(
                make_relationship(
                    source=f"alert:{row['alert_id']}",
                    relationship="INVOLVED_HASH",
                    target=f"hash:{row['file_hash']}",
                    evidence="alerts",
                )
            )

        # Alert -> MITRE
        if pd.notna(row.get("mitre_id")):
            relationships.append(
                make_relationship(
                    source=f"alert:{row['alert_id']}",
                    relationship="MAPS_TO_MITRE",
                    target=f"mitre:{row['mitre_id']}",
                    evidence="alerts",
                )
            )

    # Asset -> CVE
    for _, row in datasets["vulnerabilities"].iterrows():
        relationships.append(
            make_relationship(
                source=f"asset:{row['asset_id']}",
                relationship="HAS_VULNERABILITY",
                target=f"cve:{row['cve_id']}",
                evidence="vulnerabilities",
            )
        )

    # Alert -> Threat Intel Indicator
    threat_indicators = set(datasets["threat_intel"]["indicator"].dropna())

    for _, row in datasets["alerts"].iterrows():
        alert_id = f"alert:{row['alert_id']}"

        for field in ["ip", "domain", "file_hash"]:
            value = row.get(field)

            if pd.notna(value) and value in threat_indicators:
                relationships.append(
                    make_relationship(
                        source=alert_id,
                        relationship="MATCHES_THREAT_INTEL",
                        target=f"indicator:{value}",
                        evidence="alerts + threat_intel",
                    )
                )

    # Process -> MITRE from mapping table
    for _, row in datasets["mitre_mapping"].iterrows():
        relationships.append(
            make_relationship(
                source=f"process:{row['observable']}",
                relationship="CAN_MAP_TO_MITRE",
                target=f"mitre:{row['technique_id']}",
                evidence="mitre_mapping",
            )
        )

    relationship_df = pd.DataFrame(relationships)

    relationship_df = (
        relationship_df
        .dropna(subset=["source", "target"])
        .drop_duplicates(subset=["source", "relationship", "target"])
        .reset_index(drop=True)
    )

    return relationship_df