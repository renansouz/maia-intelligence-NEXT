# 📚 Documentação Técnica — SompoRisk AI

## Sobre

Esta pasta centraliza toda a documentação técnica e evolutiva do projeto **SompoRisk AI**.

O objetivo é manter histórico técnico, decisões arquiteturais, documentação dos módulos e evolução das funcionalidades ao longo das versões do projeto.


## 📌 Visão Geral

Pipeline completo de dados e IA que monitora, processa e prevê riscos operacionais:

```
Open-Meteo API
      ↓
api_clima.py         ← coleta climática histórica
      ↓
gerar_dataset.py     ← gera dataset híbrido (real + simulado)
      ↓
TB_RISCO_AGRICOLA    ← Oracle Database
      ↓
pre_processamento.py ← limpeza e validação
      ↓
TB_RISCO_AGRICOLA_TRATADO
      ↓
preparar_features.py ← engenharia de features
      ↓
treinar_arvore.py    ← treinamento da Árvore de Decisão
      ↓
arvore_decisao.pkl
      ↓
prever_risco.py      ← previsão por cidade
      ↓
gerar_explicacao_modelo.py    ← Gera uma explicação do por que daquilo
      ↓
TB_PREVISAO_RISCO
      ↓
Dashboard.py         ← Streamlit
```

---

## 🗂️ Estrutura do Repositório

```
somporisk-ai-challenge/
│
├── sompo-risk-config/
│   ├── api_clima.py
│   ├── gerar_dataset.py
│   ├── pre_processamento.py
│   ├── dashboard.py
│   └── machine_learning/
│       ├── preparar_features.py
│       ├── treinar_arvore.py
│       ├── prever_risco.py
│       └── gerar_explicacao_modelo.py
│
├── models/
│   ├── arvore_decisao.pkl
│   └── features.pkl
│
├── docs/
|   └── README-DOCS.md      ← Documentação completa e resumida do projeto
│
├── .env                    ← credenciais Oracle (não versionado)
├── env.example
├── requirements.txt
└── README.md
```

---

## 📊 Dataset

Dataset **híbrido** com dois tipos de dados:

**Dados Reais** — via API Open-Meteo (desde 01/01/2024):
- temperatura média diária
- precipitação (mm)
- data da medição

**Dados Simulados** — gerados em Python:
- umidade do solo, velocidade (km/h), proximidade de água (m)
- inclinação do terreno (graus), tempo de uso (horas), dias desde a última manutenção

**Indicadores Binários** (usados pelo modelo de ML):

| Indicador | Regra |
|---|---|
| `INDICADOR_CHUVA_ALTA` | chuva_mm > 30 |
| `INDICADOR_SOLO_UMIDO` | umidade_solo > 70% |
| `INDICADOR_VELOCIDADE_ALTA` | velocidade_kmh > 18 |
| `INDICADOR_PERTO_AGUA` | proximidade_agua_m < 100 |
| `INDICADOR_INCLINACAO_ALTA` | inclinacao_graus > 15° |
| `INDICADOR_MANUTENCAO_ATRASADA` | manutencao_dias > 90 |

**Cidades monitoradas:** São Paulo, Campinas, Ribeirão Preto, Sorocaba, Piracicaba, Araraquara, São José dos Campos, Ribeirão Pires e Taquaritinga.

---

## 🤖 Machine Learning

**Modelo:** `DecisionTreeClassifier` (scikit-learn)

Escolhido por ser interpretável, leve e adequado para POC acadêmica — as decisões da árvore podem ser explicadas diretamente ao usuário final.

**Variável alvo:** `ocorrencia_risco` (0 = baixo, 1 = alto), criada de forma probabilística com base nos indicadores:

```python
if total_indicadores >= 4:   probabilidade = 0.75
elif total_indicadores >= 2: probabilidade = 0.35
else:                        probabilidade = 0.08

ocorrencia_risco = int(random.random() < probabilidade)
```

