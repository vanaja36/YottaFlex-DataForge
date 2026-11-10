import sqlite3
from src.config import DATABASE_PATH, OUTPUT_DIR


def get_connection():
    """Create a database connection with foreign keys enabled."""

    OUTPUT_DIR.mkdir(parents=True, exist_ok=True)

    connection = sqlite3.connect(DATABASE_PATH)
    connection.execute("PRAGMA foreign_keys = ON")
    connection.execute("PRAGMA journal_mode = WAL")

    return connection


def initialize_database():
    """Create all FlowForge database tables."""

    with get_connection() as connection:

        connection.execute("""
            CREATE TABLE IF NOT EXISTS customers (
                customer_id TEXT PRIMARY KEY,
                customer_name TEXT NOT NULL,
                email TEXT NOT NULL,
                city TEXT NOT NULL,
                age INTEGER NOT NULL,
                updated_at TEXT NOT NULL
            )
        """)

        connection.execute("""
            CREATE TABLE IF NOT EXISTS orders (
                order_id TEXT PRIMARY KEY,
                customer_id TEXT NOT NULL,
                product_name TEXT NOT NULL,
                quantity INTEGER NOT NULL,
                unit_price REAL NOT NULL,
                order_date TEXT NOT NULL,
                total_amount REAL NOT NULL,
                FOREIGN KEY (customer_id)
                    REFERENCES customers(customer_id)
            )
        """)

        connection.execute("""
            CREATE TABLE IF NOT EXISTS rejected_records (
                rejection_id INTEGER PRIMARY KEY AUTOINCREMENT,
                dataset TEXT NOT NULL,
                source_file TEXT,
                source_row_number INTEGER,
                run_id TEXT,
                rejection_reason TEXT NOT NULL,
                original_record TEXT NOT NULL,
                rejected_at TEXT DEFAULT CURRENT_TIMESTAMP
            )
        """)

        connection.execute("""
            CREATE TABLE IF NOT EXISTS pipeline_runs (
                run_id TEXT PRIMARY KEY,
                dataset TEXT NOT NULL,
                status TEXT NOT NULL,
                total_records INTEGER DEFAULT 0,
                valid_records INTEGER DEFAULT 0,
                rejected_records INTEGER DEFAULT 0,
                started_at TEXT NOT NULL,
                completed_at TEXT
            )
        """)

        connection.execute("""
            CREATE TABLE IF NOT EXISTS processed_files (
                file_id INTEGER PRIMARY KEY AUTOINCREMENT,
                dataset TEXT NOT NULL,
                source_file TEXT NOT NULL,
                content_hash TEXT NOT NULL,
                processed_at TEXT DEFAULT CURRENT_TIMESTAMP,
                UNIQUE(dataset, content_hash)
            )
        """)


if __name__ == "__main__":
    initialize_database()
    print("FlowForge database initialized successfully!")
