import pandas as pd
from pathlib import Path


def extract_csv(file_path: Path) -> pd.DataFrame:
    """
    Read a CSV file and return its contents as a DataFrame.
    """
    file_path = Path(file_path)

    if not file_path.exists():
        raise FileNotFoundError(f"Input file not found: {file_path}")

    if file_path.suffix.lower() != ".csv":
        raise ValueError(f"Unsupported file format: {file_path.suffix}")

    try:
        return pd.read_csv(file_path, engine="python")
    except pd.errors.EmptyDataError as exc:
        raise ValueError(f"CSV file is empty: {file_path}") from exc
    except pd.errors.ParserError as exc:
        raise ValueError(f"Unable to parse CSV file: {file_path}") from exc