**Configuração do modelo:**
```python
DecisionTreeClassifier(criterion="gini", max_depth=5, random_state=42)
# Divisão: 75% treino / 25% teste
```

**Métricas avaliadas:** Accuracy, Precision, Recall, F1-Score e Matriz de Confusão.

**Saída de previsão:**
```json
{
  "cidade": "São Paulo",
  "risco_previsto": 1,
  "classificacao": "alto",
  "probabilidades": { "0": 0.4731, "1": 0.5269 }
}
```

**Explicabilidade:** O módulo `gerar_explicacao_modelo.py` traduz a previsão em linguagem humana, identificando quais fatores contribuíram e gerando recomendações operacionais (ex: "Realizar manutenção preventiva", "Evitar operação em áreas úmidas").

---

## 🗄️ Banco de Dados

Oracle Database com três tabelas principais:

| Tabela | Conteúdo |
|---|---|
| `TB_RISCO_AGRICOLA` | Dados brutos (climáticos + operacionais + indicadores) |
| `TB_RISCO_AGRICOLA_TRATADO` | Dados limpos e preparados para IA |
| `TB_PREVISAO_RISCO` | Previsões geradas pelo modelo |

---

## 🛠️ Tecnologias

**Backend:** Python 3.x, Pandas, NumPy, Requests, python-dotenv, oracledb

**Machine Learning:** scikit-learn, joblib

**Visualização:** Streamlit, Plotly

**Banco de Dados:** Oracle Database

**API Climática:** Open-Meteo (gratuita, sem autenticação)

---

## ▶️ Como Executar

### 1. Instalar dependências
```bash
pip install -r requirements.txt
```

### 2. Configurar credenciais Oracle
```bash
# Renomear env.example para .env e preencher:
ORACLE_USER=seu_usuario
ORACLE_PASSWORD=sua_senha
ORACLE_HOST=oracle.fiap.com.br
ORACLE_PORT=1521
ORACLE_SERVICE=ORCL
```

### 3. Executar o pipeline completo
```bash
# Gerar dataset
python sompo-risk-config/gerar_dataset.py

# Pré-processamento
python sompo-risk-config/pre_processamento.py

# Preparar features
python sompo-risk-config/machine_learning/preparar_features.py

# Treinar modelo
python sompo-risk-config/machine_learning/treinar_arvore.py

# Realizar previsões
python sompo-risk-config/machine_learning/prever_risco.py

# Abrir dashboard
python -m streamlit run sompo-risk-config/Dashboard.py
```

---

## 📈 Dashboard

Implementado em Streamlit, o dashboard oferece:

- monitoramento centralizado dos equipamentos por cidade
- visualização do risco previsto pelo modelo (baixo / alto)
- ranking de equipamentos com maior probabilidade de incidente
- mapa de riscos por município
- indicadores operacionais e ambientais
- filtros por período e cidade
- alertas críticos para apoio à decisão

---

## ✅ Status do Projeto

| Módulo | Status |
|---|---|
| Arquitetura e escopo | ✅ Concluído |
| Integração Open-Meteo | ✅ Concluído |
| Geração do dataset | ✅ Concluído |
| Oracle Database | ✅ Concluído |
| Pré-processamento | ✅ Concluído |
| Machine Learning (Árvore de Decisão) | ✅ Concluído |
| Previsão de risco + persistência | ✅ Concluído |
| Dashboard Streamlit | ✅ Concluído |
| Explicabilidade do modelo | ✅ Concluído |
| Integração Gemini AI | 🔄 Em desenvolvimento |
| Alertas por e-mail | 🔄 Em desenvolvimento |
| Dados reais de sinistros | 🗓️ Futuro |
| Random Forest / XGBoost | 🗓️ Futuro |

---

## 🔐 Segurança

- credenciais armazenadas exclusivamente em `.env` (fora do versionamento)
- validações de integridade nos dados antes do treinamento
- modelo versionado e rastreável via arquivos `.pkl`

---
