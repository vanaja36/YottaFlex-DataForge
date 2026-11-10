
# FlowForge – Design Decisions

## 1. Purpose

This document records the key technical decisions made while designing and implementing FlowForge.

## 2. Technology Selection

| Technology | Decision | Reason |
|---|---|---|
| Python | Selected | Readable, modular, and suitable for data processing |
| Pandas | Selected | Efficient CSV extraction and tabular transformations |
| SQLite | Selected | Lightweight relational database with transaction support |
| Pytest | Selected | Automated testing and regression verification |
| Faker | Selected | Reproducible synthetic sample data generation |
| SHA-256 | Selected | Identifies previously processed file content |

## 3. Modular Architecture

**Decision:** Separate extraction, validation, transformation, loading, logging, and reconciliation into modules.

**Reason:** Each component has a focused responsibility, making the framework easier to test, maintain, and extend.

## 4. Dataset Design

**Decision:** Use Customers and Orders as related datasets.

**Reason:** This demonstrates multiple-dataset processing and referential integrity through a customer-to-orders relationship.

## 5. Data Validation

**Decision:** Separate invalid records from valid records instead of stopping the entire batch for every record-level issue.

**Reason:** Valid records can continue through the pipeline while invalid records are preserved with rejection reasons for investigation.

## 6. Idempotency

**Decision:** Use SHA-256 hashes with a unique dataset and content-hash constraint.

**Reason:** Reprocessing identical input files should not duplicate their effects in the target database.

**Trade-off:** File-level hashing skips an entire unchanged file. It does not independently track changes to individual source rows.

## 7. Transaction Management

**Decision:** Use a shared SQLite transaction for database loading, rejection storage, and processed-file registration.

**Reason:** These operations should succeed or fail together to prevent partial database state.

## 8. Referential Integrity

**Decision:** Validate that every order references an existing customer before loading it.

**Reason:** This prevents orphan order records and maintains relational consistency.

## 9. Schema Drift

**Decision:** Detect unexpected columns and report them without automatically rejecting the entire dataset.

**Reason:** This provides visibility into source changes while allowing compatible input to continue processing.

**Limitation:** Automatic schema migration is outside the current implementation.

## 10. Performance

**Decision:** Generate data in chunks and use batch database operations.

**Reason:** Chunking avoids creating the entire synthetic dataset in memory, while batch operations reduce repeated database calls.

## 11. Testing Strategy

**Decision:** Use isolated temporary databases and input files for automated tests.

**Reason:** Tests can verify database constraints, error handling, transaction rollback, and retry behavior without modifying the main sample database.

## 12. Future Improvements

- Configurable validation rules.
- Row-level change detection.
- Incremental ingestion.
- Support for cloud databases.
- Parallel processing.
- Automated scheduling and monitoring.
- Automatic schema evolution.
