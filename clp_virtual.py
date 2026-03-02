import snap7
import struct
import time
import ctypes
import random

print("Inicializando o Servidor CLP Virtual (Siemens 840D)...")

server = snap7.server.Server()
size = 100
DB_NUMBER = 1
db_data = (ctypes.c_byte * size)()

# Blindagem de versão do S7
try:
    from snap7.type import srvArea
    area = srvArea.DB
    server.register_area(area, DB_NUMBER, db_data)
except Exception:
    try:
        from snap7.types import srvAreaDB
        server.register_area(srvAreaDB, DB_NUMBER, db_data)
    except Exception:
        class AreaWrapper:
            value = 5
        server.register_area(AreaWrapper(), DB_NUMBER, db_data)

server.start(tcp_port=102)

print("✅ CLP Virtual rodando na porta 102 (IP: 127.0.0.1)")
print("Pressione Ctrl+C para parar.")

# Variáveis para simulação física realista (Curva Assintótica)
temperatura_atual = 40.0
temperatura_alvo = 80.0
aquecendo = True

try:
    while True:
        # Lógica de aquecimento/resfriamento arredondada
        if aquecendo:
            # Aquece rápido no início, perde força perto do topo (Inércia térmica)
            incremento = (temperatura_alvo - temperatura_atual) * 0.05
            temperatura_atual += incremento + random.uniform(-0.3, 0.4)
            
            if temperatura_atual >= 78.0: 
                aquecendo = False
                temperatura_alvo = 45.0
        else:
            # Esfria rápido, estabiliza embaixo
            decremento = (temperatura_atual - temperatura_alvo) * 0.05
            temperatura_atual -= decremento + random.uniform(-0.2, 0.5)
            
            if temperatura_atual <= 48.0: 
                aquecendo = True
                temperatura_alvo = 80.0
                
        # Proteção para não vazar a temperatura
        temperatura_atual = max(35.0, min(85.0, temperatura_atual))

        dado_em_bytes = struct.pack('>f', temperatura_atual)
        for i in range(4):
            db_data[i] = dado_em_bytes[i]
        
        time.sleep(1)

except KeyboardInterrupt:
    print("\nDesligando CLP Virtual...")
    server.stop()
    server.destroy()