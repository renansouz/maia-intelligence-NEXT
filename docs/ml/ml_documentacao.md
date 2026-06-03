# 🤖 Documentação de Machine Learning — SompoRisk AI

## Objetivo

Este documento descreve a etapa de **Machine Learning** do projeto **SompoRisk AI**.

O objetivo desta fase é construir um modelo capaz de prever risco operacional em operações agrícolas a partir dos dados tratados no banco Oracle.

Nesta versão, o modelo escolhido é uma **Árvore de Decisão**, utilizando a classe:

```python
DecisionTreeClassifier
```

A Árvore de Decisão foi escolhida por ser simples, interpretável, leve e adequada para uma primeira versão da prova de conceito.

---

# 📌 Versão Atual

```txt
v2.2.0
```

Principais entregas desta versão:

- leitura da tabela tratada no Oracle;
- preparação de features;
- criação da variável alvo probabilística;
- treinamento com Árvore de Decisão;
- avaliação do modelo;
- salvamento do modelo treinado;
- previsão por cidade;
- consulta do último registro da cidade no banco;
- retorno de classificação e probabilidades.

---

# 🔄 Visão Geral do Fluxo

```txt
Oracle Database
TB_RISCO_AGRICOLA_TRATADO
      ↓
preparar_features.py
      ↓
features + ocorrencia_risco
      ↓
treinar_arvore.py
      ↓
modelo treinado
      ↓
models/arvore_decisao.pkl
models/features.pkl
      ↓
prever_risco.py
      ↓
consulta cidade no Oracle
      ↓
previsão de risco operacional
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
├── machine_learning/
│   ├── preparar_features.py
│   ├── treinar_arvore.py
│   └── prever_risco.py
│
└── models/
    ├── arvore_decisao.pkl
    └── features.pkl
```

---

# 🌳 Modelo Escolhido

## Árvore de Decisão

A Árvore de Decisão é um modelo supervisionado que aprende padrões a partir dos dados.

Ela divide os registros em decisões sucessivas, por exemplo:

```txt
chuva_mm > 30?
      ↓
velocidade_kmh > 18?
      ↓
umidade_solo > 70?
      ↓
previsão de risco
```

---

## Por que usar Árvore de Decisão?

A escolha desse modelo é adequada porque:

- é fácil de explicar;
- permite interpretação das decisões;
- funciona bem com dados tabulares;
- aceita variáveis numéricas e binárias;
- possui baixo custo computacional;
- é adequada para uma POC acadêmica;
- permite futura análise de importância das variáveis.

---

# 🎯 Variável Alvo

## Problema

O dataset atual não possui uma variável real de ocorrência, como:

- acidente registrado;
- sinistro real;
- falha mecânica real;
- ocorrência operacional validada.

Por isso, para permitir o treinamento supervisionado, foi criada uma variável alvo sintética e probabilística.

---

## Variável criada

A variável alvo utilizada é:

```txt
ocorrencia_risco
```

Ela assume dois valores:

```txt
0 = baixo risco / sem ocorrência simulada
1 = alto risco / ocorrência simulada
```

---

# 🧠 Como a variável alvo é criada?

A variável `ocorrencia_risco` é criada a partir dos indicadores binários.

Indicadores utilizados:

```txt
indicador_chuva_alta
indicador_solo_umido
indicador_velocidade_alta
indicador_perto_agua
indicador_inclinacao_alta
indicador_manutencao_atrasada
```

Cada indicador pode valer:

```txt
0 = condição ausente
1 = condição presente
```

A soma desses indicadores gera uma estimativa de exposição ao risco.

---

## Regra probabilística

A lógica utilizada é:

```txt
4 ou mais indicadores ativos → 75% de chance de ocorrência
2 ou 3 indicadores ativos   → 35% de chance de ocorrência
0 ou 1 indicador ativo      → 8% de chance de ocorrência
```

Exemplo conceitual:

```python
if total_indicadores >= 4:
    probabilidade = 0.75
elif total_indicadores >= 2:
    probabilidade = 0.35
else:
    probabilidade = 0.08
```

Depois, o sistema sorteia probabilisticamente se houve ou não ocorrência:

```python
ocorrencia_risco = int(random.random() < probabilidade)
```

---

