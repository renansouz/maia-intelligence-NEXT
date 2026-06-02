# ⚙️ Documentação do Backend — SompoRisk AI

## Objetivo

Este documento descreve a camada backend atual do projeto **SompoRisk AI**.

O backend é responsável por:

* coletar dados climáticos históricos reais via API Open-Meteo;
* gerar dados operacionais simulados;
* criar indicadores binários para Machine Learning;
* persistir dados no Oracle Database;
* realizar limpeza e padronização dos dados;
* preparar os dados para treinamento do modelo;
* treinar modelos de Machine Learning;
* realizar previsões de risco operacional.

Nesta versão, o projeto já possui um pipeline completo de dados, desde a coleta climática até a geração de previsões através de Inteligência Artificial.

---

# 🏗 Arquitetura Backend

Fluxo atual:

```txt
Open-Meteo API
      ↓
api_clima.py
      ↓
gerar_dataset.py
      ↓
TB_RISCO_AGRICOLA
      ↓
pre_processamento.py
      ↓
TB_RISCO_AGRICOLA_TRATADO
      ↓
preparar_features.py
      ↓
treinar_arvore.py
      ↓
arvore_decisao.pkl
      ↓
prever_risco.py
      ↓
Dashboard
```

---

# 📁 Estrutura

```txt
sompo-risk-config/
│
├── api_clima.py
├── gerar_dataset.py
├── pre_processamento.py
│
└── machine_learning/
    ├── preparar_features.py
    ├── treinar_arvore.py
    └── prever_risco.py
```

---

# 🛠 Stack Utilizada

## Linguagem

```txt
Python 3.x
```

## Bibliotecas Principais

```txt
requests
pandas
oracledb
python-dotenv
scikit-learn
joblib
numpy
datetime
```

---

# 🔐 Variáveis de Ambiente

As credenciais do Oracle são armazenadas em um arquivo `.env`.

Exemplo:

```env
ORACLE_USER=seu_usuario
ORACLE_PASSWORD=sua_senha
ORACLE_HOST=oracle.fiap.com.br
ORACLE_PORT=1521
ORACLE_SERVICE=ORCL
```

O arquivo `.env` deve permanecer no `.gitignore`.

---

# 1️⃣ api_clima.py

## Responsabilidade

Responsável pela comunicação com a API pública Open-Meteo.

Esse módulo realiza a obtenção dos dados climáticos históricos utilizados no projeto.

---

## Funções Principais

### buscar_coordenadas(cidade)

Converte uma cidade em latitude e longitude.

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

### buscar_clima_historico_intervalo(latitude, longitude)

Busca dados históricos entre:

```txt
01/01/2024 até a data atual
```

Retornando:

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

## Benefícios

* separação de responsabilidades;
* facilidade de manutenção;
* facilidade de troca da API futuramente;
* reutilização em outros módulos.

---

# 2️⃣ gerar_dataset.py

## Responsabilidade

Construir a base de dados operacional do projeto e persistir os dados no Oracle Database.

Tabela de destino:

```txt
TB_RISCO_AGRICOLA
```

---

## Dados Utilizados

### Dados Reais

Obtidos pela Open-Meteo:

```txt
data_medicao
temperatura
chuva_mm
```

---

### Dados Simulados

```txt
umidade_solo
velocidade_kmh
proximidade_agua_m
inclinacao_graus
tempo_uso_horas
manutencao_dias
```

---

## Indicadores Binários

São criados indicadores auxiliares para uso no Machine Learning:

```txt
indicador_chuva_alta
indicador_solo_umido
indicador_velocidade_alta
indicador_perto_agua
indicador_inclinacao_alta
indicador_manutencao_atrasada
```

Valores possíveis:

```txt
0 = condição ausente
1 = condição presente
```

---

## Objetivo dos Indicadores

Os indicadores ajudam o modelo a identificar eventos importantes de forma mais clara.

Eles não representam o risco final.

O objetivo é fornecer sinais adicionais para que a Inteligência Artificial aprenda padrões operacionais.

---

# 3️⃣ pre_processamento.py

## Responsabilidade

Preparar os dados para o treinamento dos modelos.

Entrada:

