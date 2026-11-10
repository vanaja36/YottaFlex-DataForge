
import hashlib
import json
import uuid
import time
from datetime import datetime, timezone

import pandas as pd

from src.config import INPUT_DIR
from src.database import get_connection, initialize_database
from src.extract import extract_csv
from src.validate import validate_records, inspect_schema
from src.transform import transform_records
from src.load import load_records
from src.logger import get_logger
from src.metrics import PipelineMetrics


logger = get_logger()


def calculate_file_hash(file_path):
    """Generate a SHA-256 hash for an input file."""

    sha256 = hashlib.sha256()

    with open(file_path, "rb") as file:
        for chunk in iter(lambda: file.read(1024 * 1024), b""):
            sha256.update(chunk)

    return sha256.hexdigest()


def save_rejections(
    rejected,
    dataset,
    source_file,
    run_id,
    connection=None
):
    """Save rejected records using a supplied or new connection."""

    if rejected.empty:
        return 0

    records = []

    for index, row in rejected.iterrows():
        original = row.drop(
            labels=["rejection_reason"]
        ).to_dict()

        records.append((
            dataset,
            source_file,
            int(index) + 2,
            run_id,
            row["rejection_reason"],
            json.dumps(original, default=str)
        ))

    query = """
        INSERT INTO rejected_records (
            dataset,
            source_file,
            source_row_number,
            run_id,
            rejection_reason,
            original_record
        )
        VALUES (?, ?, ?, ?, ?, ?)
    """

    if connection is not None:
        connection.executemany(query, records)
    else:
        with get_connection() as conn:
            conn.executemany(query, records)

    return len(records)


