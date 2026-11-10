
import json
import sqlite3

import pandas as pd
import pytest

from src.pipeline import calculate_file_hash, save_rejections


def test_calculate_file_hash(tmp_path):
    """Same file content should produce the same hash."""

    file_path = tmp_path / "sample.csv"
    file_path.write_text("id,name\n1,Ravi\n", encoding="utf-8")

    first_hash = calculate_file_hash(file_path)
    second_hash = calculate_file_hash(file_path)

    assert first_hash == second_hash
    assert len(first_hash) == 64


def test_save_rejections_empty():
    """No rejected records should return zero."""

    rejected = pd.DataFrame()

    result = save_rejections(
        rejected,
        "customers",
        "customers.csv",
        "test-run-001"
    )

    assert result == 0


def test_save_rejections_batch(tmp_path, monkeypatch):
    """Rejected records should be inserted as a batch."""

    import src.pipeline as pipeline

    inserted_records = []

    class FakeConnection:
        def __enter__(self):
            return self

        def __exit__(self, exc_type, exc_value, traceback):
            return False

        def executemany(self, query, records):
            inserted_records.extend(records)

    monkeypatch.setattr(
        pipeline,
        "get_connection",
        lambda: FakeConnection()
    )

    rejected = pd.DataFrame([
        {
            "customer_id": "TEST101",
            "customer_name": "Invalid User",
            "email": "wrong-email",
            "city": "Hyderabad",
            "age": 25,
            "updated_at": "2026-11-10",
            "rejection_reason": "Invalid email"
        },
        {
            "customer_id": "TEST102",
            "customer_name": "Another User",
            "email": "another-wrong-email",
            "city": "Hyderabad",
            "age": 30,
            "updated_at": "2026-11-10",
            "rejection_reason": "Invalid email"
        }
    ])

    result = save_rejections(
        rejected,
        "customers",
        "customers.csv",
        "test-run-001"
    )

    assert result == 2
    assert len(inserted_records) == 2
    assert inserted_records[0][0] == "customers"
    assert inserted_records[0][3] == "test-run-001"

    original_record = json.loads(inserted_records[0][5])
    assert original_record["customer_id"] == "TEST101"


def test_pipeline_transaction_rollback(tmp_path, monkeypatch):
    """Verify that a pipeline failure rolls back database writes."""

    import src.pipeline as pipeline

    # Create a temporary input directory.
    input_dir = tmp_path / "input"
    input_dir.mkdir()

    customer_file = input_dir / "customers.csv"

    pd.DataFrame([{
        "customer_id": "CUST_TEST_001",
        "customer_name": "Test User",
        "email": "test@example.com",
        "city": "Hyderabad",
        "age": 25,
        "updated_at": "2026-11-10"
    }]).to_csv(customer_file, index=False)

    # Create an isolated temporary database.
    database_path = tmp_path / "test.db"

    def temporary_connection():
        connection = sqlite3.connect(database_path)
        connection.execute("PRAGMA foreign_keys = ON")
        return connection

    with temporary_connection() as connection:
        connection.executescript("""
            CREATE TABLE customers (
                customer_id TEXT PRIMARY KEY,
                customer_name TEXT NOT NULL,
                email TEXT NOT NULL,
                city TEXT NOT NULL,
                age INTEGER NOT NULL,
                updated_at TEXT NOT NULL
            );

            CREATE TABLE processed_files (
                file_id INTEGER PRIMARY KEY AUTOINCREMENT,
                dataset TEXT NOT NULL,
                source_file TEXT NOT NULL,
                content_hash TEXT NOT NULL,
                processed_at TEXT DEFAULT CURRENT_TIMESTAMP,
                UNIQUE(dataset, content_hash)
            );

            CREATE TABLE rejected_records (
                rejection_id INTEGER PRIMARY KEY AUTOINCREMENT,
                dataset TEXT NOT NULL,
                source_file TEXT,
                source_row_number INTEGER,
                run_id TEXT,
                rejection_reason TEXT NOT NULL,
                original_record TEXT NOT NULL,
                rejected_at TEXT DEFAULT CURRENT_TIMESTAMP
            );

            CREATE TABLE pipeline_runs (
                run_id TEXT PRIMARY KEY,
                dataset TEXT NOT NULL,
                status TEXT NOT NULL,
                total_records INTEGER DEFAULT 0,
                valid_records INTEGER DEFAULT 0,
                rejected_records INTEGER DEFAULT 0,
                started_at TEXT NOT NULL,
                completed_at TEXT
            );
        """)

    # Redirect the pipeline to temporary resources.
    monkeypatch.setattr(pipeline, "INPUT_DIR", input_dir)
    monkeypatch.setattr(
        pipeline,
        "get_connection",
        temporary_connection
    )

    # Simulate failure while saving rejected records.
    def failing_save_rejections(*args, **kwargs):
        raise RuntimeError("Simulated rejection storage failure")

    monkeypatch.setattr(
        pipeline,
        "save_rejections",
        failing_save_rejections
    )

    # The pipeline should fail.
    with pytest.raises(
        RuntimeError,
        match="Simulated rejection storage failure"
    ):
        pipeline.run_dataset("customers")

    # Verify that the transaction rolled back.
    with temporary_connection() as connection:
        customer_count = connection.execute(
            "SELECT COUNT(*) FROM customers"
        ).fetchone()[0]

        processed_count = connection.execute(
            "SELECT COUNT(*) FROM processed_files"
        ).fetchone()[0]

        failed_count = connection.execute(
            "SELECT COUNT(*) FROM pipeline_runs WHERE status = 'FAILED'"
        ).fetchone()[0]

    assert customer_count == 0
    assert processed_count == 0
    assert failed_count == 1
