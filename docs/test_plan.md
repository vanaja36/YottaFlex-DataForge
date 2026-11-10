
# FlowForge – Test Plan

## 1. Objective

The purpose of this test plan is to verify the correctness, reliability, data quality, and recovery behavior of the FlowForge data integration framework.

## 2. Testing Approach

The project uses Pytest for automated testing.

Tests cover:
- Database operations and constraints.
- CSV extraction.
- Schema and record validation.
- Rejected-record handling.
- Transaction rollback.
- Failure recovery.

Temporary files and isolated databases are used where appropriate to avoid modifying production sample data during tests.

## 3. Test Environment

| Component | Configuration |
|---|---|
| Operating System | Windows |
| Language | Python |
| Data Processing | Pandas |
| Database | SQLite |
| Test Framework | Pytest |

## 4. Test Cases

| Test ID | Test Scenario | Expected Result |
|---|---|---|
| TC01 | Insert customer with unique ID | Successful insertion |
| TC02 | Insert duplicate customer ID | Primary-key violation |
| TC03 | Insert order with invalid customer ID | Foreign-key violation |
| TC04 | Insert valid order | Successful insertion |
| TC05 | Process an existing CSV file | Successful extraction |
| TC06 | Process a missing file | Appropriate error |
| TC07 | Process unsupported file format | Appropriate error |
| TC08 | Process zero-byte CSV | Empty-file error |
| TC09 | Process malformed CSV | Parsing error |
| TC10 | Process header-only CSV | Empty dataset handled |
| TC11 | Calculate file hash | Consistent SHA-256 hash |
| TC12 | Save an empty rejection batch | No error |
| TC13 | Save multiple rejected records | All rejection records stored |
| TC14 | Simulate transactional failure | Database changes rolled back |
| TC15 | Retry after simulated failure | Processing succeeds |
| TC16 | Validate customer records | Valid and rejected rows separated |
| TC17 | Validate order records | Valid and rejected rows separated |
| TC18 | Missing required columns | Validation error |
| TC19 | Unsupported dataset | Appropriate error |
| TC20 | Null required values | Records rejected |
| TC21 | Unexpected columns | Schema drift detected |

## 5. Additional Manual Data Quality Scenarios

The following scenarios were also demonstrated using sample input files:

### Duplicate order identifiers

Two records with the same order ID were supplied.

Expected result: Both duplicate records were rejected.

Observed result: 2 records rejected.

### Missing required value

An order with a missing product name was supplied.

Expected result: The record was rejected with a descriptive reason.

Observed result: 1 record rejected.

### Invalid customer reference

An order referencing a nonexistent customer was supplied.

Expected result: The order was rejected.

Observed result: 1 record rejected.

## 6. Transaction and Recovery Testing

A simulated rejection-storage failure was introduced during a pipeline execution.

Expected behavior:
- The transaction should roll back.
- No partial customer records should remain.
- The processed-file registration should not remain.
- A failed pipeline run should be recorded.

The same input was then retried after restoring the normal rejection-storage operation.

Expected behavior:
- The retry should complete successfully.
- The customer should be loaded.
- The file should be registered as processed.
- Both failed and successful execution histories should remain available.

## 7. Test Execution

Execute the complete test suite:

```powershell
python -m pytest -v
```

## 8. Latest Verified Test Result

| Metric | Result |
|---|---:|
| Total automated tests | 21 |
| Passed | 21 |
| Failed | 0 |
| Execution time | 2.03 seconds |

Overall result: PASS.

## 9. Reconciliation Testing

The reconciliation module was executed against the sample datasets.

| Dataset | Source Records | Database Records | Result |
|---|---:|---:|---|
| Customers | 100,000 | 100,000 | PASS |
| Orders | 500,000 | 500,000 | PASS |

Invalid customer references: 0.

Overall reconciliation: PASS.

## 10. Future Testing

Additional testing can cover:
- Very large input files.
- Concurrent pipeline execution.
- Schema changes and incompatible data types.
- Database connection interruptions.
- Partial file delivery.
- Performance under increasing data volumes.
- Automated retry limits and scheduling.
