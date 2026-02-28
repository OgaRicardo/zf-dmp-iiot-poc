import paho.mqtt.client as mqtt
import json
from influxdb_client import InfluxDBClient, Point
from influxdb_client.client.write_api import SYNCHRONOUS

# --- 1. Configurações do Roteador (MQTT) ---
MQTT_BROKER = "localhost"
MQTT_PORT = 1883
MQTT_TOPIC = "zf/usinagem/cnc_840d_01/telemetria"

# --- 2. Configurações do Cofre (InfluxDB) ---
INFLUX_URL = "http://localhost:8086"
INFLUX_TOKEN = "zIaMcxM-WXwtYkTOYolQKS3Fv6YFwBe_d8rkAdOtf4TD1XR0_w5tZm5HqZF4nJcHXCeHrfUCjD0I2mrFJePycg=="  # <-- Cole o seu token longo aqui
INFLUX_ORG = "ZF"
INFLUX_BUCKET = "telemetria_cnc"

# Conectando ao Banco de Dados
influx_client = InfluxDBClient(url=INFLUX_URL, token=INFLUX_TOKEN, org=INFLUX_ORG)
write_api = influx_client.write_api(write_options=SYNCHRONOUS)

def on_connect(client, userdata, flags, rc, *args, **kwargs):
    if rc == 0:
        print("✅ Ponte conectada ao Roteador MQTT!")
        client.subscribe(MQTT_TOPIC) # Assina o tópico para ouvir os dados
    else:
        print(f"❌ Erro MQTT: {rc}")

def on_message(client, userdata, msg):
    try:
        # Pega o pacote que chegou do MQTT e lê o JSON
        payload = json.loads(msg.payload.decode())
        print(f"📥 Chegou da Máquina: Temperatura {payload['temperatura_spindle']}ºC | RPM {payload['rpm_atual']}")

        # Prepara a "gaveta" para o InfluxDB (O que é Tag e o que é Valor numérico)
        ponto = Point("leitura_spindle") \
            .tag("maquina", payload["maquina"]) \
            .tag("status", payload["status"]) \
            .field("temperatura", float(payload["temperatura_spindle"])) \
            .field("rpm", int(payload["rpm_atual"]))

        # Salva definitivamente no banco
        write_api.write(bucket=INFLUX_BUCKET, org=INFLUX_ORG, record=ponto)
        print("   💾 Salvo no Banco com sucesso!\n")
        
    except Exception as e:
        print(f"⚠️ Erro ao salvar: {e}")

# Inicia a Ponte
print("Iniciando a Ponte de Dados (Edge-to-Database)...")
mqtt_client = mqtt.Client(client_id="Ponte_Salva_Banco")
mqtt_client.on_connect = on_connect
mqtt_client.on_message = on_message

mqtt_client.connect(MQTT_BROKER, MQTT_PORT, 60)
mqtt_client.loop_forever() # Fica rodando para sempre