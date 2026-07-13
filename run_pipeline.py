"""
run_pipeline.py

Runs the complete Incident Knowledge Graph MVP pipeline.
"""

from pathlib import Path

from src.ingestion.csv_loader import load_and_normalize
from src.extraction.extract_entities import extract_entities
from src.extraction.create_relationships import create_relationships

from src.graph.build_graph import (
    build_graph,
    get_graph_summary,
    save_graph_html,
    get_local_subgraph,
)

from src.analytics.centrality import summarize_centrality
from src.analytics.recurring_entities import (
    get_recurring_entities,
    get_entities_connected_to_multiple_incidents,
)
from src.analytics.similar_incidents import find_all_similar_incident_pairs
from src.analytics.recommendations import generate_recommendation_table


def main():
    data_dir = Path("data/raw")
    processed_dir = Path("data/processed")
    output_dir = Path("output")

    processed_dir.mkdir(parents=True, exist_ok=True)
    output_dir.mkdir(parents=True, exist_ok=True)

    print("Loading and normalizing datasets...")
    datasets = load_and_normalize(data_dir)

    print("Extracting entities...")
    entities = extract_entities(datasets)

    print("Creating relationships...")
    relationships = create_relationships(datasets)

    entities_path = processed_dir / "entities.csv"
    relationships_path = processed_dir / "relationships.csv"

    print("Saving processed files...")
    entities.to_csv(entities_path, index=False)
    relationships.to_csv(relationships_path, index=False)

    print("Building graph...")
    graph = build_graph(entities, relationships)
    summary = get_graph_summary(graph)

    print("\n========== GRAPH SUMMARY ==========")
    print(f"Nodes: {summary['nodes']}")
    print(f"Edges: {summary['edges']}")

    print("\nRunning analytics...")
    centrality_summary = summarize_centrality(graph, top_n=10)

    centrality_summary["top_degree"].to_csv(
        output_dir / "top_degree_entities.csv",
        index=False,
    )

    centrality_summary["top_betweenness"].to_csv(
        output_dir / "top_betweenness_entities.csv",
        index=False,
    )

    centrality_summary["top_assets"].to_csv(
        output_dir / "top_assets.csv",
        index=False,
    )

    centrality_summary["top_mitre_techniques"].to_csv(
        output_dir / "top_mitre_techniques.csv",
        index=False,
    )

    get_recurring_entities(graph, min_degree=2).to_csv(
        output_dir / "recurring_entities.csv",
        index=False,
    )

    get_entities_connected_to_multiple_incidents(
        graph,
        min_incidents=2,
    ).to_csv(
        output_dir / "entities_connected_to_multiple_incidents.csv",
        index=False,
    )

    find_all_similar_incident_pairs(
        graph,
        min_similarity=0.2,
        radius=2,
    ).to_csv(
        output_dir / "similar_incidents.csv",
        index=False,
    )

    top_entities = (
        centrality_summary["top_degree"]["entity_id"]
        .head(10)
        .tolist()
    )

    generate_recommendation_table(
        graph,
        top_entities,
    ).to_csv(
        output_dir / "recommendations.csv",
        index=False,
    )

    print("Saving dashboard graph visualization...")

    # Pick a useful default graph center:
    # first incident if available, otherwise first entity.
    incident_entities = entities[entities["entity_type"] == "Incident"]

    if not incident_entities.empty:
        center_node = incident_entities.iloc[0]["entity_id"]
    else:
        center_node = entities.iloc[0]["entity_id"]

    local_graph = get_local_subgraph(
        graph,
        center_node=center_node,
        radius=2,
    )

    save_graph_html(
        local_graph,
        output_dir / "incident_graph.html",
    )

    print("\nPipeline complete.")
    print("\nDashboard-ready files generated:")
    print(f"- {entities_path}")
    print(f"- {relationships_path}")
    print(f"- {output_dir / 'incident_graph.html'}")
    print(f"- {output_dir / 'top_degree_entities.csv'}")
    print(f"- {output_dir / 'top_betweenness_entities.csv'}")
    print(f"- {output_dir / 'recurring_entities.csv'}")
    print(f"- {output_dir / 'similar_incidents.csv'}")
    print(f"- {output_dir / 'recommendations.csv'}")

    print("\nLaunch dashboard with:")
    print("streamlit run src/dashboard/app.py")


if __name__ == "__main__":
    main()