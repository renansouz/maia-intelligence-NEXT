# 📊 Documentação do Dataset — SompoRisk AI

## Objetivo

Este documento descreve a estrutura, origem, tratamento e utilização do dataset do projeto **SompoRisk AI**.

O dataset reúne informações climáticas históricas e dados operacionais relacionados a operações agrícolas, servindo como base para análises, treinamento de modelos de Machine Learning e previsões de risco operacional.

Nesta versão do projeto, o dataset não possui mais classificação manual de risco nem score calculado por regras fixas. A identificação dos riscos é realizada pelo modelo de Machine Learning.

---

# 📌 Tipo de Dataset

O projeto utiliza um **dataset híbrido**, combinando:

## 🌦 Dados Climáticos Reais

Obtidos através da API pública Open-Meteo:

* temperatura média diária;
* precipitação diária;
* data da medição;
* localização geográfica.

---

## 🚜 Dados Operacionais Simulados

Gerados via Python para representar cenários agrícolas:

* umidade do solo;
* velocidade da máquina;
* proximidade de água;
* inclinação do terreno;
* tempo de uso;
* dias desde a última manutenção.

---

# 🎯 Justificativa da Abordagem

Nesta etapa da prova de conceito não existem sensores físicos conectados ao sistema.

Por esse motivo foi adotada uma abordagem híbrida:

* dados climáticos reais aumentam o realismo da solução;
* dados operacionais simulados permitem testar cenários;
* indicadores binários ajudam o modelo a identificar condições críticas;
* Oracle Database garante persistência dos dados.

---

# 🔄 Fluxo Atual do Dataset

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
Machine Learning
      ↓
prever_risco.py
      ↓
TB_PREVISAO_RISCO
      ↓
dashboard.py
```

---

# 📁 Arquivos Envolvidos

## api_clima.py

Responsável por:

* buscar coordenadas geográficas;
* consultar Open-Meteo;
* obter histórico climático;
* fornecer dados climáticos reais.

---

## gerar_dataset.py

Responsável por:

* percorrer as cidades cadastradas;
* buscar histórico climático;
* gerar variáveis operacionais;
* criar indicadores binários;
* armazenar dados no Oracle.

Tabela utilizada:

```txt
TB_RISCO_AGRICOLA
```

---

## pre_processamento.py

Responsável por:

* carregar dados do Oracle;
* remover duplicidades;
* validar dados;
* converter tipos;
* preparar os dados para IA.

Tabela de origem:

```txt
TB_RISCO_AGRICOLA
```

Tabela de destino:

```txt
TB_RISCO_AGRICOLA_TRATADO
```

---

## preparar_features.py

Responsável por:

* transformar datas em atributos temporais;
* selecionar features;
* preparar X e y;
* criar a base para treinamento.

---

## treinar_arvore.py

Responsável por:

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

* carregar o modelo;
* receber novos dados;
* prever risco operacional;
* retornar probabilidades.

Tabela de destino:

```txt
TB_PREVISAO_RISCO
```

---

## Dashboard.py

Responsável por:

* consultar dados do Oracle;
* exibir previsões de risco;
* monitorar equipamentos;
* apresentar indicadores e gráficos;
* apoiar decisões operacionais.

---

# 🌎 Fonte Climática

API utilizada:

```txt
Open-Meteo
```

Dados utilizados:

* temperatura média diária;
* precipitação diária;
* histórico climático.

Período utilizado:

```txt
01/01/2024 até a data atual
```

---

# 📍 Cidades Utilizadas

* São Paulo
* Campinas
* Ribeirão Preto
* Sorocaba
* Piracicaba
* Araraquara
* São José dos Campos
* Ribeirão Pires
* Taquaritinga

---

# 🗄 Estrutura da Tabela Bruta

Tabela:

```txt
TB_RISCO_AGRICOLA
```

Campos principais:

```txt
EQUIPAMENTO_ID
CIDADE
DATA_MEDICAO
TEMPERATURA
CHUVA_MM
UMIDADE_SOLO
VELOCIDADE_KMH
PROXIMIDADE_AGUA_M
INCLINACAO_GRAUS
TEMPO_USO_HORAS
MANUTENCAO_DIAS
```

Indicadores:

```txt
INDICADOR_CHUVA_ALTA
INDICADOR_SOLO_UMIDO
INDICADOR_VELOCIDADE_ALTA
INDICADOR_PERTO_AGUA
INDICADOR_INCLINACAO_ALTA
INDICADOR_MANUTENCAO_ATRASADA
```

---

# 🚨 Indicadores Binários

Os indicadores representam condições operacionais relevantes.

Valores:

```txt
0 = condição ausente
1 = condição presente
```

Indicadores atuais:

```python
indicador_chuva_alta = int(chuva_mm > 30)
indicador_solo_umido = int(umidade_solo > 70)
indicador_velocidade_alta = int(velocidade_kmh > 18)
indicador_perto_agua = int(proximidade_agua_m < 100)
indicador_inclinacao_alta = int(inclinacao_graus > 15)
indicador_manutencao_atrasada = int(manutencao_dias > 90)
```

---

# 🤖 Relação com Machine Learning

O modelo atual utiliza:

```txt
DecisionTreeClassifier
```

As principais features utilizadas são:

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
```

Além dos atributos temporais:

```txt
ano
mes
dia
dia_semana
```

---

# 🧹 Pré-processamento

Executado por:

```txt
pre_processamento.py
```

Etapas:

* remoção de duplicidades;
* conversão de datas;
* padronização textual;
* validação numérica;
* remoção de inconsistências.

---

# ✅ Validações Aplicadas

```txt
temperatura entre -10 e 60
chuva entre 0 e 300
umidade_solo entre 0 e 100
velocidade entre 0 e 100
proximidade_agua_m entre 0 e 5000
inclinacao_graus entre 0 e 90
tempo_uso_horas entre 0 e 24
manutencao_dias entre 0 e 365
```

---

# 🗄 Estrutura da Tabela Tratada

Tabela:

```txt
TB_RISCO_AGRICOLA_TRATADO
```

Contém:

* dados limpos;
* dados validados;
* dados preparados para Machine Learning.

---

# ▶ Como Executar

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

## Executar Previsão

```bash
python sompo-risk-config/machine_learning/prever_risco.py
```

---

# 🗄 Banco de Dados

Oracle Database.

Credenciais carregadas via:

```txt
.env
```

Variáveis:

```txt
ORACLE_USER
ORACLE_PASSWORD
ORACLE_HOST
ORACLE_PORT
ORACLE_SERVICE
```

---

# 🚀 Evoluções Futuras

## Machine Learning

* validação cruzada;
* ajuste de hiperparâmetros;
* comparação com Random Forest;
* comparação com XGBoost;
* explicabilidade do modelo.

## Sensores

* integração com ESP32;
* sensores reais;
* automação da coleta de dados.

---

# 📌 Resumo

O dataset atual fornece:

- ✅ Dados climáticos históricos reais
- ✅ Dados operacionais simulados
- ✅ Indicadores binários
- ✅ Oracle Database integrado
- ✅ Pré-processamento estruturado
- ✅ Engenharia de features
- ✅ Treinamento com Árvore de Decisão
- ✅ Previsão de risco operacional
- ✅ Persistência de dados e previsões
- ✅ Base preparada para dashboard analítico

---

## 📦 Versão Atual

```txt
v2.2.0
```
