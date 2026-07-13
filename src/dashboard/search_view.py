"""
search_view.py

Dashboard view for searching entities and exploring their graph context.
"""

import pandas as pd
import streamlit as st

from src.graph.graph_queries import (
    search_entities,
    get_entity_detail,
    get_neighbors,
    find_connected_incidents,
)
from src.analytics.recommendations import recommend_for_entity


def render_search_view(graph):
    """
    Render entity search and local investigation context.
    """

    st.header("Entity Search")

    query = st.text_input(
        "Search for an asset, incident, alert, CVE, IP, domain, process, hash, or MITRE technique"
    )

    if not query:
        st.info("Enter a search term to begin.")
        return

    results = search_entities(graph, query)

    if results.empty:
        st.warning("No matching entities found.")
        return

    st.subheader("Search Results")
    st.dataframe(results, use_container_width=True)

    selected_entity = st.selectbox(
        "Select an entity to investigate",
        results["entity_id"].tolist(),
    )

    detail = get_entity_detail(graph, selected_entity)

    if detail:
        st.subheader("Entity Details")

        col1, col2, col3 = st.columns(3)

        col1.metric("Entity Type", detail["entity_type"])
        col2.metric("Total Connections", detail["total_degree"])
        col3.metric("Source", detail["source"])

        st.write(f"**Value:** {detail['value']}")
        st.write(f"**Entity ID:** `{detail['entity_id']}`")

    st.subheader("Connected Entities")
    neighbors = get_neighbors(graph, selected_entity)

    if neighbors.empty:
        st.info("No directly connected entities found.")
    else:
        st.dataframe(neighbors, use_container_width=True)

    st.subheader("Connected Incidents")
    connected_incidents = find_connected_incidents(
        graph,
        selected_entity,
        cutoff=3,
    )

    if connected_incidents.empty:
        st.info("No connected incidents found within three hops.")
    else:
        st.dataframe(connected_incidents, use_container_width=True)

    st.subheader("Analyst Recommendations")
    recommendations = recommend_for_entity(graph, selected_entity)

    for rec in recommendations:
        st.write(f"- {rec}")