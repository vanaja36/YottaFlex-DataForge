
import pandas as pd

from src.config import CUSTOMER_COLUMNS, ORDER_COLUMNS


def get_required_columns(dataset: str) -> list:
    """Return the required columns for a supported dataset."""

    if dataset == "customers":
        return CUSTOMER_COLUMNS
    elif dataset == "orders":
        return ORDER_COLUMNS
    else:
        raise ValueError(f"Unsupported dataset: {dataset}")


def validate_columns(df: pd.DataFrame, dataset: str) -> None:
    """Check whether all required columns are present."""

    required = get_required_columns(dataset)

    missing = [column for column in required if column not in df.columns]

    if missing:
        raise ValueError(f"Missing required columns: {missing}")


def inspect_schema(df: pd.DataFrame, dataset: str) -> list:
    """Identify unexpected columns without rejecting the dataset."""

    expected = get_required_columns(dataset)

    unexpected = [
        column for column in df.columns
        if column not in expected
    ]

    return unexpected


def validate_records(df: pd.DataFrame, dataset: str):
    """Separate valid and rejected records with detailed reasons."""

    validate_columns(df, dataset)

    data = df.copy()
    errors = pd.Series("", index=data.index, dtype="object")

    def add_error(mask, message):
        mask = mask.fillna(False)
        errors.loc[mask] = errors.loc[mask].apply(
            lambda existing: f"{existing}; {message}" if existing else message
        )

    if dataset == "customers":

        required_columns = [
            "customer_id", "customer_name", "email",
            "city", "age", "updated_at"
        ]

        for column in required_columns:
            missing = (
                data[column].isna()
                | data[column].astype("string").str.strip().eq("").fillna(False)
            )
            add_error(missing, f"{column} is required")

        email = data["email"].astype("string").str.strip()

        add_error(
            email.notna()
            & email.ne("")
            & ~email.str.match(
                r"^[^@\s]+@[^@\s]+\.[^@\s]+$"
            ).fillna(False),
            "Invalid email"
        )

        age = pd.to_numeric(data["age"], errors="coerce")

        add_error(age.isna(), "Age must be numeric")

        add_error(
            age.notna() & ((age % 1) != 0),
            "Age must be a whole number"
        )

        add_error(
            age.notna() & ~age.between(1, 120),
            "Age must be between 1 and 120"
        )

        dates = pd.to_datetime(
            data["updated_at"], errors="coerce", utc=True
        )

        add_error(dates.isna(), "Invalid updated_at date")

        duplicate_ids = (
            data["customer_id"].notna()
            & data["customer_id"].duplicated(keep=False)
        )

        add_error(duplicate_ids, "Duplicate customer_id")

    elif dataset == "orders":

        required_columns = [
            "order_id", "customer_id", "product_name",
            "quantity", "unit_price", "order_date"
        ]

        for column in required_columns:
            missing = (
                data[column].isna()
                | data[column].astype("string").str.strip().eq("").fillna(False)
            )
            add_error(missing, f"{column} is required")

        quantity = pd.to_numeric(data["quantity"], errors="coerce")
        price = pd.to_numeric(data["unit_price"], errors="coerce")

        add_error(quantity.isna(), "Quantity must be numeric")

        add_error(
            quantity.notna() & ((quantity % 1) != 0),
            "Quantity must be a whole number"
        )

        add_error(
            quantity.notna() & (quantity <= 0),
            "Quantity must be positive"
        )

        add_error(price.isna(), "Unit price must be numeric")

        add_error(
            price.notna() & (price < 0),
            "Unit price cannot be negative"
        )

        dates = pd.to_datetime(data["order_date"], errors="coerce")

        add_error(dates.isna(), "Invalid order_date")

        duplicate_ids = (
            data["order_id"].notna()
            & data["order_id"].duplicated(keep=False)
        )

        add_error(duplicate_ids, "Duplicate order_id")

    valid_records = data.loc[errors == ""].copy()

    rejected_records = data.loc[errors != ""].copy()
    rejected_records["rejection_reason"] = errors.loc[errors != ""]

    return valid_records, rejected_records
