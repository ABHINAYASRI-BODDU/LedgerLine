
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from app.routes.auth import router as auth_router
from app.routes.admin import router as admin_router
from app.routes.accounts import router as accounts_router
from app.routes.transactions import router as transactions_router


app = FastAPI(
    title="LedgerLine API",
    description="A secure and transparent money movement system",
    version="1.0.0"
)

# Allow the React frontend to communicate with FastAPI
app.add_middleware(
    CORSMiddleware,
    allow_origins=[
        "http://localhost:5173",
        "http://127.0.0.1:5173"
    ],
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
