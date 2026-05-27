# 🚜 SompoRisk AI — Manual Técnico do Projeto

## 📌 Sobre o projeto

A **SompoRisk AI** é uma prova de conceito (POC) desenvolvida para prever riscos operacionais em operações agrícolas utilizando:

- dados climáticos históricos reais;
- dados operacionais simulados;
- regras de negócio;
- pré-processamento de dados;
- preparação para Machine Learning;
- futura visualização em dashboard.

O objetivo do projeto é transformar decisões reativas em decisões preventivas, permitindo identificar cenários de risco antes da ocorrência de acidentes, falhas operacionais ou perdas financeiras.

---

# 📊 Tipo de Dataset

Este projeto utiliza um **dataset híbrido**.

Ou seja:

- **dados climáticos históricos reais** obtidos via API Open-Meteo;
- **dados operacionais simulados** gerados via Python.

Essa abordagem permite construir cenários realistas mesmo sem sensores físicos conectados nesta etapa da prova de conceito.

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
├── csvs/
│   ├── dataset_risco_agricola.csv
│   └── dataset_tratado.csv
│
├── docs/
│   └── SompoRiskAI_Arquitetura.pdf
│
├── .gitignore
├── LICENSE
├── requirements.txt
├── README-project.md
└── README.md
```

---

# 📍 Fluxo completo do projeto

O funcionamento atual segue esta sequência:

```txt
1. api_clima.py
        ↓
2. gerar_dataset.py
        ↓
3. csvs/dataset_risco_agricola.csv
        ↓
4. pre_processamento.py
        ↓
5. csvs/dataset_tratado.csv
        ↓
6. Machine Learning
        ↓
7. Dashboard
```

---

# 1️⃣ api_clima.py

## Objetivo

Responsável pela comunicação com a API pública **Open-Meteo**.

Esse módulo busca dados climáticos históricos reais que serão usados para enriquecer o dataset principal.

---

## O que esse arquivo faz

### Buscar coordenadas da cidade

Transforma o nome de uma cidade em latitude e longitude.

Exemplo:

```python
buscar_coordenadas("São Paulo")
```

Retorno:

```python
{
    "latitude": -23.55,
    "longitude": -46.63
}
```

---

### Buscar clima histórico

Consulta dados climáticos históricos entre:

```txt
01/01/2024 até a data atual do sistema
```

Retorna:

- temperatura média diária;
- volume de chuva;
- data da medição.

Exemplo:

```python
buscar_clima_historico_intervalo(latitude, longitude)
```

Retorno:

```python
[
    {
        "data": "2025-04-12",
        "temperatura": 24.8,
        "chuva_mm": 12.3
    }
]
```

---

## Observação importante

Esse arquivo **não gera datasets**.

Sua única responsabilidade é fornecer dados climáticos para outros módulos do projeto.

---

# 2️⃣ gerar_dataset.py

## Objetivo

Responsável por criar o dataset principal do projeto.

Arquivo gerado:

```txt
./csvs/dataset_risco_agricola.csv
```

---

## O que esse arquivo faz

### Etapa 1 — Buscar dados climáticos históricos

Para cada cidade cadastrada:

- busca coordenadas geográficas;
- consulta histórico climático;
- armazena os dados em cache.

Isso melhora drasticamente a performance.

### Sem cache

```txt
1 chamada para cada registro gerado
```

Exemplo:

```txt
300 registros = 300 chamadas
```

### Com cache

```txt
1 chamada por cidade
```

Exemplo:

```txt
9 cidades = 9 chamadas
```

---

### Etapa 2 — Gerar dados operacionais simulados

São gerados dados fictícios que simulam comportamento operacional da máquina:

- umidade do solo;
- velocidade;
- proximidade de água;
- inclinação do terreno;
- tempo de uso;
- manutenção.

Esses dados representam cenários realistas de operação.

---

### Etapa 3 — Calcular classificação inicial de risco

A função:

```python
classificar_risco()
```

faz uma classificação inicial baseada em regras de negócio.

Exemplo:

```python
if chuva_mm > 30:
    pontos += 2
