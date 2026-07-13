"""
incident_view.py

Dashboard view for incident-specific investigation and similarity analysis.
"""

import pandas as pd
import streamlit as st

from src.graph.graph_queries import get_entity_detail, get_neighbors
from src.analytics.similar_incidents import find_similar_incidents
from src.analytics.recommendations import recommend_for_entity


def get_incident_nodes(graph) -> list[str]:
    """
    Return all incident node IDs from the graph.
    """

    return sorted(
        [
            node
            for node, attrs in graph.nodes(data=True)
            if attrs.get("entity_type") == "Incident"
        ]
    )


def render_incident_view(graph):
    """
    Render incident detail and similar incident analysis.
    """

    st.header("Incident Investigation")

    incident_nodes = get_incident_nodes(graph)

    if not incident_nodes:
        st.warning("No incident nodes found in the graph.")
        return

    selected_incident = st.selectbox(
        "Select an incident",
        incident_nodes,
    )

    detail = get_entity_detail(graph, selected_incident)

    if detail:
        st.subheader("Incident Details")

        col1, col2, col3 = st.columns(3)
        col1.metric("Entity Type", detail["entity_type"])
        col2.metric("Total Connections", detail["total_degree"])
        col3.metric("Source", detail["source"])

        st.write(f"**Title:** {detail['value']}")
        st.write(f"**Incident ID:** `{detail['entity_id']}`")

    st.subheader("Incident Neighborhood")
    neighbors = get_neighbors(graph, selected_incident)

    if neighbors.empty:
        st.info("No connected entities found.")
    else:
        st.dataframe(neighbors, use_container_width=True)

    st.subheader("Similar Incidents")
    similar = find_similar_incidents(
        graph,
        selected_incident,
        top_n=5,
        radius=2,
    )

    if similar.empty:
        st.info("No similar incidents found.")
    else:
        st.dataframe(similar, use_container_width=True)

    st.subheader("Analyst Recommendations")
    recommendations = recommend_for_entity(graph, selected_incident)

    for rec in recommendations:
        st.write(f"- {rec}")