# ✅ Por que essa abordagem melhora o modelo?

Antes, o risco era definido diretamente pela soma dos indicadores.

Isso fazia o modelo apenas reproduzir uma regra fixa.

Com a variável probabilística, o modelo passa a simular melhor a realidade:

```txt
Nem toda condição perigosa vira acidente.
Mas quanto mais condições perigosas existirem, maior é a chance de ocorrer um evento de risco.
```

Essa abordagem deixa a POC mais honesta e mais próxima de um cenário real.

---

# 1️⃣ preparar_features.py

## Responsabilidade

Este arquivo prepara os dados para o treinamento do modelo.

Ele realiza:

- leitura da tabela `TB_RISCO_AGRICOLA_TRATADO`;
- padronização dos nomes das colunas;
- conversão da data;
- criação de atributos temporais;
- criação da variável alvo `ocorrencia_risco`;
- separação entre `X` e `y`.

---

## Entrada

Tabela Oracle:

```txt
TB_RISCO_AGRICOLA_TRATADO
```

---

## Atributos temporais criados

A coluna:

```txt
data_medicao
```

é transformada em:

```txt
ano
mes
dia
dia_semana
```

Isso é necessário porque modelos de Machine Learning não interpretam datas diretamente.

---

## Features utilizadas

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

## Saída

O arquivo retorna:

```python
X
y
features
df
```

Onde:

- `X` representa as variáveis de entrada;
- `y` representa o alvo `ocorrencia_risco`;
- `features` representa a lista de colunas usadas no modelo;
- `df` representa o dataset preparado.

---

# 2️⃣ treinar_arvore.py

## Responsabilidade

Este arquivo treina a Árvore de Decisão.

---

## Etapas executadas

1. Carrega as features.
2. Divide os dados em treino e teste.
3. Cria o modelo `DecisionTreeClassifier`.
4. Treina o modelo.
5. Realiza previsões no conjunto de teste.
6. Calcula métricas.
7. Salva o modelo treinado.
8. Salva a lista de features usadas.

---

## Divisão treino/teste

A divisão usada é:

```txt
75% treino
25% teste
```

No código:

```python
train_test_split(
    X,
    y,
    test_size=0.25,
    random_state=42,
    stratify=y
)
```

---

## Modelo

```python
DecisionTreeClassifier(
    criterion="gini",
    max_depth=5,
    random_state=42
)
```

---

## Métricas utilizadas

O treinamento exibe:

- acurácia;
- precision;
- recall;
- f1-score;
- matriz de confusão.

---

## Arquivos gerados

```txt
models/arvore_decisao.pkl
models/features.pkl
```

Esses arquivos são artefatos do treinamento e podem ser recriados executando novamente o script `treinar_arvore.py`.

---

# 3️⃣ prever_risco.py

## Responsabilidade

Este arquivo utiliza o modelo treinado para prever o risco operacional.

Na versão atual, ele está conectado ao Oracle e pode realizar previsão por cidade.

---

## Fluxo de previsão por cidade

```txt
Cidade informada
      ↓
Validação da cidade
      ↓
Consulta ao Oracle
      ↓
Busca do último registro disponível
      ↓
Criação automática dos indicadores
      ↓
Carregamento do modelo
      ↓
Previsão
      ↓
Retorno da classificação e probabilidades
```

---

## Cidades válidas

Atualmente, o sistema trabalha com as cidades utilizadas na geração do dataset:

```txt
São Paulo
Campinas
Ribeirão Preto
Sorocaba
Piracicaba
Araraquara
São José Dos Campos
Ribeirão Pires
Taquaritinga
```

---

## Consulta utilizada

O sistema busca o último registro disponível da cidade:

```sql
SELECT
    CIDADE,
    DATA_MEDICAO,
    TEMPERATURA,
    CHUVA_MM,
    UMIDADE_SOLO,
    VELOCIDADE_KMH,
    PROXIMIDADE_AGUA_M,
    INCLINACAO_GRAUS,
    TEMPO_USO_HORAS,
    MANUTENCAO_DIAS
FROM TB_RISCO_AGRICOLA_TRATADO
WHERE CIDADE = :cidade
ORDER BY DATA_MEDICAO DESC
FETCH FIRST 1 ROW ONLY
```

