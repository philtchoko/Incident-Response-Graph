"""
app.py

Streamlit dashboard for the Incident Knowledge Graph MVP.
"""

from pathlib import Path
import sys

import pandas as pd
import streamlit as st

# Allows Streamlit to import src modules when run from project root.
PROJECT_ROOT = Path(__file__).resolve().parents[2]

if str(PROJECT_ROOT) not in sys.path:
    sys.path.insert(0, str(PROJECT_ROOT))

from src.graph.build_graph import build_graph, get_graph_summary
from src.dashboard.search_view import render_search_view
from src.dashboard.incident_view import render_incident_view
from src.dashboard.graph_view import render_graph_view

from src.analytics.centrality import summarize_centrality
from src.analytics.recurring_entities import (
    get_recurring_entities,
    get_entities_connected_to_multiple_incidents,
)


ENTITIES_PATH = PROJECT_ROOT / "data" / "processed" / "entities.csv"
RELATIONSHIPS_PATH = PROJECT_ROOT / "data" / "processed" / "relationships.csv"
GRAPH_HTML_PATH = PROJECT_ROOT / "output" / "incident_graph.html"


@st.cache_data
def load_processed_data():
    """
    Load processed graph data from CSV.
    """

    entities = pd.read_csv(ENTITIES_PATH)
    relationships = pd.read_csv(RELATIONSHIPS_PATH)

    return entities, relationships



def load_graph(entities, relationships):
    """
    Build and cache NetworkX graph.
    """

    return build_graph(entities, relationships)


def render_overview(graph):
    """
    Render dashboard overview page.
    """

    st.header("Overview")

    summary = get_graph_summary(graph)

    col1, col2, col3 = st.columns(3)
    col1.metric("Nodes", summary["nodes"])
    col2.metric("Edges", summary["edges"])
    col3.metric("Node Types", len(summary["node_type_counts"]))

    st.subheader("Node Type Counts")
    node_counts = pd.DataFrame(
        [
            {"node_type": key, "count": value}
            for key, value in summary["node_type_counts"].items()
        ]
    ).sort_values("count", ascending=False)

    st.dataframe(node_counts, use_container_width=True)

    st.subheader("Relationship Type Counts")
    rel_counts = pd.DataFrame(
        [
            {"relationship": key, "count": value}
            for key, value in summary["relationship_type_counts"].items()
        ]
    ).sort_values("count", ascending=False)

    st.dataframe(rel_counts, use_container_width=True)

    st.subheader("Top Central Entities")
    centrality = summarize_centrality(graph, top_n=10)

    st.write("**Top connected entities**")
    st.dataframe(centrality["top_degree"], use_container_width=True)

    st.write("**Top bridge entities**")
    st.dataframe(centrality["top_betweenness"], use_container_width=True)

    st.subheader("Recurring Entities")
    recurring = get_recurring_entities(graph, min_degree=2)
    st.dataframe(recurring.head(20), use_container_width=True)

    st.subheader("Entities Connected to Multiple Incidents")
    multi_incident_entities = get_entities_connected_to_multiple_incidents(
        graph,
        min_incidents=2,
    )
    st.dataframe(multi_incident_entities.head(20), use_container_width=True)


def main():
    st.set_page_config(
        page_title="Incident Knowledge Graph",
        page_icon="🕸️",
        layout="wide",
    )

    st.title("Incident Knowledge Graph MVP")
    st.caption(
        "Search incidents, assets, indicators, vulnerabilities, and MITRE techniques through a graph-based investigation interface."
    )

    if not ENTITIES_PATH.exists() or not RELATIONSHIPS_PATH.exists():
        st.error(
            "Processed graph files not found. Run `python run_pipeline.py` before launching the dashboard."
        )
        st.stop()

    entities, relationships = load_processed_data()
    graph = load_graph(entities, relationships)

    page = st.sidebar.radio(
        "Navigation",
        [
            "Overview",
            "Entity Search",
            "Incident Investigation",
            "Graph Visualization",
        ],
    )

    if page == "Overview":
        render_overview(graph)

    elif page == "Entity Search":
        render_search_view(graph)

    elif page == "Incident Investigation":
        render_incident_view(graph)

    elif page == "Graph Visualization":
        render_graph_view(GRAPH_HTML_PATH)


if __name__ == "__main__":
    main()