"""
recommendations.py

Generates simple rule-based analyst recommendations from graph context.

This is not machine learning yet. It is an explainable recommendation layer
that helps translate graph relationships into practical investigation guidance.
"""

import networkx as nx
import pandas as pd


def get_related_entity_types(
    graph: nx.MultiDiGraph,
    entity_id: str,
    radius: int = 2,
) -> set[str]:
    """
    Return entity types connected to the selected entity within a radius.
    """

    if entity_id not in graph:
        return set()

    undirected_graph = graph.to_undirected()

    nearby_nodes = nx.single_source_shortest_path_length(
        undirected_graph,
        entity_id,
        cutoff=radius,
    )

    return {
        graph.nodes[node].get("entity_type")
        for node in nearby_nodes
        if node != entity_id
    }


def get_related_relationships(
    graph: nx.MultiDiGraph,
    entity_id: str,
) -> set[str]:
    """
    Return relationship types directly connected to an entity.
    """

    if entity_id not in graph:
        return set()

    relationships = set()

    for _, _, attrs in graph.out_edges(entity_id, data=True):
        relationships.add(attrs.get("relationship"))

    for _, _, attrs in graph.in_edges(entity_id, data=True):
        relationships.add(attrs.get("relationship"))

    return relationships


def recommend_for_entity(
    graph: nx.MultiDiGraph,
    entity_id: str,
) -> list[str]:
    """
    Generate analyst recommendations for any selected graph entity.
    """

    if entity_id not in graph:
        return ["Entity not found in graph."]

    entity_type = graph.nodes[entity_id].get("entity_type")
    related_types = get_related_entity_types(graph, entity_id)
    relationships = get_related_relationships(graph, entity_id)

    recommendations = []

    if entity_type == "Asset":
        if "CVE" in related_types:
            recommendations.append(
                "Review vulnerabilities connected to this asset, prioritizing Critical, High, or KEV-related CVEs."
            )

        if "Incident" in related_types or "Alert" in related_types:
            recommendations.append(
                "Review recent incidents and alerts involving this asset to determine whether vulnerabilities are being actively exploited."
            )

        if "ThreatIndicator" in related_types:
            recommendations.append(
                "Investigate threat intelligence matches connected to this asset and check for additional related indicators."
            )

    elif entity_type == "Incident":
        if "ThreatIndicator" in related_types:
            recommendations.append(
                "Prioritize this incident for review because it is connected to known threat intelligence indicators."
            )

        if "MITRETechnique" in related_types:
            recommendations.append(
                "Review the mapped MITRE ATT&CK techniques and validate whether existing detections cover this behavior."
            )

        if "CVE" in related_types:
            recommendations.append(
                "Check whether vulnerabilities on the affected asset may have contributed to this incident."
            )

    elif entity_type == "IP":
        recommendations.append(
            "Check whether this IP appears in threat intelligence and whether multiple assets contacted it."
        )

    elif entity_type == "Domain":
        recommendations.append(
            "Review DNS/network activity for this domain and identify all assets that contacted it."
        )

    elif entity_type == "Process":
        if "MITRETechnique" in related_types:
            recommendations.append(
                "Review the MITRE technique associated with this process and inspect command-line activity where available."
            )
        else:
            recommendations.append(
                "Review alerts involving this process and determine whether it is expected in the environment."
            )

    elif entity_type == "CVE":
        recommendations.append(
            "Identify all assets affected by this CVE and prioritize remediation based on asset criticality and incident history."
        )

    elif entity_type == "MITRETechnique":
        recommendations.append(
            "Review incidents mapped to this technique and evaluate whether additional detection rules are needed."
        )

    if "MATCHES_THREAT_INTEL" in relationships:
        recommendations.append(
            "Because this entity directly matches threat intelligence, escalate for analyst review."
        )

    if not recommendations:
        recommendations.append(
            "Review connected entities and incidents to determine whether this item is part of a broader pattern."
        )

    return recommendations


def generate_recommendation_table(
    graph: nx.MultiDiGraph,
    entity_ids: list[str],
) -> pd.DataFrame:
    """
    Generate a table of recommendations for several entities.
    """

    rows = []

    for entity_id in entity_ids:
        recommendations = recommend_for_entity(graph, entity_id)

        rows.append(
            {
                "entity_id": entity_id,
                "entity_type": graph.nodes[entity_id].get("entity_type")
                if entity_id in graph
                else None,
                "value": graph.nodes[entity_id].get("value")
                if entity_id in graph
                else None,
                "recommendations": " | ".join(recommendations),
            }
        )

    return pd.DataFrame(rows)