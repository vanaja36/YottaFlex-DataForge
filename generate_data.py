
import argparse
import random

import pandas as pd
from faker import Faker

from src.config import INPUT_DIR

SEED = 42
CHUNK_SIZE = 10_000

PRODUCTS = [
    "Laptop", "Mobile", "Headphones", "Keyboard",
    "Monitor", "Mouse", "Tablet", "Smartwatch"
]


def generate_customers(count, fake):
    for start in range(1, count + 1, CHUNK_SIZE):
        end = min(start + CHUNK_SIZE, count + 1)

        records = []
        for i in range(start, end):
            records.append({
                "customer_id": f"CUST{i:07d}",
                "customer_name": fake.name(),
                "email": f"customer{i}@example.com",
                "city": fake.city(),
                "age": random.randint(18, 85),
                "updated_at": fake.date_time_between(
                    start_date="-2y", end_date="now"
                ).isoformat()
            })

        yield pd.DataFrame(records)


def generate_orders(count, customer_count, fake):
    for start in range(1, count + 1, CHUNK_SIZE):
        end = min(start + CHUNK_SIZE, count + 1)

        records = []
        for i in range(start, end):
            records.append({
                "order_id": f"ORD{i:09d}",
                "customer_id": (
                    f"CUST{random.randint(1, customer_count):07d}"
                ),
                "product_name": random.choice(PRODUCTS),
                "quantity": random.randint(1, 10),
                "unit_price": round(random.uniform(100, 100000), 2),
                "order_date": fake.date_between(
                    start_date="-2y", end_date="today"
                ).isoformat()
            })

        yield pd.DataFrame(records)


def write_chunks(chunks, output_path):
    first_chunk = True
    total = 0

    for chunk in chunks:
        chunk.to_csv(
            output_path,
            mode="w" if first_chunk else "a",
            header=first_chunk,
            index=False
        )
        total += len(chunk)
        first_chunk = False
        print(f"Generated {total:,} records...")

    return total


def main():
    parser = argparse.ArgumentParser(
        description="Generate FlowForge synthetic datasets"
    )
    parser.add_argument("--customers", type=int, default=100000)
    parser.add_argument("--orders", type=int, default=500000)
    args = parser.parse_args()

    if args.customers < 1 or args.orders < 1:
        parser.error("Record counts must be greater than zero.")

    random.seed(SEED)
    fake = Faker()
    Faker.seed(SEED)

    INPUT_DIR.mkdir(parents=True, exist_ok=True)

    print("Generating customers in chunks...")
    customer_total = write_chunks(
        generate_customers(args.customers, fake),
        INPUT_DIR / "customers.csv"
    )

    print("\nGenerating orders in chunks...")
    order_total = write_chunks(
        generate_orders(args.orders, args.customers, fake),
        INPUT_DIR / "orders.csv"
    )

    print("\nDataset generation completed!")
    print(f"Customers: {customer_total:,}")
    print(f"Orders: {order_total:,}")
    print(f"Total: {customer_total + order_total:,}")
    print(f"Output folder: {INPUT_DIR}")


if __name__ == "__main__":
    main()
