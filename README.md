
# FlowForge – Reusable Data Integration & Quality Framework

## 1. Project Overview

FlowForge is a reusable data integration and quality framework built using Python, Pandas, and SQLite.

It extracts data from CSV files, validates schemas and records, transforms valid data, loads records into a relational database, and tracks rejected records and pipeline execution metrics.

The framework currently supports two related datasets:
- Customers
- Orders

The design focuses on data quality, reliable loading, idempotency, error handling, and reconciliation.

## 2. Key Features

- Reusable extraction, validation, transformation, and loading components.
- Support for multiple datasets.
- Required-column and data-quality validation.
- Detection of duplicate records and missing values.
- Schema drift detection through unexpected-column inspection.
- Foreign-key validation for customer and order relationships.
- Rejected-record storage with rejection reasons.
- SHA-256 file hashing for idempotent processing.
- SQLite transactions to prevent partial database writes.
- Failure logging and retry after a failed transaction.
- Pipeline execution metrics and logging.
- Source-to-database reconciliation.
- Automated tests using Pytest.

## 3. Technology Stack

| Technology | Purpose |
|---|---|
| Python | Core programming language |
| Pandas | CSV extraction and data processing |
| SQLite | Relational database |
| NumPy | Numerical operations |
| Faker | Sample data generation |
| Pytest | Automated testing |
| Logging | Execution and error tracking |

## 4. Project Structure

```text
FlowForge/
│
├── data/
│   ├── input/
│   ├── output/
│   └── rejected/
│
├── docs/
│   ├── architecture.md
│   ├── BRD.md
│   ├── data_dictionary.md
│   ├── design_decisions.md
│   ├── HLD.md
│   ├── LLD.md
│   └── test_plan.md
│
├── reports/
│
├── src/
│   ├── config.py
│   ├── database.py
│   ├── extract.py
│   ├── generate_data.py
│   ├── load.py
│   ├── logger.py
│   ├── metrics.py
│   ├── pipeline.py
│   ├── reconcile.py
│   └── validate.py
│
├── tests/
├── main.py
├── requirements.txt
└── README.md
```

## 5. Supported Datasets

### Customers

| Column | Description |
|---|---|
| customer_id | Unique customer identifier |
| customer_name | Customer name |
| email | Customer email address |
| city | Customer city |
| age | Customer age |
| updated_at | Customer record update date |

### Orders

| Column | Description |
|---|---|
| order_id | Unique order identifier |
| customer_id | Reference to the customer |
| product_name | Ordered product |
| quantity | Number of units |
| unit_price | Price per unit |
| order_date | Order date |
| total_amount | Derived amount: quantity × unit_price |

## 6. Installation

Clone or download the project and open its root directory.

Create a virtual environment:

```powershell
python -m venv .venv
```

Activate it:

```powershell
.venv\Scripts\Activate.ps1
```

Install dependencies:

```powershell
pip install -r requirements.txt
```

## 7. Running the Framework

Generate sample data:

```powershell
python generate_data.py
```

Run the pipeline:

```powershell
python -m src.pipeline
```

Run reconciliation:

```powershell
python -m src.reconcile
```

Run automated tests:

```powershell
python -m pytest -v
```

## 8. Data Quality and Reliability

FlowForge applies validation rules before loading records.

Examples include:
- Required fields cannot be null.
- Customer and order identifiers must be unique within the input batch.
- Customer age must be between 1 and 120.
- Order quantity must be a positive integer.
- Unit price cannot be negative.
- Order records must reference an existing customer.
- Unexpected columns are detected for schema-drift awareness.

Invalid records are stored separately with their rejection reasons.

## 9. Idempotency and Transaction Handling

FlowForge calculates a SHA-256 hash for each input file.

Previously processed files with the same dataset and content hash are skipped, preventing duplicate processing during reruns.

Database writes, rejected-record storage, and processed-file registration are performed within a transaction. If an operation fails, the transaction is rolled back.

The pipeline also records failed executions separately so that the input can be retried after the underlying issue is resolved.

## 10. Performance Results

A sample execution processed:

| Dataset | Records loaded |
|---|---:|
| Customers | 100,000 |
| Orders | 500,000 |
| **Total** | **600,000** |

Previously measured execution results:

| Dataset | Duration | Throughput |
|---|---:|---:|
| Customers | 1.1085 seconds | ~90,212 records/sec |
| Orders | 6.6502 seconds | ~75,186 records/sec |

These are observed results from the sample execution environment, not guaranteed production benchmarks.

## 11. Reconciliation

The reconciliation module compares source record counts with database record counts and checks referential integrity.

A verified sample run reported:

- Customers: 100,000 source records and 100,000 database records.
- Orders: 500,000 source records and 500,000 database records.
- Invalid customer references: 0.
- Overall reconciliation status: PASS.

## 12. Testing

The automated test suite covers:
- Database primary-key and foreign-key constraints.
- CSV extraction errors and empty files.
- Required-column and record validation.
- Duplicate and null-value handling.
- Rejected-record storage.
- Transaction rollback.
- Recovery after a simulated failure.

Latest verified test result: **21 tests passed**.

Run the tests using:

```powershell
python -m pytest -v
```

## 13. Future Enhancements

- Support for additional source formats and database systems.
- Configurable validation rules.
- Incremental ingestion and change-data capture.
- Automated scheduling and monitoring.
- Parallel processing for larger datasets.
- Enhanced schema evolution management.

## 14. Author

**Vanaja Pandella**

FlowForge – Reusable Data Integration & Quality Framework

