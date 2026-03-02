import paho.mqtt.client as mqtt
import snap7
import struct
import json
import time
import random
import warnings

warnings.filterwarnings("ignore", category=DeprecationWarning)

BROKER = "localhost"
PORT = 1883
TOPIC = "zf/hlab/sensors/cnc01/telemetry"

IP_CLP = "127.0.0.1"
RACK = 0
SLOT = 1

print("Conectando ao CLP Virtual...")
plc = snap7.client.Client()
plc.connect(IP_CLP, RACK, SLOT)

mqtt_client = mqtt.Client(client_id="Edge_Gateway_CNC")
mqtt_client.connect(BROKER, PORT, 60)
mqtt_client.loop_start()

# Memória de estado para gráficos suaves (Moving Averages)
rpm_atual = 4000.0
vib_atual = 1.5
ciclo_atual = 42.0

try:
    print("🚀 Iniciando ingestão de dados ...")
    while True:
        dados_brutos = plc.db_read(db_number=1, start=0, size=4)
        temperatura_c = struct.unpack('>f', dados_brutos)[0]
        
        chance_parada = random.randint(1, 100)
        
        # Se superaqueceu (Passou de 75)
        if temperatura_c > 75.0:
            status_geral = "WARNING"
            event_type = "High Temp Alarm"
            machine_status = "Fault"
            
            # RPM despenca lentamente como inércia do spindle
            rpm_atual = max(0.0, rpm_atual - random.uniform(200, 500))
            
            # Vibração dispara (Ressonância térmica)
            vib_atual = min(8.0, vib_atual + random.uniform(0.5, 1.5))
            
            cycle_time = 0.0
            prod_rate = 0.0
            
        elif chance_parada > 95: # Pequena parada técnica
            status_geral = "IDLE"
            event_type = "Tool Change"
            machine_status = "Stopped"
            
            rpm_atual = 0.0
            vib_atual = random.uniform(0.1, 0.3)
            cycle_time = 0.0
            prod_rate = 0.0
            
        else: # Operação Normal
            status_geral = "RUNNING"
            event_type = "Production"
            machine_status = "Operational"
            
            # Controle PID Virtual: RPM balança suavemente
            rpm_atual += random.uniform(-40, 40)
            rpm_atual = max(3900, min(4100, rpm_atual))
            
            # Vibração é baseada na Temperatura! (Mecânica real)
            vib_base = 1.0 + ((temperatura_c - 40.0) * 0.04) 
            vib_atual += (vib_base - vib_atual) * 0.2 + random.uniform(-0.1, 0.1)
            vib_atual = max(0.5, vib_atual)
            
            # Tempo de ciclo estável
            ciclo_atual += random.uniform(-0.3, 0.3)
            ciclo_atual = max(41.5, min(43.5, ciclo_atual))
            
            cycle_time = ciclo_atual
            prod_rate = 60.0 / cycle_time if cycle_time > 0 else 0.0
            
        payload = {
            "machine_id": "CNC_840D_01",
            "status": status_geral,
            "spindle_rpm": round(rpm_atual, 0),
            "bearing_temp_c": round(temperatura_c, 2),
            "vib_rms_mms": round(vib_atual, 2),
            "cycle_time_sec": round(cycle_time, 1),
            "prod_rate_ppm": round(prod_rate, 2),
            "event_type": event_type,
            "machine_status": machine_status
        }
        
        json_payload = json.dumps(payload)
        mqtt_client.publish(TOPIC, json_payload)
        
        time.sleep(2)

except KeyboardInterrupt:
    print("\nParando Gateway...")
finally:
    plc.disconnect()
    mqtt_client.loop_stop()
    mqtt_client.disconnect()