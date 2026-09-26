# 🤖 MAIA — Metodologia e Motores de Inteligência Artificial

Este documento descreve a arquitetura, a fundamentação estatística e os dois modelos de Machine Learning implementados no MAIA para garantir a integridade, a explicabilidade preditiva e a prevenção holística de riscos nas frotas agrícolas seguradas pela Sompo.

---

## 🧭 Visão Geral dos Dois Motores

O MAIA não confia em uma única fonte de dados para avaliar o risco de um maquinário agrícola. A inteligência do sistema divide-se em duas frentes independentes e complementares:

```text
                                  ┌────────────────────────────────────────┐
                                  │         DADOS DA FROTA & CAMPO         │
                                  └───────────────────┬────────────────────┘
                                                      │
                         ┌────────────────────────────┴────────────────────────────┐
                         ▼                                                         ▼
        ┌───────────────────────────────────┐                     ┌───────────────────────────────────┐
        │  MOTOR 1: SAÚDE OPERACIONAL (CAN) │                     │  MOTOR 2: CONDIÇÃO AMBIENTAL (PCA)│
        │  - Barramento J1939 (Trator)      │                     │  - Sentinel-1 SAR (Radar)         │
        │  - Isolation Forest + RobustScaler│                     │  - Sentinel-2, SRTM, SoilGrids    │
        │  - Fatores SHAP & Desvios Mecânicos│                    │  - Análise Multivariada de Terreno│
        └─────────────────┬─────────────────┘                     └─────────────────┬─────────────────┘
                          │                                                         │
                          └────────────────────────────┬────────────────────────────┘
                                                       ▼
                                      ┌───────────────────────────────────┐
                                      │   SCORE GLOBAL DE RISCO DO ATIVO  │
                                      │   (Operacional + Ambiental +      │
                                      │    Contexto de Apólice / Clima)   │
                                      └───────────────────────────────────┘
```

---

# PARTE I — Motor de Saúde Operacional (Mecânica e CAN)

## 1. O Conceito Fundamental

A premissa central do motor operacional é responder objetivamente à seguinte questão:

> **"Esta máquina está operando de forma aderente ao comportamento considerado normal para ela?"**

O modelo **não prevê sinistros arbitrários**, não assegura falhas catastróficas iminentes e o seu _score_ não é uma probabilidade estática de quebra. Ele analisa a telemetria CAN e quantifica o desvio do comportamento atual em relação ao padrão aprendido.

---

## 2. As Variáveis CAN Utilizadas (J1939)

O primeiro modelo processa simultaneamente sete variáveis críticas de telemetria coletadas do barramento da máquina:

| Variável CAN (`J1939`)    | Descrição Técnica                               |
| :------------------------ | :---------------------------------------------- |
| `EngCoolantTemp`          | Temperatura do líquido de arrefecimento         |
| `EngOilTemp1`             | Temperatura do óleo do motor                    |
| `EngOilPress`             | Pressão do óleo                                 |
| `ActualEngine_PercTorque` | Percentual de torque e esforço exigido do motor |
| `EngineSpeed`             | Rotação por minuto (RPM)                        |
| `EngFuelRate`             | Taxa de consumo instantâneo de combustível      |
| `WheelBasedVehicleSpeed`  | Velocidade de deslocamento da máquina           |

O motor avalia o **conjunto estatístico multivariado** (ex: temperatura de 80°C associada a torque alto e RPM específica) para determinar se a combinação pertence ao espaço de normalidade.

---

## 3. Fundamentação Científica: Isolation Forest e RobustScaler

- **Isolation Forest:** Em ambientes reais, não dispomos de bases massivas rotuladas com falhas mecânicas específicas. Empregamos aprendizado não supervisionado (_Isolation Forest_) para isolar anomalias. Pontos que exigem menos partições para serem isolados recebem maior índice de atipicidade.
- **RobustScaler:** Normaliza variáveis com escalas díspares (ex: RPM na casa de milhares vs. velocidade em unidades simples) utilizando estatísticas robustas a _outliers_ (mediana e intervalo interquartil).

---

## 4. O Conhecimento Inicial e o Perfil Evolutivo

Na ausência de um histórico plurianual de frotas da Sompo, a linha de base (_baseline_) inicial foi calibrada com dados públicos reais de operação agrícola coletados via CAN do trator **Tümosan 81.110 Powershuttle**. O sistema implementa uma **Evolução de Perfil por Unidade**:

