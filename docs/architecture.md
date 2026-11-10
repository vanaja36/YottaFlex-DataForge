
# FlowForge – System Architecture

## 1. Architecture Overview

FlowForge follows a modular, batch-oriented data integration architecture.

It separates extraction, validation, transformation, loading, logging, metrics, and reconciliation into independent components.

## 2. Architecture Diagram

```text
                SOURCE CSV FILES
                 customers.csv
                   orders.csv
                       |
                       v
                +-------------+
                |  Extraction |
                |  extract.py  |
                +-------------+
                       |
                       v
                +-------------+
                | Validation  |
                | validate.py |
                +-------------+
                   /       \
                  /         \
                 v           v
          VALID RECORDS   REJECTED RECORDS
                 |           |
                 v           v
          +-------------+  Rejection Storage
          | Transform   |  rejected_records
          |             |
          +-------------+
                 |
                 v
          +-------------+
          | Load Module |
          |  load.py    |
          +-------------+
                 |
                 v
          +----------------------+
          | SQLite Database      |
          | customers            |
          | orders               |
          | pipeline_runs        |
          | processed_files      |
          | rejected_records     |
          +----------------------+
                 |
                 v
          +----------------------+
          | Reconciliation       |
          | Metrics and Logging  |
          +----------------------+
```

## 3. Main Components

| Component | Responsibility |
|---|---|
| config.py | Central configuration and file paths |
| extract.py | Reads and extracts source CSV files |
| validate.py | Validates schemas and records |
| pipeline.py | Orchestrates the complete workflow |
| load.py | Loads records into SQLite |
| database.py | Creates and manages database connections and tables |
| logger.py | Captures execution information and errors |
| metrics.py | Calculates processing counts and throughput |
| reconcile.py | Compares source data with database data |
| generate_data.py | Generates reproducible sample datasets |

## 4. Data Flow

1. Read customer and order CSV files.
2. Calculate a SHA-256 hash for each input file.
3. Check whether the same dataset and file content were processed previously.
4. Extract the input records.
5. Validate required columns and record-level rules.
6. Separate valid and rejected records.
7. Transform valid records into the target database structure.
8. Validate order-to-customer references.
9. Load valid records and store rejected records.
10. Register the processed file and pipeline execution metrics.
11. Reconcile source counts against database counts.

## 5. Reliability Architecture

### Idempotency

SHA-256 file hashes identify previously processed input content. A repeated file with the same dataset and hash is skipped.

### Transaction Management

Database loading, rejected-record storage, and processed-file registration share a transaction. If a transactional operation fails, its database changes are rolled back.

### Error Handling

Exceptions are logged, failed pipeline executions are recorded separately, and the source file can be retried after the issue is resolved.

### Referential Integrity

Orders are checked against existing customer identifiers before loading.

## 6. Storage Design

SQLite is the target database.

The framework maintains five tables:

- customers
- orders
- rejected_records
- pipeline_runs
- processed_files

## 7. Current Scope and Limitations

- Batch processing using CSV inputs.
- SQLite as the target database.
- Sequential processing of customers and orders.
- File-level rather than row-level idempotency.
- Schema drift detection without automatic schema migration.
- No distributed processing or production scheduler in the current implementation.
