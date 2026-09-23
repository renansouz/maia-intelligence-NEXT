# 📡 MAIA — Camada de Telemetria e Simulação IoT (ESP32 / CAN)

Este documento descreve como o MAIA realiza a ingestão de dados físicos coletados diretamente de máquinas agrícolas por meio de microcontroladores ESP32 conectados ao barramento CAN (J1939).

---

## 1. Arquitetura de Coleta e Envio

```
[ Máquina Agrícola ] ──(Barramento CAN J1939)──► [ Transceiver CAN MCP2515 ] ──(SPI)──► [ Microcontrolador ESP32 ] ──(Wi-Fi / HTTP POST)──► [ API FastAPI / MAIA ]
```

- **Leitura CAN:** O ESP32 lê os parâmetros vitais do motor transmitidos pela central da máquina.
- **Formatação de Pacote:** Os dados brutos de PGN/SPN são convertidos em um payload padronizado em formato JSON.
- **Envio Seguro:** A cada janela de tempo (ex: 60 segundos), o ESP32 realiza um envio `POST` autenticado por chave de dispositivo (`X-API-KEY`) para o endpoint `/telemetria`.

---

## 2. Como o Sistema Identifica o Superaquecimento?

O motor de inteligência não avalia a temperatura de forma isolada (o que geraria falsos positivos dependendo da carga de trabalho). A detecção de risco de superaquecimento (cobertura básica de incêndio da Sompo) combina duas abordagens:

1. **Detecção de Anomalia Multivariada (Isolation Forest):** O modelo cruza simultaneamente a temperatura do arrefecimento (`EngCoolantTemp`) com torque, rotação e pressão do óleo. Se a temperatura subir de forma incompatível com o esforço exigido da máquina, o padrão anômalo é isolado.
2. **Gatilhos Críticos de Segurança:** Valores absolutos sustentados acima dos limites de projeto do fabricante (ex: `temp_coolant >= 95.0°C` ou `temp_oleo >= 105.0°C`) elevam o score para a classe **CRÍTICA**, disparando preventivamente o alerta no painel do operador e do gestor antes de danos estruturais.

---

## 3. Como a Banca Avaliadora pode Testar o Sensor

Para facilitar a avaliação prática sem a obrigatoriedade de configurar o ambiente virtual do Wokwi, disponibilizamos um **Simulador de Terminal em Python** que injeta dados diretamente na API:

### Cenário Operacional Normal:

```bash
python3 -m iot.simulador_terminal normal
```

### Cenário Crítico (Superaquecimento / Risco de Incêndio):

```bash
python3 -m iot.simulador_terminal superaquecido
```

Ao executar o cenário superaquecido, atualize a interface web da Sompo ou do Gestor para visualizar o alerta crítico gerado em tempo real pelo motor de IA.
