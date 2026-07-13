"""
graph_view.py

Dashboard view for displaying the generated PyVis graph HTML.
"""

from pathlib import Path

import streamlit as st
import streamlit.components.v1 as components


def render_graph_view(graph_html_path: Path):
    """
    Render the PyVis graph HTML inside Streamlit.
    """

    st.header("Graph Visualization")

    if not graph_html_path.exists():
        st.warning(
            "Graph visualization file not found. Run `python run_pipeline.py` first."
        )
        return

    html = graph_html_path.read_text(encoding="utf-8")

    components.html(
        html,
        height=750,
        scrolling=True,
    )

    st.caption(
        "This is a focused graph visualization. The full graph may be too dense to interpret directly."
    )