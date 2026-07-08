"""
run_pipeline.py

Runs the complete Incident Knowledge Graph pipeline.
"""

from pathlib import Path

from src.ingestion.csv_loader import load_and_normalize
from src.extraction.extract_entities import extract_entities
from src.extraction.create_relationships import create_relationships

from src.graph.build_graph import build_graph, get_graph_summary, save_graph_html, get_local_subgraph

from src.analytics.centrality import summarize_centrality

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

    print("Saving processed CSVs...")

    entities_path = processed_dir / "entities.csv"
    relationships_path = processed_dir / "relationships.csv"

    entities.to_csv(entities_path, index=False)
    relationships.to_csv(relationships_path, index=False)

    print("Building NetworkX graph...")

    graph = build_graph(
        entities_df=entities,
        relationships_df=relationships,
    )

    summary = get_graph_summary(graph)

    print("\n========== GRAPH SUMMARY ==========")
    print(f"Nodes: {summary['nodes']}")
    print(f"Edges: {summary['edges']}")

    print("\nNode Types")
    for node_type, count in summary["node_type_counts"].items():
        print(f"  {node_type}: {count}")

    print("\nRelationship Types")
    for rel, count in summary["relationship_type_counts"].items():
        print(f"  {rel}: {count}")

    print("\nSaving interactive graph...")

    local_graph = get_local_subgraph(
        graph,
        center_node="incident:INC-0001",
        radius=2,
    )

    save_graph_html(
        local_graph,
        output_dir / "local_incident_graph.html",
    )

    save_graph_html(
        graph,
        output_dir / "incident_graph.html",
    )

    print("\nPipeline complete!")

    print(f"\nEntities saved to:")
    print(entities_path)

    print(f"\nRelationships saved to:")
    print(relationships_path)

    print(f"\nGraph saved to:")
    print(output_dir / "incident_graph.html")

    print(f"\nLocal graph saved to:")
    print(output_dir / "local_incident_graph.html" )

    centrality_summary = summarize_centrality(graph, top_n=10)

    print("\nTop connected entities:")
    print(centrality_summary["top_degree"])

    print("\nTop bridge entities:")
    print(centrality_summary["top_betweenness"])

    centrality_summary["top_degree"].to_csv(
    output_dir / "top_central_entities.csv",
    index=False,
    )   

if __name__ == "__main__":
    main()