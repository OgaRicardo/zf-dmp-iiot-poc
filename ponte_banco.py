import paho.mqtt.client as mqtt
import json
import warnings
from influxdb_client import InfluxDBClient, Point
from influxdb_client.client.write_api import SYNCHRONOUS

warnings.filterwarnings("ignore", category=DeprecationWarning)

INFLUX_URL = "http://localhost:8086"
INFLUX_TOKEN = "ZFLAB_SUPER_TOKEN"
INFLUX_ORG = "zf_lab"
INFLUX_BUCKET = "cnc"

print("🔌 Conectando ao InfluxDB...")
client_influx = InfluxDBClient(url=INFLUX_URL, token=INFLUX_TOKEN, org=INFLUX_ORG)
write_api = client_influx.write_api(write_options=SYNCHRONOUS)

BROKER = "localhost"
PORT = 1883
TOPIC = "zf/hlab/sensors/cnc01/telemetry"

def on_connect(client, userdata, flags, rc, properties=None):
    if rc == 0:
        print("✅ Ponte Conectada ao MQTT! Aguardando dados...")
        client.subscribe(TOPIC)
    else:
        print(f"❌ Falha ao conectar. Código: {rc}")

def on_message(client, userdata, msg):
    try:
        payload = msg.payload.decode('utf-8')
        data = json.loads(payload)
        
        # Força o TypeCasting para Float em tudo que é número para o banco nunca mais travar
        point = Point("cnc_telemetry") \
            .tag("machine_id", str(data["machine_id"])) \
            .field("status", str(data["status"])) \
            .field("spindle_rpm", float(data["spindle_rpm"])) \
            .field("bearing_temp_c", float(data["bearing_temp_c"])) \
            .field("vib_rms_mms", float(data["vib_rms_mms"])) \
            .field("cycle_time_sec", float(data["cycle_time_sec"])) \
            .field("prod_rate_ppm", float(data["prod_rate_ppm"])) \
            .field("event_type", str(data["event_type"])) \
            .field("machine_status", str(data["machine_status"]))
            
        write_api.write(bucket=INFLUX_BUCKET, org=INFLUX_ORG, record=point)
        print(f"💾 Gravado: Temp: {data['bearing_temp_c']}°C | Vib: {data['vib_rms_mms']} | Ciclo: {data['cycle_time_sec']}s")
        
    except Exception as e:
        print(f"❌ Erro ao processar: {e}")

mqtt_client = mqtt.Client(client_id="Bridge_InfluxDB")
mqtt_client.on_connect = on_connect
mqtt_client.on_message = on_message

mqtt_client.connect(BROKER, PORT, 60)

try:
    mqtt_client.loop_forever()
except KeyboardInterrupt:
    print("\nDesligando a Ponte...")
finally:
    client_influx.close()
    mqtt_client.disconnect()