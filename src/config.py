from pathlib import Path

# Project directories
BASE_DIR = Path(__file__).resolve().parent.parent
DATA_DIR = BASE_DIR / "data"
INPUT_DIR = DATA_DIR / "input"
OUTPUT_DIR = DATA_DIR / "output"
REJECTED_DIR = DATA_DIR / "rejected"
REPORTS_DIR = BASE_DIR / "reports"

# Database configuration
DATABASE_PATH = OUTPUT_DIR / "flowforge.db"

# Supported datasets
CUSTOMERS_DATASET = "customers"
ORDERS_DATASET = "orders"

# Required customer columns
CUSTOMER_COLUMNS = [
    "customer_id",
    "customer_name",
    "email",
    "city",
    "age",
    "updated_at",
]

# Required order columns
ORDER_COLUMNS = [
    "order_id",
    "customer_id",
    "product_name",
    "quantity",
    "unit_price",
    "order_date",
]

# Pipeline settings
SUPPORTED_DATASETS = [
    CUSTOMERS_DATASET,
    ORDERS_DATASET,
]

