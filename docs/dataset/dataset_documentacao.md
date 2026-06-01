# 📊 Documentação do Dataset — SompoRisk AI

## Objetivo

Este documento descreve a estrutura, origem, tratamento e uso do dataset do projeto **SompoRisk AI**.

O dataset tem como objetivo reunir informações climáticas e operacionais relacionadas a operações agrícolas, servindo como base para análises futuras e para o treinamento de modelos de Machine Learning.

Nesta nova abordagem, o dataset **não possui mais classificação manual de risco** nem cálculo de score por regra fixa. A previsão de risco será responsabilidade da etapa de Machine Learning.

---

# Tipo de dataset

O projeto utiliza um **dataset híbrido**.

Ou seja, ele combina:

## Dados climáticos reais

Obtidos por meio da API pública **Open-Meteo**:

- temperatura média diária;
- precipitação diária;
- data da medição;
- localização geográfica da cidade.

## Dados operacionais simulados

Gerados via Python para representar condições de operação agrícola:

- umidade do solo;
- velocidade da máquina;
- proximidade de água;
- inclinação do terreno;
- tempo de uso;
- dias desde a última manutenção.

---

# Justificativa da abordagem

Nesta etapa da prova de conceito, ainda não há sensores físicos reais conectados ao sistema.

Por isso, foi adotada uma abordagem híbrida:

- dados climáticos reais aumentam o realismo do dataset;
- dados operacionais simulados permitem criar cenários controlados;
- indicadores binários ajudam o futuro modelo de Machine Learning a identificar condições importantes;
- o banco Oracle permite persistir os dados para consulta, tratamento e modelagem.

---

# Fluxo atual do dataset

```txt
Open-Meteo API
      ↓
api_clima.py
      ↓
gerar_dataset.py
      ↓
Oracle Database
TB_RISCO_AGRICOLA
      ↓
pre_processamento.py
      ↓
Oracle Database
TB_RISCO_AGRICOLA_TRATADO
      ↓
Machine Learning
```

---

# Arquivos envolvidos

## api_clima.py

Responsável por:

- buscar coordenadas geográficas da cidade;
- consultar a API Open-Meteo;
- retornar histórico climático;
- fornecer dados climáticos reais para geração do dataset.

---

## gerar_dataset.py

Responsável por:

- percorrer as cidades cadastradas;
- buscar histórico climático real;
- gerar variáveis operacionais simuladas;
- criar indicadores binários;
- inserir os dados brutos no banco Oracle.

Tabela de destino:

```txt
TB_RISCO_AGRICOLA
```

---

## pre_processamento.py

Responsável por:

- carregar dados da tabela bruta;
- remover duplicidades;
- padronizar textos;
- converter datas;
- validar tipos numéricos;
- remover dados inconsistentes;
- salvar o dataset tratado no banco.

Tabela de origem:

```txt
TB_RISCO_AGRICOLA
```

Tabela de destino:

```txt
TB_RISCO_AGRICOLA_TRATADO
```

---

# Fonte climática

API utilizada:

```txt
Open-Meteo
```

Dados utilizados:

- temperatura média diária;
- precipitação diária;
- histórico climático.

Intervalo utilizado:

```txt
01/01/2024 até a data atual do sistema
```

Esse intervalo é definido automaticamente no código por meio da data atual do sistema.

---

# Cidades utilizadas

Atualmente, o dataset utiliza as seguintes cidades:

- São Paulo
- Campinas
- Ribeirão Preto
- Sorocaba
- Piracicaba
- Araraquara
- São José dos Campos
- Ribeirão Pires
- Taquaritinga

---

# Estrutura da tabela bruta

Tabela:

```txt
TB_RISCO_AGRICOLA
```

| Coluna | Tipo esperado | Descrição |
|---|---|---|
| EQUIPAMENTO_ID | texto | Identificador único do equipamento/registro |
| CIDADE | texto | Cidade relacionada à medição |
| DATA_MEDICAO | data | Data do registro climático |
| TEMPERATURA | numérico | Temperatura média diária |
| CHUVA_MM | numérico | Volume de chuva em milímetros |
| UMIDADE_SOLO | numérico | Umidade simulada do solo |
| VELOCIDADE_KMH | numérico | Velocidade simulada da máquina |
| PROXIMIDADE_AGUA_M | numérico | Distância até área com água |
| INCLINACAO_GRAUS | numérico | Inclinação do terreno |
| TEMPO_USO_HORAS | numérico | Tempo de uso do equipamento |
| MANUTENCAO_DIAS | numérico | Dias desde a última manutenção |
| INDICADOR_CHUVA_ALTA | binário | Indica chuva elevada |
| INDICADOR_SOLO_UMIDO | binário | Indica solo muito úmido |
| INDICADOR_VELOCIDADE_ALTA | binário | Indica velocidade elevada |
| INDICADOR_PERTO_AGUA | binário | Indica proximidade de água |
| INDICADOR_INCLINACAO_ALTA | binário | Indica inclinação acentuada |
| INDICADOR_MANUTENCAO_ATRASADA | binário | Indica manutenção atrasada |

