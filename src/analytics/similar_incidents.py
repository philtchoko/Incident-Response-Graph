"""
similar_incidents.py

Finds similar incidents based on shared graph neighborhoods.
"""

import networkx as nx
import pandas as pd


def get_incident_neighbors(
    graph: nx.MultiDiGraph,
    incident_id: str,
    radius: int = 2,
) -> set[str]:
    """
    Get nearby entities connected to an incident.

    Args:
        graph:
            Incident Knowledge Graph.
        incident_id:
            Incident node ID, such as "incident:INC-001".
        radius:
            How many graph hops to include.

    Returns:
        Set of nearby entity IDs.
    """

    if not incident_id.startswith("incident:"):
        incident_id = f"incident:{incident_id}"

    if incident_id not in graph:
        return set()

    undirected_graph = graph.to_undirected()

    path_lengths = nx.single_source_shortest_path_length(
        undirected_graph,
        incident_id,
        cutoff=radius,
    )

    return {
        node
        for node, distance in path_lengths.items()
        if node != incident_id and distance <= radius
    }


def jaccard_similarity(set_a: set[str], set_b: set[str]) -> float:
    """
    Calculate Jaccard similarity between two sets.
    """

    if not set_a and not set_b:
        return 0.0

    intersection = len(set_a.intersection(set_b))
    union = len(set_a.union(set_b))

    if union == 0:
        return 0.0

    return intersection / union


def find_similar_incidents(
    graph: nx.MultiDiGraph,
    incident_id: str,
    top_n: int = 5,
    radius: int = 2,
) -> pd.DataFrame:
    """
    Find incidents that are similar to a selected incident.

    Similarity is calculated using shared neighboring entities.
    """

    if not incident_id.startswith("incident:"):
        incident_id = f"incident:{incident_id}"

    target_neighbors = get_incident_neighbors(
        graph,
        incident_id=incident_id,
        radius=radius,
    )

    rows = []

    for node, attrs in graph.nodes(data=True):
        if attrs.get("entity_type") != "Incident":
            continue

        if node == incident_id:
            continue

        candidate_neighbors = get_incident_neighbors(
            graph,
            incident_id=node,
            radius=radius,
        )

        score = jaccard_similarity(target_neighbors, candidate_neighbors)

        if score > 0:
            shared_entities = target_neighbors.intersection(candidate_neighbors)

            rows.append(
                {
                    "incident_id": node,
                    "incident_title": attrs.get("value"),
                    "similarity_score": round(score, 4),
                    "shared_entity_count": len(shared_entities),
                    "shared_entities": ", ".join(sorted(shared_entities)),
                }
            )

    if not rows:
        return pd.DataFrame(
            columns=[
                "incident_id",
                "incident_title",
                "similarity_score",
                "shared_entity_count",
                "shared_entities",
            ]
        )

    return (
        pd.DataFrame(rows)
        .sort_values(
            ["similarity_score", "shared_entity_count"],
            ascending=False,
        )
        .head(top_n)
        .reset_index(drop=True)
    )


def find_all_similar_incident_pairs(
    graph: nx.MultiDiGraph,
    min_similarity: float = 0.2,
    radius: int = 2,
        ) -> pd.DataFrame:
    """
    Find all incident pairs above a minimum similarity threshold.
    """

    incidents = [
        node
        for node, attrs in graph.nodes(data=True)
        if attrs.get("entity_type") == "Incident"
    ]

    rows = []

    for i, incident_a in enumerate(incidents):
        neighbors_a = get_incident_neighbors(graph, incident_a, radius=radius)

        for incident_b in incidents[i + 1:]:
            neighbors_b = get_incident_neighbors(graph, incident_b, radius=radius)

            score = jaccard_similarity(neighbors_a, neighbors_b)

            if score >= min_similarity:
                shared_entities = neighbors_a.intersection(neighbors_b)

                rows.append(
                    {
                        "incident_a": incident_a,
                        "incident_b": incident_b,
                        "similarity_score": round(score, 4),
                        "shared_entity_count": len(shared_entities),
                        "shared_entities": ", ".join(sorted(shared_entities)),
                    }
                )

    return (
        pd.DataFrame(rows)
        .sort_values("similarity_score", ascending=False)
        .reset_index(drop=True)
        if rows
        else pd.DataFrame(
            columns=[
                "incident_a",
                "incident_b",
                "similarity_score",
                "shared_entity_count",
                "shared_entities",
            ]
        )
    )