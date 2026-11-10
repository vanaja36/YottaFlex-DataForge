
# FlowForge – Low-Level Design (LLD)

## 1. Introduction

This document describes the implementation-level design of the FlowForge data integration framework.

## 2. Module Responsibilities

### config.py
- Defines project directory paths.
- Defines input, output, rejected, and reports directories.
- Defines supported datasets and required columns.
- Defines the SQLite database path.

### extract.py
- Reads CSV input files using Pandas.
- Handles missing files.
- Handles unsupported file extensions.
- Handles empty and malformed CSV files.

### validate.py
- Retrieves required columns for each dataset.
- Checks required-column availability.
- Detects unexpected columns.
- Validates individual records.
- Separates valid and rejected records.
- Provides rejection reasons.

### pipeline.py
- Coordinates the end-to-end workflow.
- Calculates SHA-256 file hashes.
- Checks processed-file history.
- Runs extraction, validation, transformation, and loading.
- Checks order-to-customer references.
- Saves rejected records.
- Records pipeline execution metrics.
- Handles transactional failures.

### load.py
- Loads transformed records into SQLite.
- Uses primary-key conflict handling.
- Supports a shared database connection and transaction.

### database.py
- Creates database connections.
- Enables SQLite foreign-key enforcement.
- Initializes database tables.
- Supports transactional operations.

### logger.py
- Configures application logging.
- Records informational messages and errors.

### metrics.py
- Tracks total records.
- Tracks valid and rejected records.
- Tracks execution duration.
- Calculates throughput.

### reconcile.py
- Compares source and database record counts.
- Checks invalid customer references.
- Reports processed files and execution status.

### generate_data.py
- Generates reproducible customer and order datasets.
- Uses a fixed random seed.
- Generates data in chunks.

## 3. Processing Logic

### Step 1: Extraction

The extraction module reads the specified CSV file and returns a Pandas DataFrame.

### Step 2: Idempotency Check

The pipeline calculates a SHA-256 hash of the input file.

It checks the `processed_files` table for the combination of dataset and content hash.

If an identical file was previously processed, the pipeline skips it.

### Step 3: Schema Validation

The validation module checks required columns and detects unexpected columns.

### Step 4: Record Validation

Each record is checked against dataset-specific rules.

Invalid records are separated and assigned rejection reasons.

### Step 5: Transformation

Valid records are converted into the expected database structure.

For orders:

`total_amount = quantity * unit_price`

### Step 6: Referential Integrity

Before loading orders, the pipeline verifies that each referenced customer exists.

### Step 7: Loading and Rejection Storage

Valid records are loaded into SQLite. Rejected records are stored in `rejected_records`.

### Step 8: Transaction Completion

Loading, rejection storage, and processed-file registration share a transaction.

If an operation fails, the transaction is rolled back.

### Step 9: Metrics and Logging

The pipeline records execution status, record counts, duration, and throughput.

## 4. Database Tables

### customers
- customer_id – Primary key
- customer_name
- email
- city
- age
- updated_at

### orders
- order_id – Primary key
- customer_id – Foreign key
- product_name
- quantity
- unit_price
- total_amount
- order_date

### rejected_records
Stores dataset name, source file, row number, run ID, rejection reason, and original record.

### pipeline_runs
Stores run ID, dataset, execution status, record counts, start time, and completion time.

### processed_files
Stores dataset name, source file, SHA-256 content hash, and processing timestamp.

## 5. Failure Handling

The framework handles extraction errors, validation failures, database errors, and transaction failures.

A failed transactional operation does not leave partially loaded data. The failed execution is recorded separately, allowing the input to be retried.

## 6. Testing

The implementation is tested using Pytest.

Current automated coverage includes:
- Database constraints.
- CSV extraction scenarios.
- Schema and record validation.
- Rejected-record storage.
- Transaction rollback.
- Recovery after simulated failure.

The latest complete test run passed 21 tests.

## 7. Current Limitations

- CSV is the implemented source format.
- SQLite is the implemented target database.
- Idempotency is file-level.
- Processing is sequential.
- Automatic schema migration is not implemented.