def test_pipeline_recovers_after_failure(tmp_path, monkeypatch):
    """A failed batch should be safely retryable."""

    import src.pipeline as pipeline

    input_dir = tmp_path / "input"
    input_dir.mkdir()

    customer_file = input_dir / "customers.csv"

    pd.DataFrame([{
        "customer_id": "CUST_RETRY_001",
        "customer_name": "Retry User",
        "email": "retry@example.com",
        "city": "Hyderabad",
        "age": 25,
        "updated_at": "2026-11-10"
    }]).to_csv(customer_file, index=False)

    database_path = tmp_path / "retry_test.db"

    def temporary_connection():
        connection = sqlite3.connect(database_path)
        connection.execute("PRAGMA foreign_keys = ON")
        return connection

    with temporary_connection() as connection:
        connection.executescript("""
            CREATE TABLE customers (
                customer_id TEXT PRIMARY KEY,
                customer_name TEXT NOT NULL,
                email TEXT NOT NULL,
                city TEXT NOT NULL,
                age INTEGER NOT NULL,
                updated_at TEXT NOT NULL
            );

            CREATE TABLE processed_files (
                file_id INTEGER PRIMARY KEY AUTOINCREMENT,
                dataset TEXT NOT NULL,
                source_file TEXT NOT NULL,
                content_hash TEXT NOT NULL,
                processed_at TEXT DEFAULT CURRENT_TIMESTAMP,
                UNIQUE(dataset, content_hash)
            );

            CREATE TABLE rejected_records (
                rejection_id INTEGER PRIMARY KEY AUTOINCREMENT,
                dataset TEXT NOT NULL,
                source_file TEXT,
                source_row_number INTEGER,
                run_id TEXT,
                rejection_reason TEXT NOT NULL,
                original_record TEXT NOT NULL,
                rejected_at TEXT DEFAULT CURRENT_TIMESTAMP
            );

            CREATE TABLE pipeline_runs (
                run_id TEXT PRIMARY KEY,
                dataset TEXT NOT NULL,
                status TEXT NOT NULL,
                total_records INTEGER DEFAULT 0,
                valid_records INTEGER DEFAULT 0,
                rejected_records INTEGER DEFAULT 0,
                started_at TEXT NOT NULL,
                completed_at TEXT
            );
        """)

    monkeypatch.setattr(pipeline, "INPUT_DIR", input_dir)
    monkeypatch.setattr(
        pipeline,
        "get_connection",
        temporary_connection
    )

    original_save = pipeline.save_rejections

    def failing_save(*args, **kwargs):
        raise RuntimeError("Temporary failure")

    monkeypatch.setattr(
        pipeline,
        "save_rejections",
        failing_save
    )

    # First attempt must fail.
    with pytest.raises(RuntimeError, match="Temporary failure"):
        pipeline.run_dataset("customers")

    # Restore normal rejection saving.
    monkeypatch.setattr(
        pipeline,
        "save_rejections",
        original_save
    )

    # Retry the same file.
    result = pipeline.run_dataset("customers")

    assert result["valid_records"] == 1
    assert result["rejected_records"] == 0

    with temporary_connection() as connection:
        customer_count = connection.execute(
            "SELECT COUNT(*) FROM customers"
        ).fetchone()[0]

        processed_count = connection.execute(
            "SELECT COUNT(*) FROM processed_files"
        ).fetchone()[0]

        failed_count = connection.execute(
            "SELECT COUNT(*) FROM pipeline_runs WHERE status='FAILED'"
        ).fetchone()[0]

        success_count = connection.execute(
            "SELECT COUNT(*) FROM pipeline_runs WHERE status='SUCCESS'"
        ).fetchone()[0]

    assert customer_count == 1
    assert processed_count == 1
    assert failed_count == 1
    assert success_count == 1