---

## Saída esperada

Exemplo de saída:

```python
{
    "cidade": "São Paulo",
    "data_medicao": "2026-06-02 00:00:00",
    "risco_previsto": 1,
    "classificacao": "alto",
    "probabilidades": {
        0: 0.4731,
        1: 0.5269
    },
    "interpretacao": {
        "0": "baixo",
        "1": "alto"
    }
}
```

---

# 📊 Interpretação da saída

## risco_previsto

```txt
0 = baixo risco
1 = alto risco
```

---

## classificacao

Campo textual para facilitar leitura humana:

```txt
baixo
alto
```

---

## probabilidades

Representa o grau de confiança do modelo em cada classe.

Exemplo:

```txt
0: 0.4731 → 47,31% de chance de baixo risco
1: 0.5269 → 52,69% de chance de alto risco
```

---

# ▶ Como executar

## 1. Rodar o pré-processamento

Antes de treinar o modelo, é necessário garantir que a tabela tratada esteja atualizada.

```bash
python sompo-risk-config/pre_processamento.py
```

---

## 2. Testar preparação de features

```bash
python sompo-risk-config/machine_learning/preparar_features.py
```

---

## 3. Treinar a Árvore de Decisão

```bash
python sompo-risk-config/machine_learning/treinar_arvore.py
```

---

## 4. Testar previsão por cidade

```bash
python sompo-risk-config/machine_learning/prever_risco.py
```

---

# 📦 Dependências necessárias

Adicionar ao `requirements.txt`:

```txt
scikit-learn
joblib
```

Dependências já utilizadas no projeto:

```txt
pandas
oracledb
python-dotenv
```

---

# 🗄 Relação com o Oracle

O ML utiliza como base a tabela:

```txt
TB_RISCO_AGRICOLA_TRATADO
```

Essa tabela é gerada pelo arquivo:

```txt
pre_processamento.py
```

O treinamento não deve usar a tabela bruta diretamente, pois ela pode conter:

- dados duplicados;
- valores ausentes;
- tipos inconsistentes;
- registros inválidos.

---

# ⚠️ Limitações da versão atual

Nesta versão:

- a variável alvo ainda é sintética;
- o modelo ainda não utiliza dados reais de sinistros;
- ainda não existe tabela própria para armazenar previsões;
- ainda não há API REST de previsão;
- a integração com dashboard ainda está em desenvolvimento.

---

# 🚀 Evoluções futuras

## Melhorar a variável alvo

Substituir o alvo sintético por uma variável real, como:

```txt
ocorrencia_falha
sinistro
acidente
risco_validado
```

---

## Salvar previsões no banco

Criar tabela:

```txt
TB_PREVISAO_RISCO
```

Possíveis colunas:

```txt
ID_PREVISAO
CIDADE
DATA_MEDICAO
DATA_PREVISAO
RISCO_PREVISTO
CLASSIFICACAO
PROBABILIDADE_BAIXO
PROBABILIDADE_ALTO
MODELO_VERSAO
```

---

## Integrar com dashboard

O dashboard poderá exibir:

- risco previsto;
- probabilidade de cada classe;
- ranking de cidades críticas;
- ranking de equipamentos críticos;
- mapas de risco;
- evolução temporal.

---

## Criar API de previsão

Possível rota futura:

```txt
POST /prever-risco
```

Entrada:

```json
{
  "cidade": "São Paulo"
}
```

Saída:

```json
{
  "cidade": "São Paulo",
  "risco_previsto": 1,
  "classificacao": "alto",
  "probabilidade_alto": 0.5269
}
```

---

## Explicabilidade do modelo

Melhoria futura:

```python
modelo.feature_importances_
```

Isso permitirá identificar quais variáveis mais influenciaram a previsão.

---

# 📌 Resumo

A fase de Machine Learning adiciona ao projeto:

✅ preparação de features  
✅ variável alvo probabilística  
✅ treinamento com Árvore de Decisão  
✅ avaliação do modelo  
✅ salvamento do modelo treinado  
✅ previsão por cidade  
✅ integração com Oracle  
✅ retorno de probabilidades  
✅ base preparada para dashboard  

Essa etapa transforma o dataset tratado em uma base capaz de gerar previsões operacionais por cidade.
