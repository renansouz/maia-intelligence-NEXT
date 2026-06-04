# 🤖 Documentação de Machine Learning e Explicabilidade — SompoRisk AI

## Objetivo

Este documento descreve a etapa de **Machine Learning** do projeto **SompoRisk AI**.

O objetivo desta fase é construir um modelo capaz de prever risco operacional em operações agrícolas a partir dos dados tratados no banco Oracle, além de fornecer explicações claras sobre os fatores que influenciaram cada previsão.

Nesta versão, o modelo escolhido é uma **Árvore de Decisão**, utilizando a classe:

```python
DecisionTreeClassifier
```

A Árvore de Decisão foi escolhida por ser simples, interpretável, leve e adequada para uma primeira versão da prova de conceito.

---

## Principais entregas desta versão

* leitura da tabela tratada no Oracle;
* preparação de features;
* criação da variável alvo probabilística;
* treinamento com Árvore de Decisão;
* avaliação do modelo;
* salvamento do modelo treinado;
* previsão por cidade;
* consulta do último registro da cidade no banco;
* retorno de classificação e probabilidades;
* geração de explicações para as previsões;
* geração de recomendações operacionais.

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
gerar_explicacao_modelo.py
      ↓
API REST
      ↓
Dashboard Streamlit
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
│   ├── prever_risco.py
│   └── gerar_explicacao_modelo.py
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

* é fácil de explicar;
* permite interpretação das decisões;
* funciona bem com dados tabulares;
* aceita variáveis numéricas e binárias;
* possui baixo custo computacional;
* é adequada para uma POC acadêmica;
* permite futura análise de importância das variáveis.

---

# 🎯 Variável Alvo

## Problema

O dataset atual não possui uma variável real de ocorrência, como:

* acidente registrado;
* sinistro real;
* falha mecânica real;
* ocorrência operacional validada.

Por isso, para permitir o treinamento supervisionado, foi criada uma variável alvo sintética e probabilística.

---

## Variável criada

```txt
ocorrencia_risco
```

Valores possíveis:

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

Cada indicador pode assumir:

```txt
0 = condição ausente
1 = condição presente
```

---

## Regra probabilística

```txt
4 ou mais indicadores ativos → 75% de chance de ocorrência
2 ou 3 indicadores ativos   → 35% de chance de ocorrência
0 ou 1 indicador ativo      → 8% de chance de ocorrência
```

Implementação:

```python
if total_indicadores >= 4:
    probabilidade = 0.75
elif total_indicadores >= 2:
    probabilidade = 0.35
else:
    probabilidade = 0.08
```

Posteriormente:

```python
ocorrencia_risco = int(random.random() < probabilidade)
```

---

# ✅ Por que essa abordagem melhora o modelo?

Antes, o risco era definido diretamente pela soma dos indicadores.

Isso fazia o modelo apenas reproduzir uma regra fixa.

Com a variável probabilística:

```txt
Nem toda condição perigosa gera um incidente.

Porém, quanto mais condições perigosas estiverem presentes,
maior é a probabilidade de ocorrência de um evento de risco.
```

Isso torna o comportamento do modelo mais próximo de um cenário operacional real.

---

# 1️⃣ preparar_features.py

## Responsabilidade

Responsável por preparar os dados utilizados no treinamento.

### Etapas realizadas

* leitura da tabela tratada;
* padronização de colunas;
* conversão de datas;
* criação de atributos temporais;
* criação da variável alvo;
* separação de features e target.

---

## Atributos temporais criados

A partir da coluna:

```txt
data_medicao
```

são criadas:

```txt
ano
mes
dia
dia_semana
```

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

```python
X
y
features
df
```

---

# 2️⃣ treinar_arvore.py

## Responsabilidade

Treinar a Árvore de Decisão.

---

## Etapas executadas

1. Carregamento dos dados.
2. Divisão treino/teste.
3. Treinamento do modelo.
4. Avaliação.
5. Salvamento dos artefatos.

---

## Divisão treino/teste

```txt
75% treino
25% teste
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

* Accuracy
* Precision
* Recall
* F1-Score
* Matriz de Confusão

---

## Arquivos gerados

```txt
models/arvore_decisao.pkl
models/features.pkl
```

---

# 3️⃣ prever_risco.py

## Responsabilidade

Realizar previsões utilizando o modelo treinado.

---

## Fluxo

```txt
Cidade
 ↓
Validação
 ↓
Consulta Oracle
 ↓
Último registro
 ↓
Criação dos indicadores
 ↓
Modelo treinado
 ↓
Previsão
 ↓
