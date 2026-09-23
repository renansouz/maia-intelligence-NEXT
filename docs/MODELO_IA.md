# 🤖 MAIA — Metodologia e Motor de Inteligência Artificial

Este documento descreve a arquitetura, a fundamentação estatística e os modelos de Machine Learning implementados no MAIA para garantir a integridade, a explicabilidade e a evolução progressiva da saúde operacional das frotas agrícolas.

---

## 1. O Conceito Fundamental: O que o Modelo Responde?

A premissa central do nosso motor de Inteligência Artificial é responder objetivamente à seguinte questão:

> **"Esta máquina está operando de forma aderente ao comportamento considerado normal para ela?"**

O modelo **não prevê sinistros arbitrários**, não assegura falhas catastróficas iminentes e o seu _score_ não deve ser interpretado como uma probabilidade estática de quebra.

O sistema analisa os dados de telemetria recebidos da unidade e quantifica o desvio do comportamento atual em relação ao padrão estatístico aprendido. A arquitetura de inteligência divide-se em duas camadas complementares:

```text
DADOS DA MÁQUINA (CAN / J1939)
             │
             ▼
   MODELO OPERACIONAL (Isolation Forest)
             │
             ▼
   Score Operacional (0–100)
             │
             ▼
   SCORE CONTEXTUAL (Regras e Fatores Externos)
             │
             ├── Manutenção preventiva/corretiva
             ├── Idade do ativo
             ├── Condições ambientais e geoespaciais
             └── Feedback qualitativo do operador
             │
             ▼
   SCORE GLOBAL DA MÁQUINA (0–100)
```

1. **Saúde Operacional:** Derivada diretamente do aprendizado de máquina multivariado sobre os sinais CAN.
2. **Saúde Global (Contextual):** Agrega o resultado operacional a fatores exógenos e operacionais da máquina.

---

## 2. As Variáveis CAN Utilizadas (J1939)

O primeiro modelo operacional processa simultaneamente sete variáveis críticas de telemetria:

| Variável CAN (`J1939`)    | Descrição Técnica                               |
| :------------------------ | :---------------------------------------------- |
| `EngCoolantTemp`          | Temperatura do líquido de arrefecimento         |
| `EngOilTemp1`             | Temperatura do óleo do motor                    |
| `EngOilPress`             | Pressão do óleo                                 |
| `ActualEngine_PercTorque` | Percentual de torque e esforço exigido do motor |
| `EngineSpeed`             | Rotação por minuto (RPM)                        |
| `EngFuelRate`             | Taxa de consumo instantâneo de combustível      |
| `WheelBasedVehicleSpeed`  | Velocidade de deslocamento da máquina           |

### Abordagem Multivariada

O motor de IA não avalia essas variáveis de forma isolada. Uma temperatura de 80 °C de arrefecimento, por exemplo, possui significados distintos dependendo da carga do motor (torque), da rotação e da temperatura do óleo naquele exato instante. O modelo avalia o **conjunto estatístico** para determinar se a combinação observada pertence ou não ao espaço de normalidade aprendido.

---

## 3. Fundamentação Científica: Por que Isolation Forest e RobustScaler?

### A Escolha do Algoritmo (`Isolation Forest`)

Em ambientes operacionais reais, não dispós de bases massivas de dados históricos contendo rótulos explícitos de falha estruturada (_ex: "linha 1 = superaquecimento", "linha 2 = bomba de óleo travada"_). Treinar classificadores supervisionados sob essas condições geraria vieses graves.

Por essa razão, empregamos **Isolation Forest**, um algoritmo não supervisionado focado em **detecção de anomalias**. De forma simplificada, o algoritmo isola observações selecionando aleatoriamente uma feature e um ponto de divisão. Anomalias exigem menos partições para serem isoladas do que pontos normais, permitindo pontuar o grau de desvio sem exigir rótulos prévios de falha. Um desvio indica que o comportamento difere do padrão aprendido e requer inspeção humana.

