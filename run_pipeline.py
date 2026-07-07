from pathlib import Path

from src.ingestion.csv_loader import load_and_normalize
from src.extraction.extract_entities import extract_entities
from src.extraction.create_relationships import create_relationships



def main():
    data_dir = Path("data/raw")
    processed_dir = Path("data/processed")
    processed_dir.mkdir(parents=True, exist_ok=True)

    datasets = load_and_normalize(data_dir)

    entities = extract_entities(datasets)
    relationships = create_relationships(datasets)

    entities.to_csv(processed_dir / "entities.csv", index=False)
    relationships.to_csv(processed_dir / "relationships.csv", index=False)

    print("Extraction complete.")
    print(f"Entities: {len(entities)}")
    print(f"Relationships: {len(relationships)}")

    print("\nSample entities:")
    print(entities.head())

    print("\nSample relationships:")
    print(relationships.head())


if __name__ == "__main__":
    main()