```text
INITIAL ─────────► ADAPTING ─────────► INDIVIDUAL
(Baseline Tümosan)  (Histórico Parcial)  (Padrão Próprio da Unidade)
```

---

## 5. Explicabilidade (SHAP e Desvios)

Para atender às exigências de auditoria de uma seguradora, o resultado compara a leitura atual com os limites percentis robustos do perfil (`P05`, `Mediana`, `P95`), traduzindo o desvio em fatores textuais legíveis para gestores e operadores na interface web.

---

# PARTE II — Motor de Condição Ambiental e Satelital (PCA)

## 1. O Conceito Fundamental

Enquanto o motor operacional olha para dentro da máquina, o **Score Ambiental** avalia o cenário externo. O objetivo é responder:

> **"A condição ambiental observada agora é parecida ou diferente do padrão histórico que conhecemos para esta localização exata?"**

Como não existe um _target_ ambiental único de atolamento rotulado, o problema foi modelado de forma não supervisionada utilizando **PCA (_Principal Component Analysis_)**.

---

## 2. Fontes de Dados e Racionalidade (EDA Ambiental)

O modelo ambiental funde dados de múltiplas fontes geoespaciais e meteorológicas extraídas via Google Earth Engine e APIs públicas:

1. **Sentinel-1 (Radar SAR - Bandas VV/VH):** Emite pulsos de micro-ondas insensíveis a nuvens e tempestades, permitindo acompanhar mudanças no retroespalhamento e umidade da superfície do solo.
2. **Sentinel-2 (Óptico - NDWI / NDMI):** Índices de vegetação e água superficial, utilizados como contexto complementar dentro de uma tolerância temporal de dias.
3. **Open-Meteo (Histórico Meteorológico):** Precipitação acumulada em janelas de memória temporal móvel (`rain_3d_mm`, `rain_7d_mm`, `rain_14d_mm`), dias desde a última chuva e umidade de reanálise do solo (`soil_moisture_0_7cm`).
4. **JRC Global Surface Water:** Contexto histórico de ocorrência, sazonalidade e distância até corpos d'água permanentes ou temporários.
5. **SRTM (Topografia):** Elevação média, declividade do terreno, relevo local e elevação relativa.
6. **SoilGrids (Propriedades do Solo):** Estimativas espaciais de textura (teor de argila, areia e silte) e densidade aparente.

---

## 3. O Pipeline de Modelagem Ambiental (PCA)

- **Eixo Temporal Principal:** Cada passagem válida do Sentinel-1 serve como ancora temporal, integrada ao clima do dia, à imagem do Sentinel-2 mais próxima e às características estáticas locais.
- **Padronização e Redução:** As features passam por um `StandardScaler` e em seguida por um `PCA` treinado para reter **90% da variância explicada acumulada**.
- **Cálculo da Atipicidade:** A distância euclidiana/Mahalanobis normalizada no espaço dos componentes principais é comparada com a distribuição histórica da área.
- **Score Final:** O sistema calcula o **`score_condicao_ambiental` (0 a 100)** (`100 - Índice de Atipicidade Percentílica`) e classifica a condição em faixas interpretáveis pelo negócio (_Condição Estável e Segura_, _Atenção: Solo Instável_, _Crítico: Risco de Atolamento_).

---

# PARTE III — Orquestração e Consumo no MAIA

Na arquitetura de microsserviços do MAIA, ambos os motores operam de forma isolada e otimizada:

- **`ml_service.py`** gerencia a inferência operacional (CAN) sob demanda nas requisições de telemetria.
- **`environmental_service.py`** consulta a base persistida (`TB_ML_AMBIENTAL`) com base na coordenada da fazenda, avalia o modelo PCA ambiental treinado e entrega o índice de estabilidade do terreno.
- **Frontend (`detalhe-maquina.js`)** exibe de forma unificada o Dossiê do Ativo, contendo o Gráfico Gauge Mecânico (XAI) ao lado do Card de Condição do Solo e Terreno (Satélite SAR).

---

<p align="center"><i>Documentação técnica oficial — Core de Inteligência Artificial e Ciência de Dados — MAIA 2026</i></p>
