from pathlib import Path
import pandas as pd

from src.config import INPUT_DIR
from src.database import get_connection, initialize_database


def get_source_count(dataset):
    """Return the number of data rows in the source CSV."""

    file_path = INPUT_DIR / f"{dataset}.csv"

    if not file_path.exists():
        raise FileNotFoundError(f"Source file not found: {file_path}")

    return len(pd.read_csv(file_path))


def run_reconciliation():
    """Compare source counts with database counts."""

    initialize_database()

    source_counts = {
        "customers": get_source_count("customers"),
        "orders": get_source_count("orders"),
    }

    with get_connection() as connection:

        customer_count = connection.execute(
            "SELECT COUNT(*) FROM customers"
        ).fetchone()[0]

        order_count = connection.execute(
            "SELECT COUNT(*) FROM orders"
        ).fetchone()[0]

        rejected_count = connection.execute(
            "SELECT COUNT(*) FROM rejected_records"
        ).fetchone()[0]

        invalid_fk_count = connection.execute("""
            SELECT COUNT(*)
            FROM orders o
            LEFT JOIN customers c
                ON o.customer_id = c.customer_id
            WHERE c.customer_id IS NULL
        """).fetchone()[0]

        processed_file_count = connection.execute(
            "SELECT COUNT(*) FROM processed_files"
        ).fetchone()[0]

        run_summary = connection.execute("""
            SELECT dataset, status, COUNT(*)
            FROM pipeline_runs
            GROUP BY dataset, status
            ORDER BY dataset, status
        """).fetchall()

    print("\n========== FLOWFORGE RECONCILIATION ==========")

    print("\nSource vs Database Counts:")

    print(
        f"Customers: Source={source_counts['customers']:,} | "
        f"Database={customer_count:,} | "
        f"{'PASS' if source_counts['customers'] == customer_count else 'FAIL'}"
    )

    print(
        f"Orders: Source={source_counts['orders']:,} | "
        f"Database={order_count:,} | "
        f"{'PASS' if source_counts['orders'] == order_count else 'FAIL'}"
    )

    print(f"\nRejected records        : {rejected_count:,}")
    print(f"Invalid order references: {invalid_fk_count:,}")
    print(f"Processed files         : {processed_file_count:,}")

    print("\nPipeline Run Summary:")

    for dataset, status, count in run_summary:
        print(f"{dataset} | {status} | {count}")

    print("\nFinal Checks:")

    checks = {
        "Customer count reconciliation":
            source_counts["customers"] == customer_count,
        "Order count reconciliation":
            source_counts["orders"] == order_count,
        "Foreign key integrity":
            invalid_fk_count == 0,
    }

    for check, passed in checks.items():
        print(f"{check}: {'PASS' if passed else 'FAIL'}")

    overall = all(checks.values())

    print(
        "\nOverall Result:",
        "PASS" if overall else "FAIL"
    )

    print("===============================================")


if __name__ == "__main__":
    run_reconciliation()