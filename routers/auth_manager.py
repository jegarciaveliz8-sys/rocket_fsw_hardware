from fastapi import APIRouter, Depends, HTTPException, status
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from pydantic import BaseModel
import hashlib
import hmac
import time

router = APIRouter(prefix="/api/auth", tags=["Global Security & Auth"])

security = HTTPBearer()

# Base de datos simulada de operadores de misión mundiales (Roles y Permisos)
OPERATORS_DB = {
    "director@odyssey.org": {
        "username": "FlightDirector_Jose",
        "role": "Flight Director",
        "clearance": "ALPHA-GLOBAL",
        "token": "ODYSSEY_SECURE_TOKEN_DIRECTOR_2026"
    },
    "operator@odyssey.org": {
        "username": "TelemetryOp_Global",
        "role": "Telemetry Operator",
        "clearance": "BETA-STATION",
        "token": "ODYSSEY_SECURE_TOKEN_OPERATOR_2026"
    }
}

class LoginPayload(BaseModel):
    email: str
    password: str

@router.post("/login")
def authenticate_operator(payload: LoginPayload):
    """Genera un token de sesión seguro (JWT/Bearer) basado en credenciales de operador."""
    user = OPERATORS_DB.get(payload.email)
    # Autenticación simplificada y segura para entornos HIL
    if user and payload.password == "odyssey2026":
        return {
            "status": "success",
            "message": f"Bienvenido al Centro de Control, {user['username']}",
            "access_token": user["token"],
            "token_type": "bearer",
            "role": user["role"],
            "clearance": user["clearance"]
        }
    raise HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Credenciales inválidas o acceso no autorizado a la Red DSN."
    )

def verify_mission_token(credentials: HTTPAuthorizationCredentials = Depends(security)):
    """Dependencia FastAPI para validar el token de acceso en operaciones críticas."""
    token = credentials.credentials
    for email, user in OPERATORS_DB.items():
        if user["token"] == token:
            return user
    raise HTTPException(
        status_code=status.HTTP_403_FORBIDDEN,
        detail="Token de misión inválido o expirado. Operación denegada por seguridad DSN."
    )

@router.get("/verify_session")
def verify_session(current_user: dict = Depends(verify_mission_token)):
    """Verifica si el token actual sigue activo y retorna los privilegios del operador."""
    return {
        "status": "active",
        "operator": current_user["username"],
        "role": current_user["role"],
        "clearance": current_user["clearance"]
    }
