from fastapi import APIRouter, HTTPException

router = APIRouter(prefix="/api/auth", tags=["Security & RBAC"])

@router.post("/token")
def generate_operator_token(payload: dict):
    """Genera tokens de acceso basados en roles (Director, Operador, Ingeniero)."""
    username = payload.get("username", "guest")
    role = payload.get("role", "OBSERVER")
    return {
        "status": "success",
        "access_token": f"token_odyssey_{username}_{role.lower()}",
        "token_type": "bearer",
        "permissions": ["LAUNCH_ABORT", "UPLINK_CMD"] if role in ["DIRECTOR", "OPERATOR"] else ["READ_ONLY"]
    }
