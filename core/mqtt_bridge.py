import paho.mqtt.client as mqtt
import json

MQTT_BROKER = "broker.hivemq.com"  # O tu broker local Eclipse Mosquitto
MQTT_TOPIC_TELEMETRY = "odyssey1/sanarate/telemetry"

def on_connect(client, userdata, flags, rc):
    print(f"[MQTT] Conectado al broker DSN global con código: {rc}")
    client.subscribe(MQTT_TOPIC_TELEMETRY)

def on_message(client, userdata, msg):
    try:
        payload = json.loads(msg.payload.decode('utf-8'))
        print(f"[MQTT INBOUND] Telemetría física recibida: {payload.get('altitude')}m")
    except Exception as e:
        print(f"[MQTT ERROR] No se pudo parsear paquete: {e}")

def init_mqtt_client():
    client = mqtt.Client()
    client.on_connect = on_connect
    client.on_message = on_message
    try:
        client.connect_async(MQTT_BROKER, 1883, 60)
        client.loop_start()
    except Exception as e:
        print(f"[MQTT WARNING] No se pudo inicializar broker externo: {e}")
