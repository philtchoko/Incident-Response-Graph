"""
graph_queries.py

Reusable query functions for exploring the Incident Knowledge Graph.
"""

import networkx as nx
import pandas as pd


def search_entities(
    graph: nx.MultiDiGraph,
    query: str,
    ) -> pd.DataFrame:
    """
    Search graph entities by entity_id or displayed value.

    Args:
        graph:
            Incident knowledge graph.
        query:
            Search string.

    Returns:
        DataFrame of matching entities.
    """

    query = query.strip().lower()

    results = []

    for node, attrs in graph.nodes(data=True):
        entity_id = str(node)
        value = str(attrs.get("value", ""))
        entity_type = attrs.get("entity_type", "Unknown")

        if query in entity_id.lower() or query in value.lower():
            results.append(
                {
                    "entity_id": entity_id,
                    "entity_type": entity_type,
                    "value": value,
                    "source": attrs.get("source"),
                }
            )

    return pd.DataFrame(results)


def get_neighbors(
    graph: nx.MultiDiGraph,
    entity_id: str,
    ) -> pd.DataFrame:
    """
    Return incoming and outgoing neighbors for a selected entity.
    """

    if entity_id not in graph:
        return pd.DataFrame(
            columns=[
                "direction",
                "source",
                "relationship",
                "target",
                "neighbor_type",
                "neighbor_value",
            ]
        )

    rows = []

    # Outgoing edges
    for _, target, attrs in graph.out_edges(entity_id, data=True):
        rows.append(
            {
                "direction": "outgoing",
                "source": entity_id,
                "relationship": attrs.get("relationship"),
                "target": target,
                "neighbor_type": graph.nodes[target].get("entity_type"),
                "neighbor_value": graph.nodes[target].get("value"),
            }
        )

    # Incoming edges
    for source, _, attrs in graph.in_edges(entity_id, data=True):
        rows.append(
            {
                "direction": "incoming",
                "source": source,
                "relationship": attrs.get("relationship"),
                "target": entity_id,
                "neighbor_type": graph.nodes[source].get("entity_type"),
                "neighbor_value": graph.nodes[source].get("value"),
            }
        )

    return pd.DataFrame(rows)


def find_connected_incidents(
    graph: nx.MultiDiGraph,
    entity_id: str,
    cutoff: int = 3,
    ) -> pd.DataFrame:
    """
    Find incidents within a short graph distance of a selected entity.

    Example:
    Search an IP and return incidents connected to that IP.
    """

    if entity_id not in graph:
        return pd.DataFrame(
            columns=[
                "incident_id",
                "incident_title",
                "distance",
                "path",
            ]
        )

    undirected_graph = graph.to_undirected()

    paths = nx.single_source_shortest_path(
        undirected_graph,
        entity_id,
        cutoff=cutoff,
    )

    rows = []

    for node, path in paths.items():
        if node == entity_id:
            continue

        if graph.nodes[node].get("entity_type") == "Incident":
            rows.append(
                {
                    "incident_id": node,
                    "incident_title": graph.nodes[node].get("value"),
                    "distance": len(path) - 1,
                    "path": " -> ".join(path),
                }
            )

    return (
        pd.DataFrame(rows)
        .sort_values(["distance", "incident_id"])
        .reset_index(drop=True)
        if rows
        else pd.DataFrame(columns=["incident_id", "incident_title", "distance", "path"])
    )


def find_shortest_path(
    graph: nx.MultiDiGraph,
    source: str,
    target: str,
    ) -> list[str] | None:
    """
    Find the shortest undirected path between two entities.

    Returns None if either node is missing or no path exists.
    """

    if source not in graph or target not in graph:
        return None

    try:
        return nx.shortest_path(
            graph.to_undirected(),
            source=source,
            target=target,
        )
    except nx.NetworkXNoPath:
        return None


def get_entity_detail(
    graph: nx.MultiDiGraph,
    entity_id: str,
    ) -> dict | None:
    """
    Return details for a single graph entity.
    """

    if entity_id not in graph:
        return None

    attrs = graph.nodes[entity_id]

    return {
        "entity_id": entity_id,
        "entity_type": attrs.get("entity_type"),
        "value": attrs.get("value"),
        "source": attrs.get("source"),
        "in_degree": graph.in_degree(entity_id),
        "out_degree": graph.out_degree(entity_id),
        "total_degree": graph.degree(entity_id),
    }


def get_entities_by_type(
    graph: nx.MultiDiGraph,
    entity_type: str,
    ) -> pd.DataFrame:
    """
    Return all entities of a selected type.
    """

    rows = []

    for node, attrs in graph.nodes(data=True):
        if attrs.get("entity_type") == entity_type:
            rows.append(
                {
                    "entity_id": node,
                    "entity_type": attrs.get("entity_type"),
                    "value": attrs.get("value"),
                    "source": attrs.get("source"),
                    "degree": graph.degree(node),
                }
            )

    return pd.DataFrame(rows).sort_values("degree", ascending=False)