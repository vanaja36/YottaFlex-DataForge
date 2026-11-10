import pandas as pd


def transform_records(df: pd.DataFrame, dataset: str) -> pd.DataFrame:
    """Standardize and transform validated records."""

    data = df.copy()

    if dataset == "customers":
        for column in ["customer_name", "email", "city"]:
            data[column] = data[column].astype("string").str.strip()

        data["email"] = data["email"].str.lower()
        data["age"] = pd.to_numeric(data["age"]).astype("int64")
        data["updated_at"] = pd.to_datetime(
            data["updated_at"], utc=True
        ).dt.strftime("%Y-%m-%dT%H:%M:%SZ")

    elif dataset == "orders":
        data["product_name"] = data["product_name"].astype("string").str.strip()
        data["quantity"] = pd.to_numeric(data["quantity"]).astype("int64")
        data["unit_price"] = pd.to_numeric(data["unit_price"]).astype("float64")
        data["order_date"] = pd.to_datetime(
            data["order_date"]
        ).dt.strftime("%Y-%m-%d")

        data["total_amount"] = (
            data["quantity"] * data["unit_price"]
        ).round(2)

    else:
        raise ValueError(f"Unsupported dataset: {dataset}")

    return data
