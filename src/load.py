
import sqlite3
import pandas as pd

from src.database import get_connection


def load_records(
    df: pd.DataFrame,
    dataset: str,
    connection: sqlite3.Connection | None = None
) -> int:
    """Load records using an upsert transaction.

    An existing connection can be supplied to participate
    in a larger transaction.
    """

    if dataset not in {"customers", "orders"}:
        raise ValueError(f"Unsupported dataset: {dataset}")

    if df.empty:
        return 0

    table_columns = {
        "customers": [
            "customer_id",
            "customer_name",
            "email",
            "city",
            "age",
            "updated_at"
        ],
        "orders": [
            "order_id",
            "customer_id",
            "product_name",
            "quantity",
            "unit_price",
            "order_date",
            "total_amount"
        ],
    }

    columns = table_columns[dataset]

    missing = [
        column for column in columns
        if column not in df.columns
    ]

    if missing:
        raise ValueError(
            f"Missing loading columns: {missing}"
        )

    primary_key = {
        "customers": "customer_id",
        "orders": "order_id",
    }[dataset]

    placeholders = ", ".join(["?"] * len(columns))
    column_names = ", ".join(columns)

    update_columns = [
        column for column in columns
        if column != primary_key
    ]

    update_clause = ", ".join(
        f"{column} = excluded.{column}"
        for column in update_columns
    )

    query = (
        f"INSERT INTO {dataset} ({column_names}) "
        f"VALUES ({placeholders}) "
        f"ON CONFLICT({primary_key}) DO UPDATE SET "
        f"{update_clause}"
    )

    values = [
        tuple(row[column] for column in columns)
        for row in df[columns].to_dict(orient="records")
    ]

    def execute_load(conn):
        conn.executemany(query, values)

    try:
        if connection is not None:
            execute_load(connection)
        else:
            with get_connection() as conn:
                execute_load(conn)

    except sqlite3.IntegrityError as exc:
        raise ValueError(
            f"Database integrity error while loading "
            f"{dataset}: {exc}"
        ) from exc

    return len(values)
