
# FlowForge – Business Requirements Document (BRD)

## 1. Project Overview

FlowForge is a reusable data integration and quality framework designed to process structured data from multiple CSV sources.

It validates, transforms, and loads customer and order records into a relational database while maintaining data quality, processing history, and reconciliation results.

## 2. Business Problem

Data integration workflows often face challenges such as:
- Missing or invalid records.
- Duplicate records.
- Inconsistent source schemas.
- Broken relationships between datasets.
- Duplicate processing during reruns.
- Limited visibility into failures and data quality.

FlowForge addresses these challenges through a reusable and modular processing framework.

## 3. Business Objectives

1. Automate extraction and loading of structured datasets.
2. Improve data quality through validation.
3. Separate invalid records for investigation.
4. Prevent duplicate processing of identical files.
5. Maintain referential integrity between datasets.
6. Support failure recovery through transaction management.
7. Provide processing metrics and reconciliation.

## 4. Project Scope

### In Scope

- CSV-based data extraction.
- Customer and order dataset processing.
- Schema and record validation.
- Data transformation.
- SQLite database loading.
- Duplicate and null-value detection.
- Foreign-key validation.
- Rejected-record storage.
- File-level idempotency.
- Transaction rollback and recovery.
- Logging, metrics, and reconciliation.
- Automated testing.

### Out of Scope

- Real-time streaming ingestion.
- Distributed processing.
- Automated scheduling.
- Cloud deployment.
- Automatic schema migration.
- Dedicated automated date-range backfill.

## 5. Stakeholders

| Stakeholder | Responsibility |
|---|---|
| Data Engineer | Develops and maintains the integration framework |
| Data Analyst | Uses validated data for analysis |
| Business User | Consumes reliable customer and order information |
| System Administrator | Monitors execution and database availability |

## 6. Functional Requirements

| ID | Requirement |
|---|---|
| FR01 | Extract customer and order data from CSV files |
| FR02 | Validate required columns and record values |
| FR03 | Detect duplicate identifiers |
| FR04 | Identify invalid and missing values |
| FR05 | Transform valid records before loading |
| FR06 | Validate customer references in orders |
| FR07 | Store rejected records with reasons |
| FR08 | Prevent duplicate processing of identical files |
| FR09 | Track pipeline execution status and metrics |
| FR10 | Support transactional rollback |
| FR11 | Support retry after a failed transaction |
| FR12 | Reconcile source and database records |

## 7. Non-Functional Requirements

- **Reliability:** Prevent partial transactional database updates.
- **Maintainability:** Use independent, reusable modules.
- **Testability:** Provide automated tests.
- **Scalability:** Support larger sample datasets through chunked generation and batch operations.
- **Observability:** Record logs, metrics, and execution status.
- **Data integrity:** Enforce primary-key and foreign-key constraints.

## 8. Business Data

The framework currently supports:
- Customers: customer details and update dates.
- Orders: product, quantity, pricing, and customer references.

One customer can have multiple orders.

## 9. Success Criteria

The project demonstrates success when:
- Both datasets are processed successfully.
- Invalid records are identified and recorded.
- Identical input files are skipped on rerun.
- Failed transactions are rolled back.
- Failed processing can be retried.
- Automated tests pass.
- Source and target record counts reconcile.

## 10. Deliverables

- Python source code.
- Sample customer and order datasets.
- SQLite database implementation.
- Automated test suite.
- Project README.
- Architecture and design documents.
- Data dictionary.
- Operational and testing documentation.
- Reconciliation results and performance measurements.
