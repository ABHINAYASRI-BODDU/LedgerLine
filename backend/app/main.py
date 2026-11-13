import os
from contextlib import asynccontextmanager

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from app.create_tables import create_tables
from app.routes.auth import router as auth_router
from app.routes.admin import router as admin_router
from app.routes.accounts import router as accounts_router
from app.routes.transactions import router as transactions_router


@asynccontextmanager
async def lifespan(app: FastAPI):
    # Ensure database tables and triggers are initialized on startup
    try:
        create_tables()
    except Exception as exc:
        print(f"Startup table creation warning: {exc}")
    yield


app = FastAPI(
    title="LedgerLine API",
    description="A secure and transparent money movement system",
    version="1.0.0",
    lifespan=lifespan
)

# Local development frontend addresses
allowed_origins = [
    "http://localhost:5173",
    "http://127.0.0.1:5173",
    "http://localhost:5174",
    "http://127.0.0.1:5174"
]

# Add the deployed Vercel frontend address from the environment
frontend_url = os.getenv("FRONTEND_URL", "")

if frontend_url:
    allowed_origins.extend(
        origin.strip().rstrip("/")
        for origin in frontend_url.split(",")
        if origin.strip()
    )

app.add_middleware(
    CORSMiddleware,
    allow_origins=allowed_origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"]
)


@app.get("/")
def home():
    return {
        "message": "Welcome to LedgerLine API",
        "status": "running"
    }


@app.get("/health")
def health_check():
    return {
        "status": "healthy"
    }


app.include_router(auth_router)
app.include_router(admin_router)
app.include_router(accounts_router)
app.include_router(transactions_router)
