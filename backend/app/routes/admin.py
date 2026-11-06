
from fastapi import APIRouter, Depends

from app.dependencies.permissions import require_role
from app.models.user import User

router = APIRouter(
    prefix="/admin",
    tags=["Admin"]
)


@router.get("/dashboard")
def admin_dashboard(
    current_user: User = Depends(require_role("admin"))
):
    return {
        "message": "Welcome to the Admin Dashboard",
        "admin_id": current_user.id,
        "admin_name": current_user.full_name,
        "role": current_user.role
    }