### O Tratamento de Escalas (`RobustScaler`)

Como as variáveis possuem naturezas numéricas díspares (ex: RPM na casa de milhares vs. velocidade em unidades simples), empregamos o `RobustScaler`. Ele dimensiona os dados utilizando estatísticas robustas a _outliers_ (mediana e intervalo interquartil), prevenindo que sinais de maior amplitude numérica dominem indevidamente a função de distância do modelo.

---

## 4. O Conhecimento Inicial e o Perfil Evolutivo

Na ausência inicial de um histórico plurianual de frotas da Sompo, a linha de base (_baseline_) inicial foi calibrada com dados públicos reais de operação agrícola coletados via barramento CAN do trator **Tümosan 81.110 Powershuttle**.

Para evitar o engessamento analítico de assumir que toda máquina agrícola opera exatamente igual a um Tümosan, o sistema implementa uma **Evolução de Perfil por Unidade**:

```text
INITIAL ─────────► ADAPTING ─────────► INDIVIDUAL
(Baseline Tümosan)  (Histórico Parcial)  (Padrão Próprio da Unidade)
```

- **INITIAL:** A máquina recém-integra o sistema e utiliza a referência corporativa padrão.
- **ADAPTING:** O ativo acumula histórico próprio suficiente para iniciar a parametrização de um modelo candidato da unidade.
- **INDIVIDUAL:** Após validação estatística, o perfil operacional passa a refletir estritamente o comportamento histórico daquele trator específico.

---

## 5. Interpretabilidade e Explicabilidade (SHAP / Desvios)

Para atender às exigências de auditoria de uma seguradora, o resultado numérico bruto não é aceito como resposta final. O sistema compara a leitura atual com os limites percentis robustos do perfil (`P05`, `Mediana`, `P95`):

```text
Exemplo:
Leitura de Pressão do Óleo = 220 kPa
Referência do Perfil (Mediana) = 300 kPa (Faixa segura P05–P95: 260 - 340)
Resultado: Desvio apontado → Pressão de óleo abaixo da banda padrão.
```

Essa explicabilidade traduz-se diretamente na interface web em formato legível para gestores e operadores.

---

## 6. O Modelo Contextual e a Saúde Global

O **Score Contextual** atua como uma camada secundária de regras ponderadas que modulam o resultado puramente operacional com variáveis exógenas:

- **Manutenção:** Dias decorridos desde a última intervenção técnica.
- **Idade:** Ano de fabricação e tempo de uso do ativo.
- **Ambiente:** Condições exógenas de temperatura e umidade.
- **Feedback do Operador:** Registros qualitativos inseridos via tickets de campo (ex: ruídos atípicos, fumaça, vibração).

O resultado consolidado produz o **Score Global da Máquina (0 a 100)**, entregando uma visão sistêmica e equilibrada entre telemetria pura e contexto de campo.

---

## 7. Em Andamento: Integração do Módulo de Solo Úmido e Alagamento (Sentinel-1 / GEE)

> **Status:** Em fase de consolidação e testes de integração com o backend.

Paralelamente ao modelo de saúde mecânica CAN, o projeto incorpora a camada geoespacial de risco ambiental baseada em dados de satélite originados do projeto _Vigia.IA_:

- **Radar SAR (Sentinel-1 - Bandas VV/VH):** Monitoramento orbital com capacidade de atravesar nuvens e tempestades, avaliando o retroespalhamento da superfície para identificar saturação e alagamento de solo.
- **APIs Complementares:** Integração com _Open-Meteo_ (precipitação acumulada) e _GloFAS_ (vazão de bacias hidrográficas).
- **Objetivo da Feature:** Detectar condições críticas de solo úmido e proximidade de corpos d'água (< 30 metros), acionando as cláusulas particulares de operação de risco da apólice da Sompo.

---

<p align="center"><i>Documentação técnica oficial — Machine Learning Core — MAIA 2026</i></p>
