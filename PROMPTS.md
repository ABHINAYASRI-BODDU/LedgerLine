# LedgerLine - AI Prompt Engineering Log

## Project Information

- **Project:** LedgerLine - Money Movement with a Ledger You Can Prove
- **Challenge:** Snovasys Fresher Hiring Challenge 2026
- **Development period:** November 6-9, 2026
- **Repository:** [ABHINAYASRI-BODDU/LedgerLine](https://github.com/ABHINAYASRI-BODDU/LedgerLine)
- **Developer:** Abhinayasri Boddu

## 1. Purpose

This document records reusable AI prompts and summaries of AI-assisted development activities during LedgerLine development.

The purpose is to maintain transparency about AI assistance, document the engineering tasks performed, and make development decisions easier to understand and reproduce.

**Note:** Development entries are summaries of the actual work and discussions, not verbatim transcripts of every prompt.

## 2. Reusable Prompt Library

### 2.1 Build a Feature

Implement [feature] in LedgerLine. Inspect the existing code first and follow its architecture, naming, and UI conventions. Keep the change focused, handle loading, empty, and error states, and add or update relevant tests. Do not invent APIs, dependencies, or product requirements.

### 2.2 Review a Change

Review this change for correctness, regressions, security, and maintainability. Report actionable findings ordered by severity, with file and line references. Consider authorization, validation, data consistency, and financial calculations. Do not rewrite unrelated code.

### 2.3 Handle Financial Calculations

Implement [calculation or transaction flow] using integer minor units for currency. Avoid binary floating-point for financial calculations. Validate inputs, preserve transaction history, maintain atomicity, and add tests for boundaries, duplicate requests, and failures.

### 2.4 Diagnose a Bug

Investigate [bug and reproduction steps] by tracing the relevant code. Identify the root cause, make the smallest safe fix, and add a regression test. Preserve unrelated behavior.

### 2.5 Add Tests

Add tests for [behavior] using the project's existing testing framework. Cover expected behavior, edge cases, invalid input, authorization, and failure paths. Keep tests deterministic and avoid unrelated changes.

### 2.6 Explain a Flow

Explain how [feature or flow] works by tracing its entry point, validation, service logic, database operations, and error handling. Reference actual files and distinguish observed behavior from assumptions. Do not modify code.

### 2.7 Security Review

Review the implementation for authentication, authorization, input validation, secret handling, transaction integrity, and common security weaknesses. Identify realistic threats and recommend focused fixes with tests.

### 2.8 Documentation

Update the project documentation to match the actual implementation. Include setup instructions, architecture, API behavior, testing commands, security controls, limitations, and future improvements. Do not claim that unimplemented features are complete.

## 3. AI-Assisted Development Log

### Phase 1 - Backend Foundation and Authentication

**Development activities:**
- Set up the FastAPI backend and SQLite database.
- Created the initial project structure and application configuration.
- Implemented the user model and registration.
- Implemented password hashing and password verification.
- Added JWT authentication and protected endpoints.
- Implemented customer and administrator roles.
- Added account creation, account ownership checks, and account management APIs.

**Prompt summary:**

Help build the LedgerLine backend incrementally using FastAPI, SQLAlchemy, and SQLite. Explain the implementation step by step, preserve the existing project structure, and verify authentication, password security, and account authorization.

**Verification:** Authentication and account APIs were implemented and tested.

**Commit reference:** `629e673` - Account management APIs with role-based access.

### Phase 2 - Double-Entry Ledger and Transactions

**Development activities:**
- Implemented ledger accounts and ledger entries.
- Implemented deposits, withdrawals, and transfers.
- Used integer paise for currency storage.
- Added insufficient-balance checks.
- Implemented double-entry bookkeeping.
- Added balance calculation from ledger entries.

**Prompt summary:**

Implement deposits, withdrawals, and transfers using double-entry bookkeeping. Ensure every posted transaction has matching debit and credit entries, validate account ownership and available balances, and keep database operations atomic.

**Verification:** Transaction operations and ledger balancing were tested.

**Commit reference:** `cc7ce13` - Deposits, withdrawals, and transfers with double-entry ledger.

### Phase 3 - Transaction History

**Development activities:**
- Implemented transaction history API.
- Restricted customer history to transactions involving their own accounts.
- Added authentication and authorization checks.

**Prompt summary:**

Implement a transaction history endpoint that returns the authenticated customer's relevant transactions without exposing another customer's financial information.

**Verification:** Transaction history API tests passed.

**Commit reference:** `4b5fd9b` - Customer transaction history API.

### Phase 4 - Idempotency and Ledger Verification

**Development activities:**
- Added idempotency keys to financial transaction requests.
- Prevented duplicate processing when the same key is reused.
- Rejected reuse of a key for a different transaction.
- Added debit and credit verification before posting.
- Tested rollback behavior.

**Prompt summary:**

Improve transaction reliability by adding idempotency support. Repeated requests with the same key must not create duplicate financial movements. Verify ledger debit and credit totals before posting and test invalid key reuse and rollback scenarios.

**Verification:** Duplicate-request, key-reuse, balance-verification, and rollback tests passed.

**Commit reference:** `feat: add transaction idempotency and ledger balance verification`.

### Phase 5 - Authentication and Security Review

**Development activities:**
- Reviewed password hashing and token verification.
- Reviewed JWT validation and expiration.
- Checked protected endpoints and role-based access.
- Strengthened transaction-related protections.

**Prompt summary:**

Review LedgerLine's authentication and authorization implementation. Check password storage, token validation, expiration, account ownership, and transaction permissions. Identify weaknesses and verify fixes using tests.

**Verification:** Password and JWT validation scenarios were tested.

**Commit reference:** `0e5615b` - Strengthen authentication and transaction protections.

### Phase 6 - React Frontend

**Development activities:**
- Created a React application using Vite.
- Implemented the initial banking dashboard.
- Added frontend styling and application structure.

**Prompt summary:**

Build a React and Vite frontend for LedgerLine. Follow the existing backend API design and create a clear banking dashboard with appropriate components and styling.

**Verification:** Frontend build completed successfully.

**Commit reference:** `8dd5a32` - Build LedgerLine React frontend dashboard.

### Phase 7 - Frontend and Backend Integration

**Development activities:**
- Connected registration and login to backend APIs.
- Integrated authenticated user profile information.
- Connected account and balance information.
- Integrated transaction history.
- Added deposit, withdrawal, and transfer operations.
- Added currency input validation and rupee formatting.

**Prompt summary:**

Connect the React frontend to the existing FastAPI endpoints. Implement authentication, account information, balances, transaction history, deposits, withdrawals, and transfers. Validate amounts and display backend responses correctly.

**Verification:** Frontend API integration and production build were tested. Deposit, withdrawal, and transfer operations were exercised.

**Commit reference:** `c546601` - Integrate React frontend with banking APIs.

### Phase 8 - Automated Testing

**Development activities:**
- Set up pytest and HTTPX testing.
- Created isolated test database fixtures.
- Added authentication tests.
- Added account management tests.
- Added transaction tests.
- Tested financial integrity and rollback behavior.

**Prompt summary:**

Create automated tests for LedgerLine using pytest and HTTPX. Use an isolated test database and cover authentication, account ownership, transaction processing, duplicate requests, insufficient balances, and rollback behavior.

**Verification:** The recorded test suite reached 25 passing tests before concurrency and integrity testing were added.

**Commit reference:** `test: add automated tests for authentication accounts and transactions`.

### Phase 9 - Concurrency Safety

**Development activities:**
- Investigated concurrent financial requests.
- Added SQLite transaction serialization using `BEGIN IMMEDIATE`.
- Added PostgreSQL-oriented row-locking logic.
- Rechecked account and transaction conditions during money movements.
- Added concurrent withdrawal and transfer tests.

**Prompt summary:**

Improve financial transaction concurrency safety. Prevent concurrent requests from spending the same available balance. Handle account locking consistently and add tests for concurrent withdrawals, transfers, and duplicate requests.

**Verification:** Three concurrency tests passed. The full suite reached 28 passing tests.

**Important limitation:** SQLite serialization tests do not prove PostgreSQL row-level locking behavior.

**Commit reference:** `feat: add concurrency safety for money movements`.

### Phase 10 - Failed Attempt Auditing and Ledger Integrity

**Development activities:**
- Added a transaction-attempt audit model.
- Recorded failed deposit, withdrawal, and transfer attempts.
- Used an independent database session to preserve failed-attempt audit records.
- Added SQLite triggers preventing ledger-entry updates and deletions.
- Added ledger integrity verification.
- Installed ledger immutability triggers on the local database.
- Added audit and ledger protection tests.

**Prompt summary:**

Improve LedgerLine's auditability and ledger protection. Record failed financial transaction attempts independently of the failed transaction's rollback. Prevent modification and deletion of posted ledger entries and implement a service that verifies transaction debit and credit totals.

**Verification:** Audit, immutability, and integrity tests passed. The complete recorded test suite reached 37 passing tests.

**Commit reference:** Phase 10 audit and ledger integrity implementation.

### Phase 11 - Documentation and Security Analysis

**Development activities:**
- Updated the project README.
- Documented architecture, setup, testing, and limitations.
- Updated the threat model and security analysis.
- Reviewed `.gitignore`.
- Replaced the example JWT secret with a safe placeholder.
- Updated database table creation to install SQLite ledger immutability triggers.

**Prompt summary:**

Review and improve LedgerLine documentation. Make the README match the implemented application, document actual security controls and remaining risks, and ensure that example configuration does not expose secrets.

**Verification:** README and THREATS.md formatting were checked. Sensitive local files were verified as ignored by Git.

**Commit reference:** `ee2ab15` - Complete project documentation and security analysis.

## 4. Corrections and Engineering Decisions

The following decisions were made during development:

1. Currency values are stored as integer paise instead of binary floating-point values.
2. Customer balances are derived from ledger entries.
3. Financial movements use double-entry bookkeeping.
4. Idempotency keys are used to prevent duplicate processing.
5. Failed transaction attempts are recorded separately from rolled-back transactions.
6. Ledger entries are protected against updates and deletions using SQLite triggers.
7. Tests use a separate database instead of the local development database.
8. SQLite concurrency behavior is documented separately from PostgreSQL concurrency behavior.
9. Production deployment limitations are documented instead of claiming production readiness.
10. Example configuration uses a placeholder instead of a real JWT secret.

## 5. Testing Summary

The latest recorded full test result during Phase 10 was:

**37 passed**

The tests cover:

- Password hashing and verification.
- Authentication and JWT validation.
- Account creation and authorization.
- Deposits, withdrawals, and transfers.
- Idempotency and duplicate requests.
- Insufficient-balance handling.
- Transaction history.
- Ledger balancing.
- Transaction rollback.
- Concurrent financial requests.
- Failed transaction auditing.
- Ledger immutability.
- Ledger integrity verification.

The test suite should be rerun after further code changes.

## 6. Known Limitations and Future Work

The following work remains:

- PostgreSQL deployment and migration testing.
- PostgreSQL-specific ledger immutability protection.
- Verification of PostgreSQL row-level locking and concurrent requests.
- Robust concurrent idempotency conflict handling.
- Rate limiting and brute-force protection.
- Production monitoring and backup/recovery procedures.
- HTTPS and production secret management.
- Further frontend improvements.
- Live deployment and final demonstration.

LedgerLine is a development and demonstration project, not a production banking platform.

## 7. Transparency Statement

AI assistance was used for planning, code explanations, implementation guidance, debugging, test design, security review, and documentation.

The developer reviewed and executed the suggested commands, tested application behavior, inspected project files, and maintained the Git repository during development.

This document contains summaries of development activities and is not intended to represent exact verbatim AI conversations.