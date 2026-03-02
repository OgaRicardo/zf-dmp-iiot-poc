# 🏭 ZF Lab: PoC de IoT Edge (Cloud-Ready) para Monitoramento de OEE e Preditiva em CNCs

## 🎯 A Solução: Arquitetura IoT Edge orientada a Nuvem (Azure-Ready)
Este projeto é uma Prova de Conceito (PoC) que implementa um **Edge Gateway** industrial. Em vez de interagir com o sistema operacional da máquina, o Gateway se comunica diretamente com o CLP (via protocolo S7 Communication puro) no nível de hardware.

Os dados brutos são processados na borda (Edge Computing) e convertidos em payloads JSON leves, transmitidos via MQTT. Esta arquitetura foi desenhada para ser "Cloud-Ready", sendo o estágio preparatório ideal para ingestão massiva de telemetria no **Microsoft Azure (Azure IoT Hub e Azure Data Explorer)**.

## 🏗️ Arquitetura do Sistema (IT/OT Flow)
```mermaid
graph TD
    subgraph OT_Layer ["🏭 Camada OT (Chão de Fábrica)"]
        CNC["Máquina CNC<br>(Windows XP Legado)"]
        PLC["CLP S7-300<br>(DB1 - Dados Brutos)"]
        CNC --- PLC
    end

    subgraph Edge_Layer ["🛡️ Edge Computing Layer"]
        Snap7["Snap7 Client<br>(Leitura S7 Direct)"]
        DataPrep["Processamento Edge<br>(Cálculo OEE e Conversão JSON)"]
        MQTT_Pub["MQTT Publisher"]

        Snap7 --> DataPrep --> MQTT_Pub
    end

    subgraph Broker ["🔄 Mensageria"]
        Mosquitto["Mosquitto MQTT Broker<br>(Porta 1883)"]
    end

    subgraph IT_Layer ["📊 Local Analytics (PoC)"]
        Influx["InfluxDB<br>(Time-Series Database)"]
        Grafana["Grafana<br>(Gestão à Vista & Preditiva)"]
    end

    subgraph Cloud_Layer ["☁️ Cloud-Ready (Alvo: Microsoft Azure)"]
        IoT_Hub["Azure IoT Hub<br>(Ingestão Segura)"]
        ADX["Azure Data Explorer<br>(Preditiva Avançada)"]
    end

    %% Conexões Ativas
    PLC == "S7 Communication (Porta 102)" ==> Snap7
    MQTT_Pub == "Payload JSON" ==> Mosquitto
    Mosquitto == "Subscrição" ==> Influx
    Influx == "Consultas Flux" ==> Grafana

    %% Conexões Futuras (Cloud)
    Mosquitto -. "Ponte Cloud" .-> IoT_Hub
    IoT_Hub -. "Integração" .-> ADX

    classDef ot fill:#f9d0c4,stroke:#333,stroke-width:2px;
    classDef edge fill:#d4e157,stroke:#333,stroke-width:2px;
    classDef broker fill:#fff176,stroke:#333,stroke-width:2px;
    classDef it fill:#81d4fa,stroke:#333,stroke-width:2px;
    classDef cloud fill:#b3e5fc,stroke:#333,stroke-width:2px,stroke-dasharray: 5 5;

    class CNC,PLC ot;
    class Snap7,DataPrep,MQTT_Pub edge;
    class Mosquitto broker;
    class Influx,Grafana it;
    class IoT_Hub,ADX cloud;
```

## ⚙️ Stack Tecnológico
* **OT Layer:** Servidor Snap7 emulando os Data Blocks (DBs) do CLP de uma máquina CNC.
* **Edge Layer:** Script Python atuando como Edge Device. Realiza a leitura dos bytes, converte os tipos de dados e aplica lógicas locais.
* **Mensageria Segura:** Eclipse Mosquitto (MQTT Broker) atuando como barramento de dados.
* **Local Data & Analytics:** InfluxDB (Time-Series) e Grafana rodando em contêineres Docker (IaC) para processamento, agregação e gestão à vista local.

## 📊 Engenharia de Confiabilidade e Monitoramento Baseado em Condição (CBM)
Para validar os modelos analíticos, o projeto implementa um motor de física realista que simula os seguintes KPIs de PCM e Produção:
1. **Curva Térmica Assintótica:** O modelo matemático do mancal (*bearing*) respeita a inércia térmica (Lei de Resfriamento de Newton), essencial para estudos de limites de controle preditivo.
2. **Espectro de Vibração RMS:** Programado com correlação direta à temperatura e ao *Spindle RPM*, simulando ressonância mecânica e desbalanceamento dinâmico.
3. **Machine Analytics & OEE:** Cálculo orgânico de *Cycle Time* e *Production Rate (PPM)*. O sistema identifica autonomamente micro-paradas, alarmes severos e operação normal, gerando as bases para cálculo de Disponibilidade e Performance.

## 👨‍💻 Autor
**Ricardo A. Ogasawara**  
*Engenheiro de Controle e Automação | MBA em Gestão de Manutenção 4.0*  
Especialista em PCM, Confiabilidade e Integração de Arquiteturas IT/OT para ecossistemas industriais complexos.
