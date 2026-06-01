# 🚜 SompoRisk AI — Manual Técnico do Projeto

## 📌 Sobre o projeto

A **SompoRisk AI** é uma prova de conceito (POC) desenvolvida para identificar e prever riscos operacionais em operações agrícolas utilizando:

- dados climáticos históricos reais;
- dados operacionais simulados;
- indicadores operacionais binários;
- banco de dados Oracle;
- pré-processamento de dados;
- preparação para Machine Learning;
- futura visualização em dashboard.

O objetivo do projeto é transformar decisões reativas em decisões preventivas, permitindo identificar cenários de risco antes da ocorrência de acidentes, falhas operacionais ou perdas financeiras.

---

# 🏗 Estrutura atual do projeto

```txt
somporisk-ai-challenge/
│
├── sompo-risk-config/
│   ├── api_clima.py
│   ├── gerar_dataset.py
│   └── pre_processamento.py
│
├── docs/
│   ├── backend/
│   ├── dataset/
│   └── arquitetura/
│
├── .env
├── .gitignore
├── requirements.txt
├── README-project.md
└── README.md
```

---

# 📍 Fluxo completo do projeto

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
Machine Learning
      ↓
Dashboard
```

---

# 1️⃣ api_clima.py

## Objetivo

Responsável pela comunicação com a API Open-Meteo.

Esse módulo busca:

- coordenadas geográficas;
- temperatura histórica;
- precipitação histórica;
- datas de medição.

---

## Funções principais

### buscar_coordenadas()

Converte uma cidade em latitude e longitude.

### buscar_clima_historico_intervalo()

Consulta dados históricos entre:

```txt
01/01/2024 até a data atual
```

Retornando:

- data;
- temperatura;
- chuva.

---

# 2️⃣ gerar_dataset.py

## Objetivo

Criar a base de dados operacional do projeto.

Diferentemente das versões anteriores, este módulo não calcula mais score de risco nem classificação final.

A responsabilidade dele agora é:

- gerar dados;
- enriquecer dados;
- criar indicadores binários;
- armazenar tudo no Oracle.

---

## Dados climáticos

Obtidos da Open-Meteo:

- temperatura média diária;
- precipitação diária;
- data da medição.

---

## Dados operacionais simulados

- umidade do solo;
- velocidade da máquina;
- proximidade de água;
- inclinação;
- tempo de uso;
- manutenção.

---

## Indicadores binários

Os indicadores representam condições operacionais importantes.

Exemplos:

```txt
INDICADOR_CHUVA_ALTA
INDICADOR_SOLO_UMIDO
INDICADOR_VELOCIDADE_ALTA
INDICADOR_PERTO_AGUA
INDICADOR_INCLINACAO_ALTA
INDICADOR_MANUTENCAO_ATRASADA
```

Valores possíveis:

```txt
0 = condição ausente
1 = condição presente
```

Esses indicadores serão utilizados futuramente pelos modelos de Machine Learning.

---

## Persistência

Os dados gerados são armazenados na tabela:

```txt
TB_RISCO_AGRICOLA
```

---

# 3️⃣ pre_processamento.py

## Objetivo

Preparar os dados para a etapa de Machine Learning.

---

## Entrada

Tabela:

```txt
TB_RISCO_AGRICOLA
```

---

## Limpeza

Remove:

- registros duplicados;
- valores ausentes;
- inconsistências;
- tipos inválidos.

---

## Padronização

Padroniza:

- cidade;
- datas;
- tipos numéricos.

---

## Validações

Exemplos:

```txt
temperatura entre -10 e 60
chuva entre 0 e 300
umidade_solo entre 0 e 100
velocidade entre 0 e 100
tempo_uso_horas entre 0 e 24
manutencao_dias entre 0 e 365
```

---

## Saída

Tabela:

```txt
TB_RISCO_AGRICOLA_TRATADO
```

Essa tabela será utilizada pelo Machine Learning.

---

# 🗄 Banco de Dados

O projeto utiliza Oracle Database.

Variáveis carregadas do arquivo `.env`:

```txt
ORACLE_USER
ORACLE_PASSWORD
ORACLE_HOST
ORACLE_PORT
ORACLE_SERVICE
```

---

## Tabelas

### TB_RISCO_AGRICOLA

Armazena os dados brutos.

### TB_RISCO_AGRICOLA_TRATADO

Armazena os dados tratados.

---

# ▶ Como executar

## Instalar dependências

```bash
pip install -r requirements.txt
```

---

## Gerar dataset

```bash
python sompo-risk-config/gerar_dataset.py
```

---

## Executar pré-processamento

```bash
python sompo-risk-config/pre_processamento.py
```

---

# 🤖 Machine Learning (próxima etapa)

A próxima fase do projeto será responsável por:

- leitura da tabela tratada;
- definição da variável alvo;
- treinamento do modelo;
- avaliação de métricas;
- previsão de risco operacional.

Possíveis algoritmos:

- Random Forest;
- Logistic Regression;
- XGBoost.

---

# 📊 Dashboard (futuro)

Será desenvolvido para:

- visualização dos indicadores;
- análise operacional;
- acompanhamento dos riscos previstos;
- monitoramento em tempo real.

---

# 📌 Resumo

Atualmente o projeto já possui:

✅ integração com Open-Meteo  
✅ Oracle Database  
✅ geração de dataset  
✅ indicadores binários  
✅ pré-processamento estruturado  
✅ documentação técnica  
✅ base preparada para Machine Learning
