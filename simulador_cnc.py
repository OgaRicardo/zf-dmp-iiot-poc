import paho.mqtt.client as mqtt
import snap7
import struct
import json
import time
import random

# --- 1. Configurações do Roteador (MQTT) ---
BROKER = "localhost"
PORT = 1883
TOPIC = "zf/usinagem/cnc_840d_01/telemetria"

# --- 2. Configurações do CLP Siemens (Físico ou Virtual) ---
IP_CLP = "127.0.0.1" # Aponta para o seu próprio computador (CLP Virtual)
RACK = 0
SLOT = 1  # Padrão S7-300

print(f"🔌 Conectando ao CLP Siemens em {IP_CLP}...")
plc = snap7.client.Client()
plc.connect(IP_CLP, RACK, SLOT)
print("✅ Conectado ao CLP com sucesso!")

# --- 3. Configurações do Cliente MQTT ---
def on_connect(client, userdata, flags, rc, *args, **kwargs):
    if rc == 0:
        print("✅ Conectado ao servidor EMQX!")
    else:
        print(f"❌ Erro MQTT: {rc}")

mqtt_client = mqtt.Client(client_id="CNC_Gateway_Siemens")
mqtt_client.on_connect = on_connect
mqtt_client.connect(BROKER, PORT, 60)
mqtt_client.loop_start()

try:
    print("🚀 Iniciando a leitura de memória S7 e envio para a Nuvem...")
    while True:
        # 1. LÊ O DADO FÍSICO DO CLP
        # Vamos ler a DB 1, começando no byte 0, pegando 4 bytes de tamanho (Float/Real)
        dados_brutos = plc.db_read(db_number=1, start=0, size=4)
        
        # 2. CONVERTE OS BYTES DE MÁQUINA PARA NÚMERO
        temperatura_real = struct.unpack('>f', dados_brutos)[0]
        
        # 3. MONTA O PACOTE JSON
        payload = {
            "maquina": "CNC_840D_01",
            "status": "PRODUZINDO",
            "temperatura_spindle": round(temperatura_real, 2), # Dado FÍSICO!
            "rpm_atual": int(random.uniform(1500, 2500)) # Deixei o RPM aleatório só para ter ruído visual
        }
        
        json_payload = json.dumps(payload)
        
        # 4. DISPARA PARA O SERVIDOR EMQX
        print(f"📡 DB1.DBD0 = {round(temperatura_real, 2)}ºC -> Publicando MQTT...")
        mqtt_client.publish(TOPIC, json_payload)
        
        time.sleep(2)

except KeyboardInterrupt:
    print("\nParando a coleta.")
finally:
    plc.disconnect()
    mqtt_client.loop_stop()
    mqtt_client.disconnect()