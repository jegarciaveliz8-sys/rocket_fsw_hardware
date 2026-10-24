import asyncio
import websockets
import json
import time
import logging

logging.basicConfig(level=logging.INFO, format="%(asctime)s [%(levelname)s] %(message)s")
logger = logging.getLogger("SWARM-LOAD-TEST")

URI = "ws://localhost:8000/ws/telemetry"
NUM_CLIENTS = 25
TEST_DURATION = 10.0  # Duración de la prueba en segundos

async def simulate_client(client_id: int):
    start_time = time.time()
    messages_received = 0
    try:
        async with websockets.connect(URI) as websocket:
            logger.info(f"Cliente {client_id} conectado.")
            while time.time() - start_time < TEST_DURATION:
                try:
                    data = await asyncio.wait_for(websocket.recv(), timeout=2.0)
                    parsed = json.loads(data)
                    messages_received += 1
                except asyncio.TimeoutError:
                    logger.warning(f"Cliente {client_id}: Timeout esperando telemetría.")
                    break
    except Exception as e:
        logger.error(f"Cliente {client_id} error de conexión: {e}")
        return client_id, 0, False

    duration = time.time() - start_time
    logger.info(f"Cliente {client_id} finalizado. Recibidos {messages_received} mensajes en {duration:.2f}s.")
    return client_id, messages_received, True

async def main():
    logger.info(f"Iniciando prueba de carga de enjambre con {NUM_CLIENTS} clientes WebSocket concurrentes durante {TEST_DURATION}s...")
    tasks = [simulate_client(i) for i in range(1, NUM_CLIENTS + 1)]
    results = await asyncio.gather(*tasks)
    
    success_count = sum(1 for r in results if r[2])
    total_msgs = sum(r[1] for r in results)
    
    logger.info("=== RESUMEN DE PRUEBA DE ESTRÉS DE ENJAMBRE ===")
    logger.info(f"Clientes Exitosos: {success_count} / {NUM_CLIENTS}")
    logger.info(f"Total de Mensajes Procesados: {total_msgs}")
    logger.info(f"Promedio de Mensajes por Cliente: {total_msgs / NUM_CLIENTS if NUM_CLIENTS > 0 else 0:.1f}")

if __name__ == "__main__":
    asyncio.run(main())
