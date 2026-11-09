# LedgerLine

**A secure money-movement application with a verifiable double-entry ledger.**

LedgerLine is a full-stack banking application designed to manage customer accounts and financial transactions while maintaining financial integrity, transaction traceability, and secure access.

## Features

- User registration and login
- Password hashing and JWT authentication
- Role-based access control
- Customer account management
- Deposits, withdrawals and transfers
- Transaction history
- Idempotency protection
- Double-entry bookkeeping
- Debit and credit verification
- Transaction rollback
- Concurrency safeguards
- Failed transaction attempt auditing
- SQLite ledger immutability triggers
- Ledger integrity verification
- React banking dashboard

## Technology Stack

| Component | Technology |
|---|---|
| Frontend | React 19 |
| Frontend tooling | Vite 8 |
| Backend | Python, FastAPI |
| ORM | SQLAlchemy |
| Local database | SQLite |
| PostgreSQL driver | Psycopg |
| Authentication | JWT |
| Configuration | Pydantic Settings |
| Testing | Pytest, HTTPX |
| Version control | Git and GitHub |

SQLite is the current local development database. PostgreSQL deployment and its database-specific protections require additional configuration and verification.

## Architecture

```text
LedgerLine/
|-- backend/
|   |-- app/
|   |   |-- dependencies/
|   |   |-- models/
|   |   |-- routes/
|   |   |-- schemas/
|   |   |-- security/
|   |   |-- services/
|   |   |-- config.py
|   |   |-- database.py
|   |   |-- create_tables.py
|   |   `-- main.py
|   |-- tests/
|   `-- requirements.txt
|-- frontend/
|   |-- public/
|   |-- src/
|   `-- package.json
|-- docs/
|-- .env.example
|-- PROMPTS.md
|-- THREATS.md
`-- README.md
```

## Double-Entry Ledger Design

Every successful transaction creates corresponding debit and credit ledger entries.

**Total debits = Total credits**

| Transaction | Debit | Credit |
|---|---|---|
| Deposit | System cash | Customer liability |
| Withdrawal | Customer liability | System cash |
| Transfer | Source customer liability | Destination customer liability |

Amounts are stored as integer paise to avoid floating-point rounding errors. Customer balances are calculated from ledger entries.

## Getting Started

### Prerequisites

- Python
- Node.js and npm
- Git

### 1. Clone the repository

```bash
git clone https://github.com/ABHINAYASRI-BODDU/LedgerLine.git
cd LedgerLine
```

### 2. Create and activate the virtual environment

Windows Command Prompt:

```cmd
python -m venv venv
venv\Scripts\activate
```

### 3. Configure environment variables

```cmd
copy .env.example .env
```

Open `.env` and configure a fresh, randomly generated JWT secret.

Required variables:

```env
APP_NAME=LedgerLine API
APP_VERSION=1.0.0
ENVIRONMENT=development
JWT_SECRET_KEY=replace-with-a-long-random-secret
JWT_ALGORITHM=HS256
ACCESS_TOKEN_EXPIRE_MINUTES=30
```

Never commit `.env` or publish actual secret values.

### 4. Install backend dependencies

From the repository root:

```cmd
cd backend
pip install -r requirements.txt
```

### 5. Initialize the database

From the backend directory:

```cmd
python -m app.create_tables
```

This creates missing database tables and installs SQLite ledger immutability triggers.

The local database is stored at `backend/ledgerline.db`.

### 6. Start the backend

From the backend directory:

```cmd
python -m uvicorn app.main:app --reload
```

- Backend: http://127.0.0.1:8000
- API documentation: http://127.0.0.1:8000/docs
- Health endpoint: http://127.0.0.1:8000/health

### 7. Start the frontend

Open a second terminal. From the repository root:

```cmd
cd frontend
npm install
npm run dev
```

Frontend: http://localhost:5173

Keep both servers running while using the application.

## Testing

From the backend directory, run:

```cmd
python -m pytest
```

The test suite covers password security, authentication, account management, money movements, idempotency, transaction history, ledger verification, rollback, concurrency, failed-attempt auditing and ledger immutability.

**Latest recorded test result: 37 tests passed.**

Run the tests again after code changes to verify the current result.

## Frontend Commands

Run these commands from the frontend directory.

| Command | Purpose |
|---|---|
| `npm install` | Install dependencies |
| `npm run dev` | Start development server |
| `npm run build` | Build frontend |
| `npm run lint` | Run ESLint |
| `npm run preview` | Preview production build |

## Security and Limitations

Implemented controls include password hashing, JWT authentication, role-based authorization, account ownership checks, idempotency keys, transaction rollback, concurrency safeguards, failed-attempt audit records, SQLite ledger immutability triggers and ledger integrity verification.

This project is a development and demonstration application, not a production banking platform.

Before production deployment, additional work is required:

- Configure and verify PostgreSQL deployment.
- Implement database migrations and PostgreSQL-specific ledger protections.
- Validate concurrency and transaction isolation under PostgreSQL.
- Add rate limiting and additional account-protection controls.
- Configure HTTPS and secure production secrets.
- Review logging, monitoring, backup and recovery procedures.
- Perform security testing and deployment reviews.

SQLite `BEGIN IMMEDIATE` concurrency behavior is not equivalent to PostgreSQL row-level locking. Passing SQLite concurrency tests does not establish production PostgreSQL concurrency safety.

See [THREATS.md](THREATS.md) for the project's threat analysis.

## Development Documentation

- [PROMPTS.md](PROMPTS.md) - AI-assisted development prompts and project history.
- [THREATS.md](THREATS.md) - Security threats and mitigations.

## Project Status

LedgerLine has implemented its core authentication, account management, money movement, ledger, frontend integration, concurrency safeguards, audit functionality and automated tests.

Remaining work includes documentation improvements, frontend refinement, deployment and final submission verification.

## Author

**Abhinayasri Boddu**

GitHub: https://github.com/ABHINAYASRI-BODDU

Repository: https://github.com/ABHINAYASRI-BODDU/LedgerLine