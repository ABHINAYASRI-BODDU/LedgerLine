# LedgerLine - Threat Model and Security Analysis



## 1. Purpose



This document identifies security and financial integrity threats affecting LedgerLine and describes the controls implemented to reduce those risks.



LedgerLine is a development and demonstration banking application. It is not a production banking platform.



## 2. Assets to Protect



- User account credentials and password hashes.

- JWT access tokens.

- Customer account information.

- Financial transactions and balances.

- Double-entry ledger records.

- Failed transaction audit records.

- Database files and backups.

- Application configuration and JWT secrets.



## 3. System Components



LedgerLine consists of:



- **Frontend:** React application built with Vite.

- **Backend:** Python application using FastAPI.

- **Database:** SQLite for local development.

- **ORM:** SQLAlchemy.

- **Authentication:** Password hashing and JWT authentication.

- **Testing:** Pytest and HTTPX.



## 4. Trust Boundaries



1\. User browser to React frontend.

2\. Frontend to FastAPI backend.

3\. Backend services to the database.

4\. Application administrators to protected administrative operations.

5\. Development environment to source code and deployment configuration.



All client-provided data must be treated as untrusted and validated by the backend.



## 5. Identified Threats and Mitigations



| Threat | Potential impact | Implemented controls and remaining work |

|---|---|---|

| Unauthorized account access | Exposure of customer information or unauthorized transactions | Password hashing, JWT authentication and protected endpoints. Rate limiting and MFA remain future work. |

| Broken account authorization | A customer accesses another customer's account | Server-side account ownership checks and role-based permissions. |

| Duplicate transaction requests | Money is credited or transferred more than once | Idempotency keys and duplicate-request tests. |

| Negative account balances | Customers withdraw more money than available | Insufficient-balance validation and concurrency safeguards. |

| Concurrent withdrawals | Multiple requests spend the same available balance | SQLite transaction serialization using `BEGIN IMMEDIATE`; PostgreSQL row-locking behavior still requires verification. |

| Ledger modification or deletion | Financial records become unreliable | SQLite triggers prevent ledger-entry updates and deletions. PostgreSQL-specific protections remain future work. |

| Unbalanced transactions | Incorrect financial records or balances | Debit and credit verification before posting and ledger integrity verification. |

| Failed transactions | Inconsistent balances or missing failure records | Transaction rollback and independently stored failed-attempt audit records. |

| Secret exposure | Unauthorized access through leaked credentials or configuration | Environment-based configuration and `.gitignore` protections. Secret rotation and deployment secret management remain necessary. |

| Denial of service | Application becomes unavailable | Additional rate limiting, monitoring and resource controls are required. |



## 6. Implemented Security Controls



### Authentication and Authorization



- Passwords are hashed rather than stored as plain text.

- JWT tokens are used for authentication.

- Protected API endpoints require authentication.

- Role-based access control distinguishes customers and administrators.

- Customer account ownership is checked by the backend.



### Financial Transaction Protection



- Amounts are stored as integer paise.

- Deposits, withdrawals and transfers use double-entry bookkeeping.

- Insufficient-balance requests are rejected.

- Idempotency keys help prevent duplicate transaction processing.

- Database transactions provide rollback when operations fail.

- Concurrency safeguards are implemented for money movements.



### Audit and Ledger Integrity



- Failed deposit, withdrawal and transfer attempts are recorded.

- Failed-attempt audit records use an independent database session.

- SQLite triggers prevent updates and deletions of ledger entries.

- Ledger integrity verification checks debit and credit totals against transaction amounts.

- Automated tests verify important financial integrity behaviors.



## 7. Automated Security and Integrity Testing



The project includes automated tests for:



- Password hashing and verification.

- Authentication and invalid or expired tokens.

- Account management and authorization.

- Deposits, withdrawals and transfers.

- Duplicate transaction requests.

- Insufficient-balance validation.

- Transaction history.

- Ledger debit and credit balancing.

- Transaction rollback.

- Concurrent withdrawals and transfers.

- Failed transaction auditing.

- Ledger-entry update and deletion prevention.

- Ledger integrity verification.



**Latest recorded result: 37 tests passed.**



This result applies to the recorded local test run. Tests should be rerun after code changes.



## 8. Remaining Risks and Future Improvements



1\. Configure and test PostgreSQL deployment.

2\. Add database migrations.

3\. Implement PostgreSQL-specific ledger immutability protections.

4\. Verify concurrent transactions using PostgreSQL row-level locking and appropriate isolation.

5\. Strengthen idempotency handling for concurrent requests using database conflict handling.

6\. Add rate limiting and protection against brute-force login attempts.

7\. Consider multi-factor authentication.

8\. Configure HTTPS and secure production secrets.

9\. Review logging to avoid exposing tokens or sensitive financial information.

10\. Implement monitoring, backup and recovery procedures.

11\. Perform additional security testing and deployment reviews.



SQLite's `BEGIN IMMEDIATE` behavior is not equivalent to PostgreSQL row-level locking. Passing SQLite concurrency tests does not prove production PostgreSQL concurrency safety.



## 9. Security Assumptions and Limitations



- The current implementation uses SQLite for local development.

- SQLite immutability triggers are database-specific.

- The current automated tests do not establish production security.

- No claim of regulatory compliance or production banking readiness is made.

- Production deployment requires additional infrastructure, operational controls and security review.



## 10. Review Checklist



- [x] Identify application components and trust boundaries.

- [x] Identify important financial and authentication assets.

- [x] Implement authentication and authorization controls.

- [x] Implement idempotency and transaction protections.

- [x] Implement failed-attempt auditing.

- [x] Implement SQLite ledger immutability protections.

- [x] Add automated security and integrity tests.

- [ ] Verify PostgreSQL deployment and concurrency behavior.

- [ ] Add production monitoring, rate limiting and recovery procedures.

- [ ] Complete production security review.



## 11. Conclusion



LedgerLine implements several foundational authentication, authorization, transaction safety, audit and ledger integrity controls.



The project demonstrates how double-entry bookkeeping and backend security mechanisms can be combined in a full-stack financial application.



Further work is required before the application can be considered suitable for production financial use.