def run_dataset(dataset):
    """Extract, validate, transform and load one dataset."""

    file_path = INPUT_DIR / f"{dataset}.csv"
    run_id = str(uuid.uuid4())
    started_at = datetime.now(timezone.utc).isoformat()

    metrics = PipelineMetrics(dataset=dataset)
    start_time = time.perf_counter()

    logger.info("Starting %s pipeline", dataset)

    try:
        if not file_path.exists():
            raise FileNotFoundError(
                f"Input file not found: {file_path}"
            )

        # Step 1: Calculate the input file hash.
        content_hash = calculate_file_hash(file_path)

        # Step 2: Check whether the file was already processed.
        with get_connection() as connection:
            already_processed = connection.execute(
                """
                SELECT 1
                FROM processed_files
                WHERE dataset = ? AND content_hash = ?
                """,
                (dataset, content_hash)
            ).fetchone()

        if already_processed:
            logger.info(
                "%s file already processed. Skipping.",
                dataset
            )

            return {
                "dataset": dataset,
                "status": "SKIPPED"
            }

        # Step 3: Extract data.
        df = extract_csv(file_path)
        df.index = range(len(df))

        metrics.total_records = len(df)

        logger.info(
            "%s extraction completed: %s records",
            dataset,
            metrics.total_records
        )

        # Step 4: Inspect schema for unexpected columns.
        unexpected_columns = inspect_schema(df, dataset)

        if unexpected_columns:
            logger.warning(
                "Unexpected columns detected in %s: %s",
                dataset,
                unexpected_columns
            )

        # Step 5: Handle a valid empty batch.
        if df.empty:
            logger.warning(
                "%s contains no data records. Processing as an empty batch.",
                dataset
            )

            metrics.calculate_performance(start_time)

            completed_at = datetime.now(
                timezone.utc
            ).isoformat()

            with get_connection() as connection:

                # Recheck idempotency before registering the empty batch.
                already_processed = connection.execute(
                    """
                    SELECT 1
                    FROM processed_files
                    WHERE dataset = ? AND content_hash = ?
                    """,
                    (dataset, content_hash)
                ).fetchone()

                if already_processed:
                    return {
                        "dataset": dataset,
                        "status": "SKIPPED"
                    }

                connection.execute(
                    """
                    INSERT INTO processed_files (
                        dataset,
                        source_file,
                        content_hash
                    )
                    VALUES (?, ?, ?)
                    """,
                    (
                        dataset,
                        file_path.name,
                        content_hash
                    )
                )

                connection.execute(
                    """
                    INSERT INTO pipeline_runs (
                        run_id,
                        dataset,
                        status,
                        total_records,
                        valid_records,
                        rejected_records,
                        started_at,
                        completed_at
                    )
                    VALUES (?, ?, ?, ?, ?, ?, ?, ?)
                    """,
                    (
                        run_id,
                        dataset,
                        "SUCCESS",
                        0,
                        0,
                        0,
                        started_at,
                        completed_at
                    )
                )

            logger.info(
                "%s empty batch completed successfully.",
                dataset
            )

            return metrics.to_dict()

        # Step 6: Validate records.
        valid, rejected = validate_records(df, dataset)

        # Step 7: Transform valid records.
        transformed = transform_records(valid, dataset)

        # Step 8: Start one transaction for database operations.
        with get_connection() as connection:

            # Recheck idempotency before writing.
            already_processed = connection.execute(
                """
                SELECT 1
                FROM processed_files
                WHERE dataset = ? AND content_hash = ?
                """,
                (dataset, content_hash)
            ).fetchone()

            if already_processed:
                logger.info(
                    "%s file was processed by another run. Skipping.",
                    dataset
                )

                return {
                    "dataset": dataset,
                    "status": "SKIPPED"
                }

            # Step 9: Check order customer references.
            if dataset == "orders" and not valid.empty:

                existing_customers = {
                    row[0]
                    for row in connection.execute(
                        "SELECT customer_id FROM customers"
                    )
                }

                missing_customers = ~valid[
                    "customer_id"
                ].isin(existing_customers)

                invalid_orders = valid.loc[
                    missing_customers
                ].copy()

                invalid_orders["rejection_reason"] = (
                    "Referenced customer_id does not exist"
                )

                valid = valid.loc[
                    ~missing_customers
                ].copy()

                rejected = pd.concat(
                    [rejected, invalid_orders],
                    ignore_index=False
                )

                # Transform again after removing invalid orders.
                transformed = transform_records(
                    valid,
                    dataset
                )

            metrics.valid_records = len(valid)
            metrics.rejected_records = len(rejected)

            logger.info(
                "%s validation completed | Valid: %s | Rejected: %s",
                dataset,
                metrics.valid_records,
                metrics.rejected_records
            )

            # Step 10: Load valid records using the same connection.
            loaded_count = load_records(
                transformed,
                dataset,
                connection=connection
            )

            # Step 11: Save rejected records in the same transaction.
            rejected_count = save_rejections(
                rejected,
                dataset,
                file_path.name,
                run_id,
                connection
            )

            # Step 12: Register the processed file.
            connection.execute(
                """
                INSERT INTO processed_files (
                    dataset,
                    source_file,
                    content_hash
                )
                VALUES (?, ?, ?)
                """,
                (
                    dataset,
                    file_path.name,
                    content_hash
                )
            )

            # Step 13: Calculate performance metrics.
            metrics.calculate_performance(start_time)

            completed_at = datetime.now(
                timezone.utc
            ).isoformat()

            # Step 14: Save successful pipeline run.
            connection.execute(
                """
                INSERT INTO pipeline_runs (
                    run_id,
                    dataset,
                    status,
                    total_records,
                    valid_records,
                    rejected_records,
                    started_at,
                    completed_at
                )
                VALUES (?, ?, ?, ?, ?, ?, ?, ?)
                """,
                (
                    run_id,
                    dataset,
                    "SUCCESS",
                    metrics.total_records,
                    metrics.valid_records,
                    metrics.rejected_records,
                    started_at,
                    completed_at
                )
            )

        # Transaction commits when the connection context exits.
        logger.info(
            "%s completed | Total: %s | Upserted: %s | "
            "Rejected: %s | Duration: %.4f seconds | "
            "Throughput: %.2f records/second",
            dataset,
            metrics.total_records,
            loaded_count,
            rejected_count,
            metrics.duration_seconds,
            metrics.records_per_second
        )

        return metrics.to_dict()

    except Exception:
        logger.exception("%s pipeline failed", dataset)

        # Record failure separately after the main transaction rolls back.
        try:
            with get_connection() as connection:
                connection.execute(
                    """
                    INSERT INTO pipeline_runs (
                        run_id,
                        dataset,
                        status,
                        total_records,
                        valid_records,
                        rejected_records,
                        started_at,
                        completed_at
                    )
                    VALUES (?, ?, ?, ?, ?, ?, ?, ?)
                    """,
                    (
                        run_id,
                        dataset,
                        "FAILED",
                        metrics.total_records,
                        metrics.valid_records,
                        metrics.rejected_records,
                        started_at,
                        datetime.now(
                            timezone.utc
                        ).isoformat()
                    )
                )
        except Exception:
            logger.exception(
                "Unable to record failed pipeline run"
            )

        raise


def run_pipeline():
    """Run customers first, followed by orders."""

    initialize_database()

    results = []

    for dataset in ["customers", "orders"]:
        results.append(run_dataset(dataset))

    print("\n========== FLOWFORGE PIPELINE SUMMARY ==========")

    for result in results:
        print(result)

    print("================================================")


if __name__ == "__main__":
    run_pipeline()
