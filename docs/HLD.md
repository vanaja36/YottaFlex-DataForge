
# FlowForge – High-Level Design (HLD)

## 1. Introduction

FlowForge is a reusable batch data integration and quality framework. It processes customer and order data from CSV files and loads validated records into a SQLite database.

## 2. System Objectives

- Support multiple datasets through reusable pipeline components.
- Validate input schemas and record-level data quality.
- Separate valid and rejected records.
- Maintain referential integrity.
- Prevent duplicate processing of identical input files.
- Support transaction rollback and recovery.
- Provide execution metrics, logs, and reconciliation.

## 3. System Components

| Component | Input | Output |
|---|---|---|
| Extraction | CSV files | DataFrames |
| Validation | Extracted DataFrames | Valid and rejected records |
| Transformation | Valid records | Database-ready records |
| Loading | Transformed records | SQLite tables |
| Logging | Pipeline events | Log entries |
| Metrics | Execution details | Processing statistics |
| Reconciliation | Source and database records | Reconciliation results |

## 4. Processing Workflow

1. Initialize database tables.
2. Identify the dataset and source file.
3. Calculate the source file's SHA-256 hash.
4. Check whether the same content was already processed.
5. Extract records from the CSV file.
6. Validate schema and record-level rules.
7. Separate valid and invalid records.
8. Transform valid records.
9. Check foreign-key relationships for orders.
10. Load valid records and save rejected records.
11. Register the processed file.
12. Record execution metrics and status.
13. Run reconciliation to verify results.

## 5. Dataset Relationships

The system processes two related datasets.

- Customers are the parent dataset.
- Orders are the child dataset.
- `customers.customer_id` is the primary key.
- `orders.order_id` is the primary key.
- `orders.customer_id` references `customers.customer_id`.

Customers are processed before orders to support referential integrity.

## 6. Database Design

The framework uses five SQLite tables:

| Table | Purpose |
|---|---|
| customers | Stores customer records |
| orders | Stores order records |
| rejected_records | Stores rejected input records |
| pipeline_runs | Tracks pipeline executions |
| processed_files | Tracks previously processed file hashes |

## 7. Error Handling

The framework handles:
- Missing input files.
- Unsupported file formats.
- Empty files.
- Malformed CSV files.
- Missing required columns.
- Null and invalid values.
- Duplicate identifiers.
- Invalid customer references.
- Database transaction failures.

Rejected records are stored with reasons. Transactional database operations are rolled back if a failure occurs.

## 8. Idempotency and Recovery

SHA-256 hashes identify previously processed input content.

A file with the same dataset and content hash is skipped during a rerun.

If a transactional operation fails, the database changes are rolled back. The failed execution is recorded, and the source can be retried after resolving the issue.

## 9. Performance and Scalability

The framework uses chunked sample-data generation and batch database operations.

A sample execution processed 100,000 customers and 500,000 orders.

Previously measured throughput:
- Customers: approximately 90,212 records per second.
- Orders: approximately 75,186 records per second.

These measurements apply to the tested local environment and sample execution.

## 10. Security and Operational Considerations

- Database files and generated outputs are excluded from version control.
- Input data is validated before loading.
- Database constraints protect key relationships.
- Logs record pipeline execution and errors.
- SQLite is suitable for the current demonstration; larger production deployments may require a server database.

## 11. Future Scope

- Additional source formats.
- Configurable pipeline definitions.
- Incremental data ingestion.
- Cloud database integration.
- Scheduling and monitoring.
- Parallel processing.
- Automated schema evolution.
