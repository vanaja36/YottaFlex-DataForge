
# FlowForge – Data Dictionary

## 1. Overview

This document describes the datasets, fields, data types, business rules, and relationships used by FlowForge.

The framework currently processes two datasets: Customers and Orders.

## 2. Customers Dataset

| Column | Logical data type | Description | Validation |
|---|---|---|---|
| customer_id | String | Unique customer identifier | Required, unique, non-null |
| customer_name | String | Customer's name | Required, non-null |
| email | String | Customer email address | Required, valid email format |
| city | String | Customer's city | Required, non-null |
| age | Integer | Customer's age | Required, integer, between 1 and 120 |
| updated_at | Date/Datetime | Last update timestamp | Required, valid date |

Primary key: `customer_id`

## 3. Orders Dataset

| Column | Logical data type | Description | Validation |
|---|---|---|---|
| order_id | String | Unique order identifier | Required, unique, non-null |
| customer_id | String | Customer associated with the order | Required, must reference an existing customer |
| product_name | String | Product name | Required, non-null |
| quantity | Integer | Number of products ordered | Required, positive integer |
| unit_price | Numeric | Price per product unit | Required, numeric, non-negative |
| order_date | Date | Date of the order | Required, valid date |
| total_amount | Numeric | Calculated order amount | Derived as quantity × unit_price |

Primary key: `order_id`

Foreign key: `orders.customer_id` references `customers.customer_id`.

## 4. Derived Fields

### total_amount

Calculation:

`total_amount = quantity * unit_price`

This field is derived during transformation and represents the total value of an order before any additional charges or discounts.

## 5. Database Tables

| Table | Purpose |
|---|---|
| customers | Stores valid customer records |
| orders | Stores valid order records |
| rejected_records | Stores rejected records and rejection reasons |
| pipeline_runs | Tracks pipeline execution status and record counts |
| processed_files | Tracks processed file hashes for idempotency |

## 6. Data Quality Rules

1. Required fields must not contain null values.
2. Primary identifiers must be unique within an input batch.
3. Customer age must be between 1 and 120.
4. Order quantity must be greater than zero.
5. Unit price must not be negative.
6. Every order must reference an existing customer.
7. Invalid records are rejected with a descriptive reason.
8. Unexpected columns are detected as potential schema drift.

## 7. Relationships

```text
CUSTOMERS
---------
customer_id (Primary Key)
       |
       | 1-to-Many
       |
ORDERS
------
order_id (Primary Key)
customer_id (Foreign Key)
```

One customer can have multiple orders. Each order belongs to one customer.

## 8. Assumptions and Limitations

- Input data is provided as CSV files.
- Customer data is processed before order data.
- Identifiers are treated as strings.
- Validation rules are implemented in Python.
- SQLite is used as the target database.
- The current implementation uses file-level SHA-256 hashes for idempotency.
- Schema drift is detected through unexpected columns; automatic schema migration is not implemented.
