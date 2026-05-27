# ⚙️ Documentação do Backend — SompoRisk AI

## Objetivo

Este módulo documenta a camada backend atual do projeto **SompoRisk AI**.

O backend é responsável por:

- coleta de dados externos;
- geração do dataset;
- tratamento e limpeza dos dados;
- cálculo de score de risco;
- preparação para Machine Learning.

Nesta etapa, o backend ainda opera em modo batch (execução manual), mas foi estruturado para futura evolução para processamento automatizado e em tempo real.

---

# Arquitetura backend

Fluxo atual:

```txt
Open-Meteo API
      ↓
api_clima.py
      ↓
gerar_dataset.py
      ↓
dataset_risco_agricola.csv
      ↓
pre_processamento.py
      ↓
dataset_tratado.csv
      ↓
Machine Learning
```

---

# Estrutura

```txt
sompo-risk-config/
│
├── api_clima.py
├── gerar_dataset.py
└── pre_processamento.py
```

---

# Stack utilizada

## Linguagem

```txt
Python 3.x
```

---

## Bibliotecas

```txt
requests
pandas
pathlib
datetime
random
```

---

# 1️⃣ api_clima.py

## Responsabilidade

Comunicação com a API pública Open-Meteo.

Responsável por:

- geocodificação;
- consulta climática;
- retorno estruturado.

---

## Funções

### buscar_coordenadas(cidade)

Converte cidade em latitude/longitude.

Entrada:

```python
cidade = "São Paulo"
```

Saída:

```python
{
    "latitude": -23.55,
    "longitude": -46.63
}
```

---

## buscar_clima_historico_intervalo(latitude, longitude)

Busca histórico climático.

Entrada:

```python
latitude
longitude
```

Consulta:

```txt
01/01/2024 até data atual
```

Retorno:

```python
[
    {
        "data": "2025-02-11",
        "temperatura": 27.3,
        "chuva_mm": 18.2
    }
]
```

---

## Papel no sistema

Esse módulo funciona como gateway externo.

Ele desacopla:

```txt
API externa ↔ aplicação
```

Isso facilita:

- manutenção;
- troca de fornecedor;
- testes;
- mocks futuros.

---

# 2️⃣ gerar_dataset.py

## Responsabilidade

Construção do dataset operacional.

Esse módulo combina:

- dados reais;
- dados simulados;
- regras de negócio.

---

# Fluxo interno

## 1. Seleção de cidades

Lista atual:

```txt
São Paulo
Campinas
Ribeirão Preto
Sorocaba
Piracicaba
Araraquara
São José dos Campos
Ribeirão Pires
Taquaritinga
```

---

## 2. Busca histórica

Para cada cidade:

```txt
buscar coordenadas
↓
buscar clima histórico
↓
armazenar em cache
```

---

## Cache

Objetivo:

reduzir chamadas API.

Sem cache:

```txt
1 request por registro
```

Com cache:

```txt
1 request por cidade
```

Benefícios:

- velocidade;
- menor consumo;
- menos risco de timeout;
- menos rate limit.

---

## 3. Geração simulada

Variáveis simuladas:

```txt
umidade_solo
velocidade_kmh
proximidade_agua_m
inclinacao_graus
tempo_uso_horas
manutencao_dias
```

Motivo:

ainda não existem sensores físicos reais.

---

## 4. Regra inicial

Função:

```python
classificar_risco()
```

Critérios:

```txt
chuva alta
solo úmido
velocidade elevada
proximidade de água
inclinação
manutenção
```

Saída:

```txt
baixo
medio
alto
```

---

# Saída

Arquivo:

```txt
csvs/dataset_risco_agricola.csv
```

---

# 3️⃣ pre_processamento.py

## Responsabilidade

Preparar os dados para Machine Learning.

---

# Etapas

## Leitura

Entrada:

```txt
dataset_risco_agricola.csv
```

---

## Limpeza

Remove:

- duplicados;
- registros corrompidos;
- valores nulos;
- inconsistências.

---

## Padronização

Normaliza:

cidade:

```txt
São Paulo
```

risco:

```txt
alto
medio
baixo
```

datas:

```txt
datetime
```

---

## Conversão

Converte tipos numéricos.

Exemplo:

```python
pd.to_numeric()
```

---

## Sanidade

Filtra valores absurdos.

Exemplos:

```txt
temperatura > 60
chuva > 300
velocidade > 100
```

---

## Score

Função:

```python
calcular_score_risco()
```

Saída:

```txt
0–100
```

---

## Classificação final

Função:

```python
classificar_por_score()
```

Saída:

```txt
baixo
medio
alto
```

---

# Saída

Arquivo:

```txt
csvs/dataset_tratado.csv
```

---

# Execução

## Instalação

```bash
pip install -r requirements.txt
```

---

## Pipeline completo

### Dataset

```bash
python sompo-risk-config/gerar_dataset.py
```

---

### Tratamento

```bash
python sompo-risk-config/pre_processamento.py
```

---

# Tratamento de erros

## API indisponível

Problemas:

- timeout;
- sem internet;
- indisponibilidade Open-Meteo.

Impacto:

falha na coleta.

Mitigação futura:

```txt
retry
fallback
cache persistente
```

---

## CSV inexistente

Erro:

```python
FileNotFoundError
```

Solução:

executar geração primeiro.

---

## Dados inválidos

Tratamento:

```txt
dropna
filtros
normalização
```

---

# Limitações atuais

Nesta fase:

❌ sem API REST própria  
❌ sem banco persistente  
❌ sem autenticação  
❌ sem filas  
❌ sem execução automática  
❌ sem logs estruturados  

---

# Evolução planejada

Próximas melhorias:

## API própria

FastAPI / Flask:

```txt
POST /prever-risco
GET /dashboard
```

---

## Banco

Possíveis:

- PostgreSQL
- Firebase
- MongoDB

---

## Automação

Scheduler:

```txt
cron
celery
worker
```

---

## Tempo real

Futuro:

```txt
ESP32
MQTT
WebSocket
```

---

# Resumo

O backend atual fornece a base operacional do projeto:

✅ integração externa  
✅ dataset híbrido  
✅ regras de negócio  
✅ pipeline de preparação  
✅ dados prontos para IA
