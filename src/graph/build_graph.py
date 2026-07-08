"""
build_graph.py

Builds a NetworkX graph from extracted entities and relationships.
"""

from pathlib import Path

import networkx as nx
import pandas as pd

from src.graph.graph_schema import (
    validate_entities_schema,
    validate_relationships_schema,
)


def build_graph(
    entities_df: pd.DataFrame,
    relationships_df: pd.DataFrame,
) -> nx.MultiDiGraph:
    """
    Build a directed multigraph from entity and relationship DataFrames.

    Nodes come from entities_df.
    Edges come from relationships_df.

    Args:
        entities_df:
            DataFrame with entity_id, entity_type, value, source.
        relationships_df:
            DataFrame with source, relationship, target, evidence.

    Returns:
        NetworkX MultiDiGraph.
    """

    validate_entities_schema(entities_df)
    validate_relationships_schema(relationships_df)

    graph = nx.MultiDiGraph()

    for _, row in entities_df.iterrows():
        graph.add_node(
            row["entity_id"],
            entity_type=row["entity_type"],
            value=row["value"],
            source=row.get("source"),
        )

    for _, row in relationships_df.iterrows():
        source = row["source"]
        target = row["target"]

        # Only add edges where both nodes exist.
        # This prevents dangling relationships from breaking the graph.
        if source not in graph:
            graph.add_node(
                source,
                entity_type="Unknown",
                value=source,
                source="relationship_only",
            )

        if target not in graph:
            graph.add_node(
                target,
                entity_type="Unknown",
                value=target,
                source="relationship_only",
            )

        graph.add_edge(
            source,
            target,
            relationship=row["relationship"],
            evidence=row.get("evidence"),
        )

    return graph


def load_graph_from_csv(
    entities_path: Path,
    relationships_path: Path,
) -> nx.MultiDiGraph:
    """
    Load entities and relationships from CSV files and build a graph.
    """

    entities_df = pd.read_csv(entities_path)
    relationships_df = pd.read_csv(relationships_path)

    return build_graph(entities_df, relationships_df)


def get_graph_summary(graph: nx.MultiDiGraph) -> dict:
    """
    Return simple graph summary metrics.
    """

    node_type_counts = {}

    for _, attrs in graph.nodes(data=True):
        node_type = attrs.get("entity_type", "Unknown")
        node_type_counts[node_type] = node_type_counts.get(node_type, 0) + 1

    relationship_type_counts = {}

    for _, _, attrs in graph.edges(data=True):
        rel_type = attrs.get("relationship", "UNKNOWN")
        relationship_type_counts[rel_type] = relationship_type_counts.get(rel_type, 0) + 1

    return {
        "nodes": graph.number_of_nodes(),
        "edges": graph.number_of_edges(),
        "node_type_counts": node_type_counts,
        "relationship_type_counts": relationship_type_counts,
    }

def get_local_subgraph(graph, center_node: str, radius: int = 2):
    """
    Return a smaller subgraph around one selected node.

    This helps avoid rendering the entire graph at once.
    """

    if center_node not in graph:
        raise ValueError(f"Node not found in graph: {center_node}")

    undirected_graph = graph.to_undirected()

    nodes = nx.single_source_shortest_path_length(
        undirected_graph,
        center_node,
        cutoff=radius,
    ).keys()

    return graph.subgraph(nodes).copy()

def save_graph_html(graph: nx.MultiDiGraph, output_path: Path) -> None:
    """
    Save an interactive HTML graph using pyvis.
    """

    try:
        from pyvis.network import Network
    except ImportError:
        print("pyvis is not installed. Skipping graph HTML export.")
        return

    output_path.parent.mkdir(parents=True, exist_ok=True)

    net = Network(
        height="750px",
        width="100%",
        directed=True,
        notebook=False,
        bgcolor="#ffffff",
        font_color="#222222",
    )

    net.force_atlas_2based(
        gravity=-80,
        central_gravity=0.01,
        spring_length=180,
        spring_strength=0.08,
        damping=0.4,
    )

    for node, attrs in graph.nodes(data=True):
        node_type = attrs.get("entity_type", "Unknown")
        label = str(attrs.get("value", node))

        net.add_node(
            node,
            label=label,
            title=f"{node_type}: {node}",
            group=node_type,
        )

    for source, target, attrs in graph.edges(data=True):
        relationship = attrs.get("relationship", "")

        net.add_edge(
            source,
            target,
            label=relationship,
            title=relationship,
        )

    net.write_html(str(output_path))