```

Critérios avaliados:

- chuva alta;
- solo muito úmido;
- velocidade elevada;
- proximidade com água;
- inclinação acentuada;
- manutenção atrasada.

Resultado possível:

```txt
baixo
medio
alto
```

---

## Colunas geradas

```txt
equipamento_id
cidade
data_medicao
temperatura
chuva_mm
umidade_solo
velocidade_kmh
proximidade_agua_m
inclinacao_graus
tempo_uso_horas
manutencao_dias
risco
```

---

# 3️⃣ pre_processamento.py

## Objetivo

Preparar os dados para a etapa de Machine Learning.

Arquivo gerado:

```txt
./csvs/dataset_tratado.csv
```

---

## O que esse arquivo faz

### Carregamento do dataset

Lê o dataset bruto:

```txt
dataset_risco_agricola.csv
```

---

### Limpeza de dados

Remove:

- registros duplicados;
- valores ausentes;
- dados inválidos;
- tipos incorretos.

---

### Padronização

Padroniza informações textuais:

Cidade:

```txt
são paulo → São Paulo
```

Risco:

```txt
ALTO → alto
```

Data:

```txt
string → datetime
```

---

### Conversão numérica

Converte corretamente colunas numéricas:

- temperatura;
- chuva;
- velocidade;
- inclinação;
- manutenção;
- tempo de uso;
- proximidade de água;
- umidade do solo.

---

### Regras de sanidade

Remove valores fora da realidade.

Exemplos:

```txt
temperatura < -10
temperatura > 60
velocidade > 100
chuva > 300
tempo_uso > 24
```

---

### Score de risco

Cria:

```python
score_risco
```

Faixa:

```txt
0 até 100
```

Exemplo:

- chuva alta → +20
- solo úmido → +20
- velocidade alta → +20
- proximidade com água → +20

---

### Classificação final

Cria:

```python
classificacao_risco
```

Regras:

```txt
>= 70 → alto
>= 40 → medio
< 40 → baixo
```

---

## Saída final

O dataset final terá colunas adicionais:

```txt
score_risco
classificacao_risco
```

---

# ▶ Como executar

## 1. Instalar dependências

```bash
pip install pandas requests scikit-learn matplotlib seaborn
```

Ou:

```bash
pip install -r requirements.txt
```

---

## 2. Gerar dataset bruto

Executar:

```bash
python sompo-risk-config/gerar_dataset.py
```

Saída:

```txt
csvs/dataset_risco_agricola.csv
```

---

## 3. Realizar pré-processamento

Executar:

```bash
python sompo-risk-config/pre_processamento.py
```

Saída:

```txt
csvs/dataset_tratado.csv
```

---

# ⚠ Possíveis erros comuns

## FileNotFoundError

Erro:

```python
FileNotFoundError
```

Causa:

Dataset bruto ainda não foi criado.

Solução:

```bash
python sompo-risk-config/gerar_dataset.py
```

---

## ModuleNotFoundError

Erro:

```python
ModuleNotFoundError
```

Causa:

Dependências não instaladas.

Solução:

```bash
pip install -r requirements.txt
```

---

## Timeout / erro na API

Possíveis causas:

- internet indisponível;
- timeout;
- indisponibilidade da Open-Meteo.

Solução:

Verificar conexão e tentar novamente.

---

# 📌 Próximas etapas

## Machine Learning

Será implementado:

- split treino/teste;
- encoding;
- normalização;
- Random Forest;
- Logistic Regression;
- métricas de avaliação;
- matriz de confusão;
- análise de performance.

---

## Dashboard

Será implementado:

- visualização de score de risco;
- gráficos analíticos;
- indicadores operacionais;
- alertas preventivos;
- monitoramento visual.

---
