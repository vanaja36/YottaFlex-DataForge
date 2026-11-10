
import pandas as pd
import pytest

from src.validate import validate_records, validate_columns


def test_customer_validation_counts():
    """Check valid and rejected customer records."""

    data = pd.DataFrame([
        {
            "customer_id": "TEST001",
            "customer_name": "Ravi",
            "email": "ravi@example.com",
            "city": "Hyderabad",
            "age": 25,
            "updated_at": "2026-11-10"
        },
        {
            "customer_id": "TEST002",
            "customer_name": "Invalid Email",
            "email": "invalid-email",
            "city": "Hyderabad",
            "age": 30,
            "updated_at": "2026-11-10"
        },
        {
            "customer_id": "TEST003",
            "customer_name": "Invalid Age",
            "email": "age@example.com",
            "city": "Hyderabad",
            "age": 150,
            "updated_at": "2026-11-10"
        },
        {
            "customer_id": "TEST004",
            "customer_name": "Missing City",
            "email": "city@example.com",
            "city": " ",
            "age": 28,
            "updated_at": "2026-11-10"
        },
        {
            "customer_id": "TEST005",
            "customer_name": "Duplicate One",
            "email": "one@example.com",
            "city": "Hyderabad",
            "age": 32,
            "updated_at": "2026-11-10"
        },
        {
            "customer_id": "TEST005",
            "customer_name": "Duplicate Two",
            "email": "two@example.com",
            "city": "Hyderabad",
            "age": 35,
            "updated_at": "2026-11-10"
        }
    ])

    valid, rejected = validate_records(data, "customers")

    assert len(valid) == 1
    assert len(rejected) == 5
    assert valid.iloc[0]["customer_id"] == "TEST001"

    reasons = rejected["rejection_reason"].tolist()

    assert "Invalid email" in reasons
    assert "Age must be between 1 and 120" in reasons
    assert "city is required" in reasons
    assert reasons.count("Duplicate customer_id") == 2


def test_order_validation_counts():
    """Check valid and rejected order records."""

    data = pd.DataFrame([
        {
            "order_id": "ORD001",
            "customer_id": "CUST0000001",
            "product_name": "Laptop",
            "quantity": 2,
            "unit_price": 50000,
            "order_date": "2026-11-10"
        },
        {
            "order_id": "ORD002",
            "customer_id": "CUST0000001",
            "product_name": "Mobile",
            "quantity": 0,
            "unit_price": 20000,
            "order_date": "2026-11-10"
        },
        {
            "order_id": "ORD003",
            "customer_id": "CUST0000001",
            "product_name": "Tablet",
            "quantity": 1,
            "unit_price": -500,
            "order_date": "2026-11-10"
        },
        {
            "order_id": "ORD004",
            "customer_id": "CUST0000001",
            "product_name": "Keyboard",
            "quantity": 1.5,
            "unit_price": 1000,
            "order_date": "2026-11-10"
        },
        {
            "order_id": "ORD005",
            "customer_id": "CUST0000001",
            "product_name": "Monitor",
            "quantity": 1,
            "unit_price": 15000,
            "order_date": "invalid-date"
        }
    ])

    valid, rejected = validate_records(data, "orders")

    assert len(valid) == 1
    assert len(rejected) == 4
    assert valid.iloc[0]["order_id"] == "ORD001"

    reasons = rejected["rejection_reason"].tolist()

    assert "Quantity must be positive" in reasons
    assert "Unit price cannot be negative" in reasons
    assert "Quantity must be a whole number" in reasons
    assert "Invalid order_date" in reasons


def test_missing_required_columns():
    """Check that missing required columns raise an error."""

    data = pd.DataFrame([
        {
            "customer_id": "TEST006",
            "customer_name": "Test User"
        }
    ])

    with pytest.raises(ValueError, match="Missing required columns"):
        validate_records(data, "customers")


def test_unsupported_dataset():
    """Check that unsupported datasets are rejected."""

    data = pd.DataFrame()

    with pytest.raises(ValueError, match="Unsupported dataset"):
        validate_columns(data, "products")
def test_null_values_are_rejected():
    """Check that null required fields are rejected."""

    customers = pd.DataFrame([{
        "customer_id": "TEST010",
        "customer_name": None,
        "email": "test@example.com",
        "city": "Hyderabad",
        "age": 25,
        "updated_at": "2026-11-10"
    }])

    orders = pd.DataFrame([{
        "order_id": "ORD010",
        "customer_id": "CUST0000001",
        "product_name": None,
        "quantity": 2,
        "unit_price": 500,
        "order_date": "2026-11-10"
    }])

    valid_customers, rejected_customers = validate_records(
        customers, "customers"
    )

    valid_orders, rejected_orders = validate_records(
        orders, "orders"
    )

    assert len(valid_customers) == 0
    assert len(rejected_customers) == 1
    assert "customer_name is required" in rejected_customers.iloc[0]["rejection_reason"]

    assert len(valid_orders) == 0
    assert len(rejected_orders) == 1
    assert "product_name is required" in rejected_orders.iloc[0]["rejection_reason"]

def test_unexpected_columns_are_detected():
    """Check that extra columns are identified without rejecting data."""

    from src.validate import inspect_schema

    data = pd.DataFrame([{
        "customer_id": "TEST020",
        "customer_name": "Ravi",
        "email": "ravi@example.com",
        "city": "Hyderabad",
        "age": 25,
        "updated_at": "2026-11-10",
        "unexpected_field": "extra data"
    }])

    unexpected = inspect_schema(data, "customers")

    assert unexpected == ["unexpected_field"]

def test_unexpected_columns_are_detected():
    """Check that extra columns are identified without rejecting data."""

    from src.validate import inspect_schema

    data = pd.DataFrame([{
        "customer_id": "TEST020",
        "customer_name": "Ravi",
        "email": "ravi@example.com",
        "city": "Hyderabad",
        "age": 25,
        "updated_at": "2026-11-10",
        "unexpected_field": "extra data"
    }])

    unexpected = inspect_schema(data, "customers")

    assert unexpected == ["unexpected_field"]