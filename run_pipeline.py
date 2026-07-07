from pathlib import Path
from src.ingestion.csv_loader import load_and_normalize


def main():
    data_dir = Path("data/raw")

    datasets = load_and_normalize(data_dir)

    for name, df in datasets.items():
        print(f"\n{name.upper()}")
        print(df.head())
        print(df.shape)


if __name__ == "__main__":
    main()