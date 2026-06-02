# 🚜 SompoRisk AI — Manual Técnico do Projeto

## 📌 Sobre o Projeto

A **SompoRisk AI** é uma Prova de Conceito (POC) desenvolvida para identificar e prever riscos operacionais em operações agrícolas utilizando:

* dados climáticos históricos reais;
* dados operacionais simulados;
* indicadores operacionais binários;
* banco de dados Oracle;
* pré-processamento de dados;
* Machine Learning com Árvore de Decisão;
* futura visualização em dashboard.

O objetivo do projeto é transformar decisões reativas em decisões preventivas, permitindo identificar cenários de risco antes da ocorrência de acidentes, falhas operacionais ou perdas financeiras.

---

# 🏗 Estrutura Atual do Projeto

```txt
somporisk-ai-challenge/
│
├── sompo-risk-config/
│   ├── api_clima.py
│   ├── gerar_dataset.py
│   ├── pre_processamento.py
│   │
│   └── machine_learning/
│       ├── preparar_features.py
│       ├── treinar_arvore.py
│       └── prever_risco.py
│
├── models/
│   ├── arvore_decisao.pkl
│   └── features.pkl
│
├── docs/
│   ├── arquitetura/
│   ├── backend/
│   ├── dataset/
│   └── ml/
│
├── .env
├── .gitignore
├── requirements.txt
├── README-project.md
└── README.md
```

---

# 📍 Fluxo Completo do Projeto

```txt
Open-Meteo API
      ↓
api_clima.py
      ↓
gerar_dataset.py
      ↓
Oracle Database
(TB_RISCO_AGRICOLA)
      ↓
pre_processamento.py
      ↓
Oracle Database
(TB_RISCO_AGRICOLA_TRATADO)
      ↓
preparar_features.py
      ↓
treinar_arvore.py
      ↓
models/arvore_decisao.pkl
      ↓
prever_risco.py
      ↓
Dashboard
```

---

# 1️⃣ api_clima.py

## Objetivo

Responsável pela comunicação com a API Open-Meteo.

Esse módulo busca:

* coordenadas geográficas;
* temperatura histórica;
* precipitação histórica;
* datas de medição.

### Funções Principais

#### buscar_coordenadas()

Converte uma cidade em latitude e longitude.

#### buscar_clima_historico_intervalo()

Consulta dados climáticos históricos entre:

```txt
01/01/2024 até a data atual
```

Retornando:

* data;
* temperatura;
* precipitação.

---

# 2️⃣ gerar_dataset.py

## Objetivo

Criar a base de dados operacional do projeto.

Responsabilidades:

* buscar dados climáticos históricos;
* gerar dados operacionais simulados;
* criar indicadores binários;
* armazenar os registros no Oracle.

## Indicadores Binários

```txt
INDICADOR_CHUVA_ALTA
INDICADOR_SOLO_UMIDO
INDICADOR_VELOCIDADE_ALTA
INDICADOR_PERTO_AGUA
INDICADOR_INCLINACAO_ALTA
INDICADOR_MANUTENCAO_ATRASADA
```

Valores:

```txt
0 = condição ausente
1 = condição presente
```

Esses indicadores serão utilizados pelo modelo de Machine Learning.

---

# 3️⃣ pre_processamento.py

## Objetivo

Preparar os dados para o treinamento dos modelos.

### Entrada

```txt
TB_RISCO_AGRICOLA
```

### Processos executados

* remoção de duplicidades;
* tratamento de dados ausentes;
* validação de faixas numéricas;
* padronização de datas;
* padronização de textos;
* preparação para Machine Learning.

### Saída

```txt
TB_RISCO_AGRICOLA_TRATADO
```

---

# 4️⃣ Machine Learning

## Objetivo

Treinar um modelo capaz de prever riscos operacionais a partir dos dados tratados.

### Modelo Utilizado

```txt
DecisionTreeClassifier
(Árvore de Decisão)
```

---

## preparar_features.py

Responsável por:

* carregar dados tratados;
* transformar datas;
* criar atributos temporais;
* criar a variável alvo de treinamento;
* separar X e y.

### Features Utilizadas

```txt
temperatura
chuva_mm
umidade_solo
velocidade_kmh
proximidade_agua_m
inclinacao_graus
tempo_uso_horas
manutencao_dias

indicador_chuva_alta
indicador_solo_umido
indicador_velocidade_alta
indicador_perto_agua
indicador_inclinacao_alta
indicador_manutencao_atrasada

ano
mes
dia
dia_semana
```

---

## treinar_arvore.py

Responsável por:

* dividir treino e teste;
* treinar a Árvore de Decisão;
* calcular métricas;
* salvar o modelo treinado.

Arquivos gerados:

```txt
models/arvore_decisao.pkl
models/features.pkl
```

---

## prever_risco.py

Responsável por:

* carregar o modelo treinado;
* receber novos dados;
* gerar previsão;
* retornar probabilidades por classe.

Exemplo de saída:

```json
{
  "risco_previsto": "alto",
  "probabilidades": {
    "alto": 0.87,
    "medio": 0.11,
    "baixo": 0.02
  }
}
```

---

# 🗄 Banco de Dados

O projeto utiliza Oracle Database.

Variáveis carregadas pelo arquivo `.env`:

```txt
ORACLE_USER
ORACLE_PASSWORD
ORACLE_HOST
ORACLE_PORT
ORACLE_SERVICE
```

## Tabelas

### TB_RISCO_AGRICOLA

Armazena os dados brutos.

### TB_RISCO_AGRICOLA_TRATADO

Armazena os dados tratados.

---

# ▶ Como Executar

## Instalar Dependências

```bash
pip install -r requirements.txt
```

---

## Gerar Dataset

```bash
python sompo-risk-config/gerar_dataset.py
```

---

## Executar Pré-processamento

```bash
python sompo-risk-config/pre_processamento.py
```

---

## Preparar Features

```bash
python sompo-risk-config/machine_learning/preparar_features.py
```

---

## Treinar Modelo

```bash
python sompo-risk-config/machine_learning/treinar_arvore.py
```

---

## Realizar Previsões

```bash
python sompo-risk-config/machine_learning/prever_risco.py
```

---

# 📊 Dashboard (Próxima Etapa)

O dashboard será responsável por:

* visualização dos indicadores;
* visualização das previsões;
* ranking de equipamentos críticos;
* acompanhamento temporal;
* monitoramento operacional.

---

# 📌 Resumo

Atualmente o projeto possui:

✅ integração com Open-Meteo
✅ Oracle Database
✅ geração de dataset histórico
✅ indicadores binários
✅ pré-processamento estruturado
✅ engenharia de features
✅ Machine Learning com Árvore de Decisão
✅ previsão de risco operacional
✅ documentação técnica estruturada
