"""
graph_schema.py

Defines the supported node types and relationship types
for the Incident Knowledge Graph MVP.

This file acts as a schema contract so the rest of the project
uses consistent entity and relationship names.
"""


# Node types supported by the MVP graph.
NODE_TYPES = {
    "Asset",
    "Incident",
    "Alert",
    "Process",
    "IP",
    "Domain",
    "Hash",
    "CVE",
    "ThreatIndicator",
    "MITRETechnique",
}


# Relationship types supported by the MVP graph.
RELATIONSHIP_TYPES = {
    # Incident relationships
    "INVOLVES_ASSET",
    "HAS_ALERT",

    # Alert relationships
    "OBSERVED_ON_ASSET",
    "EXECUTED_PROCESS",
    "CONTACTED_IP",
    "CONTACTED_DOMAIN",
    "INVOLVED_HASH",
    "MAPS_TO_MITRE",
    "MATCHES_THREAT_INTEL",

    # Asset / vulnerability relationships
    "HAS_VULNERABILITY",

    # Process / MITRE enrichment relationships
    "CAN_MAP_TO_MITRE",
}


# Optional: human-readable descriptions for documentation/debugging.
NODE_TYPE_DESCRIPTIONS = {
    "Asset": "A device, server, workstation, VM, or monitored system.",
    "Incident": "A security incident or case record.",
    "Alert": "A detection, alert, or event associated with an incident.",
    "Process": "A process or executable observed during an alert.",
    "IP": "An IP address observed in alerts or threat intelligence.",
    "Domain": "A domain or URL-related entity.",
    "Hash": "A file hash associated with a suspicious or malicious file.",
    "CVE": "A vulnerability identifier.",
    "ThreatIndicator": "An IP, domain, hash, or other IOC from threat intelligence.",
    "MITRETechnique": "A MITRE ATT&CK technique.",
}


RELATIONSHIP_DESCRIPTIONS = {
    "INVOLVES_ASSET": "Connects an incident to an affected asset.",
    "HAS_ALERT": "Connects an incident to an alert.",
    "OBSERVED_ON_ASSET": "Connects an alert to the asset where it was observed.",
    "EXECUTED_PROCESS": "Connects an alert to a process involved in the event.",
    "CONTACTED_IP": "Connects an alert to an observed IP address.",
    "CONTACTED_DOMAIN": "Connects an alert to an observed domain.",
    "INVOLVED_HASH": "Connects an alert to a file hash.",
    "MAPS_TO_MITRE": "Connects an alert to a MITRE ATT&CK technique.",
    "MATCHES_THREAT_INTEL": "Connects an alert to a known threat intelligence indicator.",
    "HAS_VULNERABILITY": "Connects an asset to a CVE.",
    "CAN_MAP_TO_MITRE": "Connects an observable process to a MITRE ATT&CK technique.",
}


def is_valid_node_type(node_type: str) -> bool:
    """
    Check whether a node type is supported by the graph schema.
    """
    return node_type in NODE_TYPES


def is_valid_relationship_type(relationship_type: str) -> bool:
    """
    Check whether a relationship type is supported by the graph schema.
    """
    return relationship_type in RELATIONSHIP_TYPES


def validate_entities_schema(entities_df):
    """
    Validate that extracted entities use supported node types.

    Raises:
        ValueError if unsupported node types are found.
    """
    invalid_types = set(entities_df["entity_type"]) - NODE_TYPES

    if invalid_types:
        raise ValueError(
            f"Unsupported entity types found: {sorted(invalid_types)}"
        )


def validate_relationships_schema(relationships_df):
    """
    Validate that extracted relationships use supported relationship types.

    Raises:
        ValueError if unsupported relationship types are found.
    """
    invalid_relationships = set(relationships_df["relationship"]) - RELATIONSHIP_TYPES

    if invalid_relationships:
        raise ValueError(
            f"Unsupported relationship types found: {sorted(invalid_relationships)}"
        )