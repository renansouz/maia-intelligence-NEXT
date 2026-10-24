# 📡 MAIA — Kit de Telemetria IoT e Viabilidade de Hardware

Este documento detalha a camada de hardware do ecossistema MAIA. Projetado sob a ótica de viabilidade econômica e implantação em larga escala, o kit IoT foi pensado para ser instalado em frotas agrícolas, transformando maquinário tradicional em ativos conectados em tempo real.

---

## 🦈 O Pitch para a Sompo: Por que investir em Hardware Próprio?

> _"Em um portfólio de seguros agrícolas onde um único sinistro de colheitadeira custa mais de R$ 400 mil, monitorar o ativo preventivamente é a apólice de seguro mais barata que a seguradora pode comprar."_

Ao equipar a frota do segurado com o **Kit de Telemetria MAIA**, a Sompo assume o controle ativo da gestão de risco. O custo de implantação de hardware por máquina é irrelevante frente à economia gerada pela prevenção de um único evento de incêndio por superaquecimento.

---

## 🛠️ Especificação do Kit de Hardware (BOM - Bill of Materials)

O kit de telemetria foi desenhado com componentes comerciais de prateleira (_COTS - Commercial Off-The-Shelf_), garantindo baixíssimo custo e facilidade de reposição:

| Componente                                      | Função Principal                                                                                        | Custo Médio Unitário (BRL) |
| :---------------------------------------------- | :------------------------------------------------------------------------------------------------------ | :------------------------- |
| **Microcontrolador ESP32**                      | Processamento local, lógica de captura e conectividade Wi-Fi / Bluetooth (controlador CAN nativo TWAI). | R$ 35,00 a R$ 45,00        |
| **Módulo Transceiver CAN (MCP2515 + TJA1050)**  | Interface física isolada para tradução segura do barramento CAN (J1939) da máquina.                     | R$ 20,00 a R$ 30,00        |
| **Módulo Modem 4G LTE (SIM7600E)**              | Transmissão celular de dados em áreas rurais com suporte às bandas regionais brasileiras.               | R$ 130,00 a R$ 190,00      |
| **Conversor de Tensão DC-DC (12V/24V para 5V)** | Regulação segura da energia extraída diretamente da bateria do trator/colheitadeira.                    | R$ 15,00 a R$ 25,00        |
| **Caixa de Proteção Estanque (IP67) + Chicote** | Proteção contra poeira, umidade extrema, vibração e intempéries do campo.                               | R$ 40,00 a R$ 60,00        |
| **CUSTO TOTAL ESTIMADO DO KIT**                 | **Hardware completo e autônomo por máquina**                                                            | **R$ 240,00 a R$ 350,00**  |

---

## ⚙️ Como Funciona na Prática (Arquitetura de Coleta)

1. **Conexão passiva:** O módulo transceptor conecta-se aos pinos CAN-High e CAN-Low do barramento padrão SAE J1939 presente em tratores modernos, operando por leitura passiva e **projetado para respeitar os parâmetros de integridade elétrica do fabricante**.
2. **Leitura e Processamento Local:** O ESP32 escuta os PGNs/SPNs da rede, decodifica os parâmetros vitais (temperaturas, pressões, RPM, torque) e armazena em buffer temporário.
3. **Disparo Seguro via API:** A cada janela operacional, os dados consolidados são transmitidos via rede celular (4G) em formato JSON leve (`POST /telemetria`), autenticados por chave de dispositivo exclusiva (`X-API-KEY`), alimentando instantaneamente o motor de IA no Oracle Cloud.

---

## 📈 Benefícios Comerciais e de Negócio para a Sompo

- **Mitigação Preventiva:** O investimento médio de ~R$ 300 por kit é amortizado na primeira intervenção preventiva que evita uma retífica de motor ou princípio de incêndio.
- **Redução Agressiva da Sinistralidade:** Mitigação de perdas totais em colheitadeiras e tratores de alta potência.
- **Diferencial Competitivo em Apólices:** A Sompo pode estruturar incentivos ou critérios de aceitação mais dinâmicos para frotas monitoradas em tempo real.

---

## 🧪 Validação Prática

Para fins de testes acadêmicos e demonstração sem a exigência de montagem física de bancada, o repositório disponibiliza um **Simulador de Telemetria via Terminal** (`iot/simular_sensor.py`), que injeta dados diretamente na API reproduzindo o comportamento exato do ESP32:

### Operação Normal:

```bash
python3 -m iot.simular_sensor normal
```

### Simulação de Superaquecimento (Risco de Incêndio / Alerta Sompo):

```bash
python3 -m iot.simular_sensor superaquecido
```