```txt
TB_RISCO_AGRICOLA
```

Saída:

```txt
TB_RISCO_AGRICOLA_TRATADO
```

---

## Etapas Executadas

### Limpeza

Remove:

* duplicidades;
* registros inválidos;
* valores ausentes.

---

### Padronização

Padroniza:

```txt
cidade
data_medicao
tipos numéricos
```

---

### Conversões

Utiliza:

```python
pd.to_numeric()
pd.to_datetime()
```

---

### Regras de Sanidade

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

## Resultado

Geração da tabela:

```txt
TB_RISCO_AGRICOLA_TRATADO
```

Base oficial para treinamento dos modelos.

---

# 4️⃣ Machine Learning

## Objetivo

Prever riscos operacionais utilizando Inteligência Artificial.

---

## Modelo Atual

```txt
DecisionTreeClassifier
(Árvore de Decisão)
```

A escolha foi realizada pela simplicidade de interpretação e facilidade de explicação das decisões do modelo.

---

# preparar_features.py

Responsável por:

* carregar dados tratados;
* criar atributos temporais;
* preparar features;
* criar variável alvo;
* separar X e y.

---

## Features Utilizadas

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

# treinar_arvore.py

Responsável por:

* divisão treino/teste;
* treinamento do modelo;
* cálculo de métricas;
* persistência do modelo.

Arquivos gerados:

```txt
models/arvore_decisao.pkl
models/features.pkl
```

---

# prever_risco.py

Responsável por:

* carregar modelo treinado;
* receber novos dados;
* realizar previsões;
* retornar probabilidades.

Exemplo:

```json
{
  "risco_previsto": "alto",
  "probabilidade": 0.87
}
```

---

# 🗄 Banco de Dados

O projeto utiliza Oracle Database.

---

## Tabelas Principais

### TB_RISCO_AGRICOLA

Armazena:

* dados climáticos reais;
* dados simulados;
* indicadores binários.

---

### TB_RISCO_AGRICOLA_TRATADO

Armazena:

* dados limpos;
* dados padronizados;
* dados preparados para IA.

---

# ▶ Execução

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

## Executar Previsões

```bash
python sompo-risk-config/machine_learning/prever_risco.py
```

---

# ⚠ Tratamento de Erros

## API indisponível

Possíveis causas:

* timeout;
* indisponibilidade da Open-Meteo;
* ausência de internet.

Melhorias futuras:

```txt
retry automático
cache persistente
fallback local
```

---

## Oracle indisponível

Possíveis causas:

* credenciais incorretas;
* .env ausente;
* indisponibilidade do banco.

---

## Tabelas inexistentes

Erro comum:

```txt
ORA-00942: table or view does not exist
```

Solução:

* verificar existência da tabela;
* validar permissões.

---

# Limitações Atuais

✅ Oracle integrado
✅ Open-Meteo integrado
✅ Indicadores binários
✅ Pré-processamento estruturado
✅ Machine Learning implementado
✅ Árvore de Decisão treinável

Ainda não possui:

❌ Dashboard final
❌ API REST própria
❌ Processamento em tempo real
❌ Autenticação de usuários

---

# Evolução Planejada

## Machine Learning

Próximas melhorias:

* validação cruzada;
* ajuste de hiperparâmetros;
* comparação com Random Forest;
* comparação com XGBoost;
* explicabilidade do modelo;
* treinamento com dados reais de sinistros.

---

## API

Tecnologias candidatas:

```txt
FastAPI
Flask
```

Possíveis rotas:

```txt
POST /prever-risco
GET /equipamentos
GET /dashboard
```

---

## Dashboard

Planejado:

* gráficos;
* filtros;
* ranking de risco;
* monitoramento operacional;
* indicadores em tempo real.

---

# 📌 Resumo

O backend atual fornece toda a base operacional da solução:

✅ integração com Open-Meteo
✅ geração de dataset climático-operacional
✅ indicadores binários
✅ Oracle Database
✅ pré-processamento estruturado
✅ engenharia de features
✅ treinamento de Árvore de Decisão
✅ previsão de risco operacional
✅ persistência de modelos
✅ base preparada para dashboard

---

## 📦 Versão Atual

```txt
v2.1.0
```
