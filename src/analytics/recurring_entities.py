"""
recurring_entities.py

Finds entities that repeatedly appear across incidents, alerts, and relationships.
"""

import networkx as nx
import pandas as pd


def get_recurring_entities(
    graph: nx.MultiDiGraph,
    min_degree: int = 2,
    entity_type: str | None = None,
) -> pd.DataFrame:
    """
    Identify entities that appear repeatedly in the graph.

    Args:
        graph:
            Incident Knowledge Graph.
        min_degree:
            Minimum number of graph connections required.
        entity_type:
            Optional entity type filter, such as "Asset", "IP", "Domain", or "Process".

    Returns:
        DataFrame of recurring entities.
    """

    rows = []

    for node, attrs in graph.nodes(data=True):
        node_type = attrs.get("entity_type")

        if entity_type and node_type != entity_type:
            continue

        degree = graph.degree(node)

        if degree >= min_degree:
            rows.append(
                {
                    "entity_id": node,
                    "entity_type": node_type,
                    "value": attrs.get("value"),
                    "degree": degree,
                    "source": attrs.get("source"),
                }
            )

    return (
        pd.DataFrame(rows)
        .sort_values("degree", ascending=False)
        .reset_index(drop=True)
    )


def get_recurring_by_type(
    graph: nx.MultiDiGraph,
    min_degree: int = 2,
) -> dict[str, pd.DataFrame]:
    """
    Return recurring entities grouped by entity type.
    """

    entity_types = sorted(
        {
            attrs.get("entity_type")
            for _, attrs in graph.nodes(data=True)
            if attrs.get("entity_type")
        }
    )

    return {
        entity_type: get_recurring_entities(
            graph,
            min_degree=min_degree,
            entity_type=entity_type,
        )
        for entity_type in entity_types
    }


def get_entities_connected_to_multiple_incidents(
    graph: nx.MultiDiGraph,
    min_incidents: int = 2,
) -> pd.DataFrame:
    """
    Identify entities connected to multiple incidents within a short graph distance.

    This is useful for finding recurring indicators, assets, processes,
    domains, or MITRE techniques across different cases.
    """

    undirected_graph = graph.to_undirected()
    rows = []

    incident_nodes = {
        node
        for node, attrs in graph.nodes(data=True)
        if attrs.get("entity_type") == "Incident"
    }

    for node, attrs in graph.nodes(data=True):
        if attrs.get("entity_type") == "Incident":
            continue

        connected_incidents = []

        for incident in incident_nodes:
            try:
                distance = nx.shortest_path_length(
                    undirected_graph,
                    source=node,
                    target=incident,
                )

                if distance <= 3:
                    connected_incidents.append(incident)

            except nx.NetworkXNoPath:
                continue

        if len(connected_incidents) >= min_incidents:
            rows.append(
                {
                    "entity_id": node,
                    "entity_type": attrs.get("entity_type"),
                    "value": attrs.get("value"),
                    "incident_count": len(connected_incidents),
                    "connected_incidents": ", ".join(sorted(connected_incidents)),
                }
            )

    return (
        pd.DataFrame(rows)
        .sort_values("incident_count", ascending=False)
        .reset_index(drop=True)
    )