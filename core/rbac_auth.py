import jwt
import time
from fastapi import HTTPException, Security
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials

SECRET_JWT_KEY = "ODYSSEY_ULTRA_SECURE_JWT_SECRET_2026"
ALGORITHM = "HS256"

security = HTTPBearer()

# Base de datos simulada de usuarios y roles
USERS_DB = {
    "director_sanarate": {"password": "root_secure_password", "role": "FLIGHT_DIRECTOR"},
    "operator_01": {"password": "op_password", "role": "TELEMETRY_OPERATOR"},
    "viewer_guest": {"password": "guest", "role": "VIEWER"}
}

def create_access_token(username: str, role: str) -> str:
    expiration = time.time() + 86400  # 24 horas
    payload = {"sub": username, "role": role, "exp": expiration}
    return jwt.encode(payload, SECRET_JWT_KEY, algorithm=ALGORITHM)

def verify_role(required_role: str):
    """Dependencia de FastAPI para verificar Roles (RBAC)."""
    def dependency(credentials: HTTPAuthorizationCredentials = Security(security)):
        token = credentials.credentials
        try:
            payload = jwt.decode(token, SECRET_JWT_KEY, algorithms=[ALGORITHM])
            user_role = payload.get("role")
            
            # Jerarquía de permisos: FLIGHT_DIRECTOR > OPERATOR > VIEWER
            role_hierarchy = {"FLIGHT_DIRECTOR": 3, "TELEMETRY_OPERATOR": 2, "VIEWER": 1}
            
            if role_hierarchy.get(user_role, 0) < role_hierarchy.get(required_role, 0):
                raise HTTPException(status_code=403, detail=f"ACCESO DENEGADO: Se requiere rol {required_role}")
            return payload
        except jwt.PyJWTError:
            raise HTTPException(status_code=401, detail="Token JWT inválido o expirado.")
    return dependency
