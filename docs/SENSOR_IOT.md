# 📡 MAIA — Kit de Telemetria IoT e Viabilidade de Hardware

Este documento detalha a camada de hardware do ecossistema MAIA. Projetado sob a ótica de viabilidade econômica e implantação em larga escala, o kit IoT foi pensado para ser instalado em qualquer frota agrícola segurada, transformando maquinário tradicional em ativos conectados em tempo real.

---

## 🦈 Por que investir em Hardware Próprio?

> *"Em um portfólio de seguros agrícolas onde um único sinistro de colheitadeira custa mais de R$ 400 mil, monitorar o ativo preventivamente não é custo operacional, é a apólice de seguro mais barata que a seguradora pode comprar."*

Ao equipar a frota do segurado com o **Kit de Telemetria MAIA**, a Sompo deixa de ser uma pagadora passiva de sinistros e assume o controle ativo da gestão de risco. O custo de implantação de hardware por máquina é irrelevante frente à economia gerada pela prevenção de um único evento de incêndio por superaquecimento.

---

## 🛠️ Especificação do Kit de Hardware (BOM - Bill of Materials)

O kit de telemetria foi desenhado com componentes comerciais de prateleira (*COTS - Commercial Off-The-Shelf*), garantindo baixíssimo custo, facilidade de reposição e homologação imediata:

| Componente | Função Principal | Custo Médio Unitário (BRL) |
| :--- | :--- | :--- |
| **Microcontrolador ESP32** | Processamento local, lógica de captura e conectividade Wi-Fi / Bluetooth. | R$ 35,00 a R$ 45,00 |
| **Módulo Transceiver CAN (MCP2515 + TJA1050)** | Interface física isolada para leitura segura do barramento CAN (J1939) da máquina. | R$ 20,00 a R$ 30,00 |
| **Módulo Modem 4G LTE (SIM7600E ou SIM800L)** | Transmissão celular de dados em áreas rurais sem cobertura Wi-Fi. | R$ 120,00 a R$ 180,00 |
| **Conversor de Tensão DC-DC (12V/24V para 5V)** | Regulação segura da energia extraída diretamente da bateria do trator/colheitadeira. | R$ 15,00 a R$ 25,00 |
| **Caixa de Proteção Estanque (IP67) + Chicote** | Proteção contra poeira, umidade extrema, vibração e intempéries do campo. | R$ 40,00 a R$ 60,00 |
| **CUSTO TOTAL ESTIMADO DO KIT** | **Hardware completo e autônomo por máquina** | **R$ 230,00 a R$ 340,00** |

---

## ⚙️ Como Funciona na Prática (Arquitetura de Coleta)

1. **Conexão não-intrusiva:** O módulo MCP2515 conecta-se aos pinos CAN-High e CAN-Low do barramento padrão SAE J1939 presente em tratores modernos (John Deere, Case IH, Valtra, New Holland, Massey Ferguson), **sem interferir na central eletrônica (ECU) original** e sem violar a garantia de fábrica do bem segurado.
2. **Leitura e Processamento Local:** O ESP32 escuta os PGNs/SPNs da rede, decodifica os parâmetros vitais (temperaturas, pressões, RPM, torque) e armazena em buffer temporário.
3. **Disparo Seguro via API:** A cada 60 segundos, os dados consolidados são transmitidos via rede celular (4G) em formato JSON leve (`POST /telemetria`), autenticados por chave de dispositivo exclusiva (`X-API-KEY`), alimentando instantaneamente o motor de IA no Oracle Cloud.

---

## 📈 Benefícios Comerciais e de Negócio para a Sompo

- **ROI Imediato:** O investimento médio de ~R$ 300 por kit é amortizado na primeira intervenção preventiva que evita uma retífica de motor ou um princípio de incêndio de R$ 100k+.
- **Redução Agressiva da Sinistralidade:** Mitigação drástica de perdas totais em colheitadeiras e tratores de alta potência.
- **Diferencial Competitivo em Apólices:** A Sompo pode oferecer descontos no prêmio do seguro para frotas que adotarem o MAIA, atraindo os melhores clientes do agronegócio por operar com base em dados de risco reais.
- **Fidelização e Upsell Automatizado:** Identificação de carências de cobertura em tempo real, gerando campanhas de cross-sell customizadas para o gestor da frota.

---

## 🧪 Validação Prática

Para fins de testes acadêmicos e demonstração da Sprint 4 sem a exigência de montagem física de bancada, o repositório disponibiliza um **Simulador de Telemetria via Terminal**, que injeta dados diretamente na API reproduzindo o comportamento exato do ESP32:

### Operação Normal:
```bash
python3 -m iot.simulador_terminal normal
```

### Simulação de Superaquecimento (Risco de Incêndio / Alerta Sompo):
```bash
python3 -m iot.simulador_terminal superaquecido
```
