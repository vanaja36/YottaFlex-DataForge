
import sqlite3

import pytest


@pytest.fixture
def test_db(tmp_path):
    """Create an isolated temporary database for testing."""

    db_path = tmp_path / "test_flowforge.db"

    connection = sqlite3.connect(db_path)
    connection.execute("PRAGMA foreign_keys = ON")

    connection.executescript("""
        CREATE TABLE customers (
            customer_id TEXT PRIMARY KEY,
            customer_name TEXT NOT NULL,
            email TEXT NOT NULL,
            city TEXT NOT NULL,
            age INTEGER NOT NULL,
            updated_at TEXT NOT NULL
        );

        CREATE TABLE orders (
            order_id TEXT PRIMARY KEY,
            customer_id TEXT NOT NULL,
            product_name TEXT NOT NULL,
            quantity INTEGER NOT NULL,
            unit_price REAL NOT NULL,
            order_date TEXT NOT NULL,
            total_amount REAL NOT NULL,
            FOREIGN KEY (customer_id)
                REFERENCES customers(customer_id)
        );

        CREATE TABLE processed_files (
            file_id INTEGER PRIMARY KEY AUTOINCREMENT,
            dataset TEXT NOT NULL,
            source_file TEXT NOT NULL,
            content_hash TEXT NOT NULL,
            UNIQUE(dataset, content_hash)
        );
    """)

    yield connection

    connection.close()


def test_customer_primary_key(test_db):
    """Customer IDs must be unique."""

    test_db.execute("""
        INSERT INTO customers VALUES (
            'C001', 'Ravi', 'ravi@example.com',
            'Hyderabad', 25, '2026-11-10'
        )
    """)

    with pytest.raises(sqlite3.IntegrityError):
        test_db.execute("""
            INSERT INTO customers VALUES (
                'C001', 'Another Ravi', 'another@example.com',
                'Vijayawada', 30, '2026-11-10'
            )
        """)


def test_order_foreign_key(test_db):
    """Orders must reference an existing customer."""

    with pytest.raises(sqlite3.IntegrityError):
        test_db.execute("""
            INSERT INTO orders VALUES (
                'ORD001', 'UNKNOWN', 'Laptop',
                1, 50000, '2026-11-10', 50000
            )
        """)


def test_valid_order_insert(test_db):
    """An order referencing an existing customer should succeed."""

    test_db.execute("""
        INSERT INTO customers VALUES (
            'C001', 'Ravi', 'ravi@example.com',
            'Hyderabad', 25, '2026-11-10'
        )
    """)

    test_db.execute("""
        INSERT INTO orders VALUES (
            'ORD001', 'C001', 'Laptop',
            2, 50000, '2026-11-10', 100000
        )
    """)

    count = test_db.execute(
        "SELECT COUNT(*) FROM orders"
    ).fetchone()[0]

    assert count == 1


def test_processed_file_uniqueness(test_db):
    """The same dataset and content hash cannot be registered twice."""

    test_db.execute("""
        INSERT INTO processed_files (
            dataset, source_file, content_hash
        )
        VALUES ('customers', 'customers.csv', 'abc123')
    """)

    with pytest.raises(sqlite3.IntegrityError):
        test_db.execute("""
            INSERT INTO processed_files (
                dataset, source_file, content_hash
            )
            VALUES ('customers', 'customers.csv', 'abc123')
        """)
