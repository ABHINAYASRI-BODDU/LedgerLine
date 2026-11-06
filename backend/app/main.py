from fastapi import FastAPI

from app.routes.auth import router as auth_router
from app.routes.admin import router as admin_router
from app.routes.accounts import router as accounts_router
app = FastAPI(
    title="LedgerLine API",
    description="A secure and transparent money movement system",
    version="1.0.0"
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


# Register authentication routes
app.include_router(auth_router)
app.include_router(admin_router)
app.include_router(accounts_router)