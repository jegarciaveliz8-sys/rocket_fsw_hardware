import hmac
import hashlib
import time

# Clave secreta simétrica compartida entre la GCS y la FSW (debe mantenerse segura)
SHARED_SECRET_KEY = b"ODYSSEY_1_SECURE_FLIGHT_KEY_2026"

def generate_command_signature(command_payload: str, timestamp: int, counter: int) -> str:
    """
    Genera un token HMAC-SHA256 para autenticar el comando uplink.
    Combina el payload, una marca de tiempo (timestamp) y un contador anti-replay.
    """
    message = f"{command_payload}:{timestamp}:{counter}".encode('utf-8')
    signature = hmac.new(SHARED_SECRET_KEY, message, hashlib.sha256).hexdigest()
    return signature

def verify_command_signature(command_payload: str, timestamp: int, counter: int, client_signature: str, max_drift_seconds: int = 10) -> bool:
    """
    Verifica la autenticidad del comando recibido en la FSW:
    1. Valida que el timestamp no esté vencido (protección contra retardos maliciosos).
    2. Recalcula el HMAC y compara de forma segura contra la firma del cliente.
    """
    current_time = int(time.time())
    
    # Validación de ventana temporal (Anti-Replay / Drift)
    if abs(current_time - timestamp) > max_drift_seconds:
        print(f"[SECURITY WARNING] Comando rechazado: Desfase temporal excesivo ({abs(current_time - timestamp)}s).")
        return False
        
    expected_signature = generate_command_signature(command_payload, timestamp, counter)
    
    # Comparación de tiempo constante para prevenir ataques de canal lateral
    return hmac.compare_digest(expected_signature, client_signature)

if __name__ == "__main__":
    # Prueba unitaria local
    cmd = "ACTUATE_THRUST:85.0"
    ts = int(time.time())
    cnt = 42
    
    sig = generate_command_signature(cmd, ts, cnt)
    print("Firma Generada:", sig)
    
    is_valid = verify_command_signature(cmd, ts, cnt, sig)
    print("¿Firma Válida?:", is_valid)
