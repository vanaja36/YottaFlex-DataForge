import pandas as pd
import pytest

from src.extract import extract_csv


def test_extract_valid_csv(tmp_path):
    file_path = tmp_path / "customers.csv"
    file_path.write_text(
        "customer_id,customer_name\nCUST001,Ravi\n",
        encoding="utf-8"
    )

    result = extract_csv(file_path)

    assert len(result) == 1
    assert result.iloc[0]["customer_id"] == "CUST001"


def test_extract_missing_file(tmp_path):
    file_path = tmp_path / "missing.csv"

    with pytest.raises(FileNotFoundError):
        extract_csv(file_path)


def test_extract_unsupported_format(tmp_path):
    file_path = tmp_path / "customers.txt"
    file_path.write_text("sample data", encoding="utf-8")

    with pytest.raises(ValueError, match="Unsupported file format"):
        extract_csv(file_path)


def test_extract_empty_csv(tmp_path):
    file_path = tmp_path / "empty.csv"
    file_path.write_text("", encoding="utf-8")

    with pytest.raises(ValueError, match="CSV file is empty"):
        extract_csv(file_path)

def test_extract_malformed_csv(tmp_path):
    file_path = tmp_path / "malformed.csv"
    file_path.write_text(
        'customer_id,customer_name\n"CUST001,"Ravi\n',
        encoding="utf-8"
    )

    with pytest.raises(ValueError, match="Unable to parse CSV file"):
        extract_csv(file_path)
def test_extract_header_only_csv(tmp_path):
    """A CSV with headers but no data should return an empty DataFrame."""

    file_path = tmp_path / "header_only.csv"
    file_path.write_text(
        "customer_id,customer_name\n",
        encoding="utf-8"
    )

    result = extract_csv(file_path)

    assert result.empty
    assert list(result.columns) == ["customer_id", "customer_name"]