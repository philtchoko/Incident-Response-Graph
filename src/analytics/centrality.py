"""
centrality.py

Graph centrality analytics for the Incident Knowledge Graph.

Centrality helps identify important entities in the graph:
- assets involved in many incidents
- alerts connected to many indicators
- MITRE techniques appearing across multiple alerts
- CVEs connected to important assets
"""

import networkx as nx
import pandas as pd


def calculate_degree_centrality(graph: nx.MultiDiGraph) -> pd.DataFrame:
    """
    Calculate degree centrality for each node.

    Degree centrality measures how connected a node is.
    In this project, highly connected nodes may represent important
    assets, recurring indicators, common MITRE techniques, or frequent CVEs.
    """

    simple_graph = nx.Graph(graph)
    scores = nx.degree_centrality(simple_graph)

    rows = []

    for node, score in scores.items():
        rows.append(
            {
                "entity_id": node,
                "entity_type": graph.nodes[node].get("entity_type"),
                "value": graph.nodes[node].get("value"),
                "degree": simple_graph.degree(node),
                "degree_centrality": score,
            }
        )

    return (
        pd.DataFrame(rows)
        .sort_values("degree_centrality", ascending=False)
        .reset_index(drop=True)
    )


def calculate_betweenness_centrality(graph: nx.MultiDiGraph) -> pd.DataFrame:
    """
    Calculate betweenness centrality for each node.

    Betweenness centrality identifies nodes that act as bridges
    between different parts of the graph.

    In cybersecurity, a high-betweenness asset, IP, process, or MITRE
    technique may connect multiple incidents or campaigns.
    """

    simple_graph = nx.Graph(graph)
    scores = nx.betweenness_centrality(simple_graph)

    rows = []

    for node, score in scores.items():
        rows.append(
            {
                "entity_id": node,
                "entity_type": graph.nodes[node].get("entity_type"),
                "value": graph.nodes[node].get("value"),
                "degree": simple_graph.degree(node),
                "betweenness_centrality": score,
            }
        )

    return (
        pd.DataFrame(rows)
        .sort_values("betweenness_centrality", ascending=False)
        .reset_index(drop=True)
    )


def get_top_central_entities(
    graph: nx.MultiDiGraph,
    metric: str = "degree",
    top_n: int = 10,
    entity_type: str | None = None,
) -> pd.DataFrame:
    """
    Return the top central entities.

    Args:
        graph:
            Incident Knowledge Graph.
        metric:
            Either "degree" or "betweenness".
        top_n:
            Number of rows to return.
        entity_type:
            Optional filter, such as "Asset", "IP", "CVE", or "MITRETechnique".
    """

    if metric == "degree":
        df = calculate_degree_centrality(graph)
        score_col = "degree_centrality"

    elif metric == "betweenness":
        df = calculate_betweenness_centrality(graph)
        score_col = "betweenness_centrality"

    else:
        raise ValueError("metric must be either 'degree' or 'betweenness'")

    if entity_type:
        df = df[df["entity_type"] == entity_type]

    return df.sort_values(score_col, ascending=False).head(top_n).reset_index(drop=True)


def summarize_centrality(graph: nx.MultiDiGraph, top_n: int = 10) -> dict[str, pd.DataFrame]:
    """
    Produce a small centrality summary for analyst reporting.

    Returns:
        Dictionary containing top degree and betweenness tables.
    """

    return {
        "top_degree": get_top_central_entities(
            graph,
            metric="degree",
            top_n=top_n,
        ),
        "top_betweenness": get_top_central_entities(
            graph,
            metric="betweenness",
            top_n=top_n,
        ),
        "top_assets": get_top_central_entities(
            graph,
            metric="degree",
            top_n=top_n,
            entity_type="Asset",
        ),
        "top_mitre_techniques": get_top_central_entities(
            graph,
            metric="degree",
            top_n=top_n,
            entity_type="MITRETechnique",
        ),
    }