Resultado
```

---

## Saída

Exemplo:

```json
{
    "cidade": "São Paulo",
    "risco_previsto": 1,
    "classificacao": "alto",
    "probabilidades": {
        "0": 0.4731,
        "1": 0.5269
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

```txt
baixo
alto
```

---

## probabilidades

Exemplo:

```txt
0: 47,31% → Baixo risco
1: 52,69% → Alto risco
```

---

# 🔍 Explicabilidade da IA

## Objetivo

Além de prever riscos, o sistema busca explicar de forma transparente os fatores que influenciaram cada decisão.

O objetivo é permitir que gestores e operadores entendam:

* por que o risco foi classificado como alto ou baixo;
* quais fatores contribuíram para a previsão;
* quais ações preventivas podem ser adotadas.

---

## Indicadores utilizados na explicação

```txt
indicador_chuva_alta
indicador_solo_umido
indicador_velocidade_alta
indicador_perto_agua
indicador_inclinacao_alta
indicador_manutencao_atrasada
```

---

## Regras dos indicadores

| Indicador           | Regra                    |
| ------------------- | ------------------------ |
| Chuva Alta          | chuva_mm > 30            |
| Solo Úmido          | umidade_solo > 70        |
| Velocidade Alta     | velocidade_kmh > 18      |
| Próximo da Água     | proximidade_agua_m < 100 |
| Inclinação Alta     | inclinacao_graus > 15    |
| Manutenção Atrasada | manutencao_dias > 90     |

---

## Exemplos de interpretação

### Chuva elevada + solo úmido

```txt
Chuva > 30 mm
Umidade > 70%
```

Interpretação:

> A combinação de chuva elevada e solo excessivamente úmido aumenta o risco de atolamento, reduz a tração do equipamento e dificulta a execução segura das operações agrícolas.

---

### Chuva elevada + proximidade de corpos d'água

```txt
Chuva > 30 mm
Distância da água < 100 m
```

Interpretação:

> A alta precipitação associada à proximidade de rios ou áreas alagáveis aumenta a probabilidade de encharcamento do terreno.

---

### Manutenção atrasada

```txt
Manutenção > 90 dias
```

Interpretação:

> Equipamentos com manutenção atrasada possuem maior probabilidade de falhas mecânicas e interrupções não planejadas.

---

### Inclinação elevada

```txt
Inclinação > 15°
```

Interpretação:

> Terrenos inclinados aumentam a instabilidade operacional e exigem maior cuidado durante a operação.

---

### Velocidade elevada

```txt
Velocidade > 18 km/h
```

Interpretação:

> Velocidades elevadas reduzem o tempo de reação diante de situações inesperadas.

---

## Exemplo completo

Entrada:

```txt
Chuva: 45 mm
Umidade do solo: 82%
Manutenção: 120 dias
```

Resultado:

```txt
Classificação: Alto Risco
Probabilidade: 87,40%
```

Explicação:

> O equipamento foi classificado como Alto Risco devido à presença simultânea de chuva elevada, solo excessivamente úmido e manutenção atrasada.

> A combinação de chuva acima de 30 mm e umidade superior a 70% aumenta significativamente a probabilidade de atolamento e perda de tração durante a operação.

> Além disso, a manutenção superior a 90 dias aumenta a probabilidade de falhas mecânicas e interrupções não planejadas, elevando o risco operacional total.

---

## Recomendações geradas

Exemplos:

```txt
Monitorar condições climáticas.

Evitar operação em áreas excessivamente úmidas.

Realizar manutenção preventiva.

Reduzir velocidade em terrenos inclinados.

Redobrar atenção em regiões próximas a corpos d'água.
```

---

## Benefícios

A camada de explicabilidade permite:

* justificar previsões;
* aumentar a confiança dos usuários;
* apoiar auditorias;
* facilitar tomadas de decisão;
* transformar previsões em ações preventivas.

---

# 🗄 Relação com o Oracle

O treinamento utiliza:

```txt
TB_RISCO_AGRICOLA_TRATADO
```

Essa tabela é produzida pelo processo de pré-processamento.

O modelo não utiliza diretamente a tabela bruta para evitar:

* registros duplicados;
* valores inconsistentes;
* dados inválidos;
* valores ausentes.

---

# ⚠️ Limitações atuais

* variável alvo sintética;
* ausência de sinistros reais;
* ausência de histórico validado de falhas;
* API ainda em desenvolvimento;
* dashboard ainda em evolução.

---

# 🚀 Evoluções futuras

## Dados reais

Substituir o alvo sintético por:

```txt
ocorrencia_falha
sinistro
acidente
risco_validado
```

---

## Persistência das previsões

Criar tabela:

```txt
TB_PREVISAO_RISCO
```

---

## Dashboard

Exibir:

* risco previsto;
* probabilidades;
* fatores de risco;
* explicações da IA;
* recomendações;
* mapas;
* tendências temporais.

---

## API REST

Exemplo:

```http
GET /explicacao/{cidade}
```

Resposta:

```json
{
  "cidade": "São Paulo",
  "classificacao": "alto",
  "probabilidade_alto": 0.87,
  "fatores_risco": [
    "Chuva elevada",
    "Solo úmido",
    "Manutenção atrasada"
  ],
  "explicacao": [
    "A combinação dos fatores aumenta o risco de atolamento."
  ],
  "recomendacoes": [
    "Realizar manutenção preventiva."
  ]
}
```

---

# 📌 Resumo

A camada de Machine Learning adiciona ao projeto:

✅ preparação de features
✅ variável alvo probabilística
✅ treinamento com Árvore de Decisão
✅ avaliação do modelo
✅ integração com Oracle
✅ previsão por cidade
✅ retorno de probabilidades
✅ explicabilidade da IA
✅ recomendações operacionais
✅ base preparada para API e dashboard

O resultado é uma solução capaz não apenas de prever riscos operacionais, mas também de explicar os motivos da previsão e apoiar ações preventivas para redução de perdas.
