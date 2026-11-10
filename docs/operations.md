
# FlowForge – Operations Guide

## 1. Purpose

This document explains how to operate FlowForge, rerun failed processing, restart the pipeline, and process corrected or historical input files.

## 2. Prerequisites

- Python environment configured.
- Project dependencies installed.
- Input CSV files available in `data/input/`.
- SQLite database accessible.
- Required directory structure available.

Activate the virtual environment:

```powershell
.venv\Scripts\Activate.ps1
```

## 3. Normal Pipeline Execution

Run the pipeline:

```powershell
python -m src.pipeline
```

The framework processes customers before orders.

Check the pipeline logs in:

```text
reports/flowforge.log
```

## 4. Handling Pipeline Failures

When a pipeline execution fails:

1. Read the error message in the terminal.
2. Inspect `reports/flowforge.log`.
3. Identify whether the issue is related to extraction, validation, transformation, or database operations.
4. Correct the source data or resolve the technical issue.
5. Retry the pipeline.

Transactional database changes are rolled back when a transactional operation fails. The failed execution is recorded separately.

## 5. Retry Procedure

After resolving the issue, execute:

```powershell
python -m src.pipeline
```

The framework calculates the input file hash.

- If the same file was successfully processed earlier, it is skipped.
- If the previous attempt failed before registering the file as processed, the same file can be retried.
- Successfully processed records are protected by database keys and upsert behavior.

## 6. Restart Procedure

To restart normal processing:

1. Verify that the input files are available.
2. Check the database and pipeline logs.
3. Resolve any previous errors.
4. Execute the pipeline again.
5. Run reconciliation.

```powershell
python -m src.pipeline
python -m src.reconcile
```

The framework uses the processed-file registry to avoid reprocessing identical input content.

## 7. Backfill Procedure

A backfill means processing corrected or historical data again.

Recommended procedure:

1. Prepare the corrected or historical CSV file.
2. Validate its columns and data types.
3. Back up the database before making significant changes.
4. Place the file in the expected input location.
5. Run the relevant dataset pipeline.
6. Verify loaded records and rejected records.
7. Run reconciliation.

FlowForge uses file-level SHA-256 hashes for idempotency. A file with changed content has a different hash and can be processed as a new input.

**Important limitations:**
- The current implementation does not provide a dedicated date-range backfill command.
- Upserts update matching primary keys but do not automatically delete target records absent from the new file.
- Historical corrections should be reviewed before processing.
- Orders depend on existing customer records, so customers should be processed first.

## 8. Data Quality Investigation

Rejected records are stored in the `rejected_records` database table.

Investigate:
- Dataset name.
- Source filename.
- Source row number.
- Rejection reason.
- Original record.
- Pipeline run ID.

Correct the source data before retrying.

## 9. Reconciliation

After a successful execution, run:

```powershell
python -m src.reconcile
```

Verify:
- Source and database record counts.
- Invalid customer references.
- Processed-file information.
- Pipeline execution status.

The overall reconciliation result should be PASS.

## 10. Operational Safety

- Back up the SQLite database before destructive maintenance.
- Do not manually delete processed-file records to force a rerun without understanding the consequences.
- Do not delete production input files before verifying successful processing.
- Preserve logs and rejected records for investigation.
- Avoid running multiple pipeline instances against the same database simultaneously.

## 11. Current Operational Limitations

- Retry is manually initiated.
- No automated scheduler is configured.
- No automatic retry limit or backoff mechanism is implemented.
- Backfill is performed using corrected input files.
- Processing is sequential.
