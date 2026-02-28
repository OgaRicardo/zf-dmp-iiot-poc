import snap7
import time
import struct
import ctypes  # <-- Biblioteca nativa para lidar com memória de hardware

# Tenta descobrir dinamicamente como a sua versão do snap7 chama a área DB
try:
    AREA_DB = snap7.types.SrvArea.DB
except AttributeError:
    try:
        AREA_DB = snap7.type.SrvArea.DB
    except AttributeError:
        AREA_DB = snap7.types.srvAreaDB

# Cria o Servidor (Finge ser a CPU do CLP)
server = snap7.server.Server()
server.start()

# ⚠️ O SEGREDO ESTÁ AQUI: Criamos um bloco de memória C real (1024 bytes)
db1_data = (ctypes.c_uint8 * 1024)()

# Registramos a DB no servidor APENAS UMA VEZ
server.register_area(AREA_DB, 1, db1_data)

print("🟢 CLP Virtual S7-300 Rodando na porta 102...")

# Fica rodando e atualizando a memória continuamente
try:
    temperatura = 45.0
    
    while True:
        # Simula a temperatura subindo aos poucos
        temperatura += 0.5
        if temperatura > 80.0:
            temperatura = 45.0
            
        # Altera o valor diretamente na memória física (DB1, Byte 0)
        # O servidor S7Comm vai transmitir automaticamente qualquer mudança feita aqui!
        struct.pack_into('>f', db1_data, 0, temperatura)
        
        time.sleep(1)

except KeyboardInterrupt:
    print("🔴 CLP Virtual Desligado.")
    server.stop()