---

# Indicadores binários

Os indicadores binários foram criados para representar condições relevantes que podem influenciar o risco operacional.

Eles assumem apenas dois valores:

```txt
0 = condição não presente
1 = condição presente
```

---

## Indicadores atuais

### Chuva alta

```python
indicador_chuva_alta = int(chuva_mm > 30)
```

---

### Solo úmido

```python
indicador_solo_umido = int(umidade_solo > 70)
```

---

### Velocidade alta

```python
indicador_velocidade_alta = int(velocidade_kmh > 18)
```

---

### Proximidade de água

```python
indicador_perto_agua = int(proximidade_agua_m < 100)
```

---

### Inclinação alta

```python
indicador_inclinacao_alta = int(inclinacao_graus > 15)
```

---

### Manutenção atrasada

```python
indicador_manutencao_atrasada = int(manutencao_dias > 90)
```

---

# Por que usar indicadores?

Os indicadores ajudam a destacar condições importantes para o modelo de Machine Learning.

Eles não definem diretamente o risco final.

A ideia é fornecer ao modelo tanto:

- variáveis numéricas brutas;
- variáveis auxiliares binárias.

Assim, o modelo poderá aprender padrões a partir dos dados e decidir quais combinações mais influenciam a previsão de risco.

---

# Mudança importante

A versão anterior do projeto calculava:

- risco;
- score_risco;
- classificacao_risco.

Essas regras foram removidas da geração e do pré-processamento.

Agora:

```txt
gerar_dataset.py → gera dados e indicadores
pre_processamento.py → limpa e trata dados
Machine Learning → será responsável por prever o risco
```

---

# Pré-processamento

O pré-processamento é executado pelo arquivo:

```txt
pre_processamento.py
```

Ele realiza:

- remoção de registros duplicados;
- padronização da cidade;
- conversão da data;
- conversão de colunas numéricas;
- remoção de valores nulos;
- validação de faixas aceitáveis.

---

# Validações aplicadas

Exemplos de filtros utilizados:

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

# Estrutura da tabela tratada

Tabela:

```txt
TB_RISCO_AGRICOLA_TRATADO
```

Essa tabela contém os dados limpos e preparados para a etapa de Machine Learning.

Ela mantém as mesmas colunas principais da tabela bruta, porém após:

- padronização;
- conversão de tipos;
- remoção de inconsistências;
- validação dos registros.

---

# Como executar

## 1. Gerar dataset e inserir no banco

```bash
python sompo-risk-config/gerar_dataset.py
```

Esse comando gera os dados e insere na tabela:

```txt
TB_RISCO_AGRICOLA
```

---

## 2. Executar pré-processamento

```bash
python sompo-risk-config/pre_processamento.py
```

Esse comando lê a tabela bruta, trata os dados e salva na tabela:

```txt
TB_RISCO_AGRICOLA_TRATADO
```

---

# Banco de dados

O projeto utiliza **Oracle Database**.

As credenciais são carregadas pelo arquivo:

```txt
.env
```

Variáveis utilizadas:

```txt
ORACLE_USER
ORACLE_PASSWORD
ORACLE_HOST
ORACLE_PORT
ORACLE_SERVICE
```

O arquivo `.env` deve estar no `.gitignore` para não expor credenciais.

---

# Relação com Machine Learning

A tabela tratada será a base para a próxima etapa do projeto.

O modelo de Machine Learning deverá utilizar os dados tratados para aprender padrões e prever risco operacional.

Exemplos de possíveis features:

- temperatura;
- chuva_mm;
- umidade_solo;
- velocidade_kmh;
- proximidade_agua_m;
- inclinacao_graus;
- tempo_uso_horas;
- manutencao_dias;
- indicadores binários.

---

# Observação sobre variável alvo

Para um modelo supervisionado, será necessário definir uma variável alvo.

Essa variável poderá ser construída ou obtida futuramente, por exemplo:

- ocorrência de sinistro;
- ocorrência de falha;
- acidente registrado;
- classificação histórica de risco;
- label criada a partir de dados reais ou regras validadas.

Nesta etapa, o dataset está sendo preparado para receber essa modelagem posteriormente.

---

# Evoluções futuras

Próximas melhorias previstas:

- criação da etapa de Machine Learning;
- definição da variável alvo;
- treinamento de modelos;
- integração com dashboard;
- uso de dados reais de sensores;
- integração com ESP32;
- uso de dados geoespaciais;
- automação do pipeline.

---

# Resumo

O dataset atual fornece uma base estruturada para o projeto.

Ele contém:

✅ dados climáticos históricos reais  
✅ dados operacionais simulados  
✅ indicadores binários  
✅ persistência em Oracle  
✅ pré-processamento estruturado  
✅ base preparada para Machine Learning
