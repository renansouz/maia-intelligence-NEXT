# 📊 Documentação do Dataset — SompoRisk AI

## Objetivo

Este módulo documenta a criação, estrutura e tratamento do dataset utilizado no projeto **SompoRisk AI**.

O dataset foi desenvolvido para simular cenários operacionais agrícolas com base em:

- dados climáticos históricos reais;
- dados operacionais simulados;
- regras iniciais de classificação de risco.

Seu principal objetivo é servir como base para o treinamento dos modelos de Machine Learning.

---

# Tipo de dataset

O projeto utiliza um **dataset híbrido**.

Ou seja:

## Dados reais
Obtidos via API pública **Open-Meteo**:

- temperatura histórica;
- volume de chuva;
- data da medição;
- localização geográfica.

---

## Dados simulados
Gerados artificialmente:

- umidade do solo;
- velocidade da máquina;
- proximidade de água;
- inclinação do terreno;
- tempo de uso;
- manutenção.

---

## Justificativa

Nesta etapa do projeto, sensores físicos reais ainda não estão conectados.

Por isso, foi adotada uma abordagem híbrida que permite:

- cenários mais realistas;
- variabilidade climática real;
- simulação operacional controlada;
- preparação para futura integração com IoT.

---

# Fluxo do dataset

```txt
api_clima.py
      ↓
coleta clima histórico
      ↓
gerar_dataset.py
      ↓
dataset_risco_agricola.csv
      ↓
pre_processamento.py
      ↓
dataset_tratado.csv
```

---

# Arquivos envolvidos

## api_clima.py

Responsável por:

- buscar coordenadas da cidade;
- consultar API Open-Meteo;
- retornar histórico climático.

---

## gerar_dataset.py

Responsável por:

- escolher cidades;
- carregar dados climáticos;
- gerar variáveis simuladas;
- aplicar regra inicial de risco;
- criar dataset bruto.

Saída:

```txt
csvs/dataset_risco_agricola.csv
```

---

## pre_processamento.py

Responsável por:

- limpeza;
- padronização;
- conversão de tipos;
- remoção de inconsistências;
- score de risco;
- classificação final.

Saída:

```txt
csvs/dataset_tratado.csv
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

Intervalo:

```txt
01/01/2024 até a data atual do sistema
```

---

# Cidades utilizadas

Atualmente:

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

# Estrutura do dataset bruto

Arquivo:

```txt
dataset_risco_agricola.csv
```

Colunas:

| Coluna | Tipo | Descrição |
|-------|------|-----------|
| equipamento_id | string | Identificador único |
| cidade | string | Cidade da medição |
| data_medicao | date | Data do clima histórico |
| temperatura | float | Temperatura média diária |
| chuva_mm | float | Precipitação diária |
| umidade_solo | int | Simulação de umidade |
| velocidade_kmh | float | Velocidade operacional |
| proximidade_agua_m | int | Distância da água |
| inclinacao_graus | float | Inclinação |
| tempo_uso_horas | int | Tempo de operação |
| manutencao_dias | int | Dias desde manutenção |
| risco | string | Classificação inicial |

---

# Regra inicial de risco

A classificação inicial usa regras simples.

Critérios:

## Chuva alta

```python
chuva_mm > 30
```

---

## Solo úmido

```python
umidade_solo > 70
```

---

## Velocidade elevada

```python
velocidade_kmh > 18
```

---

## Proximidade de água

```python
proximidade_agua_m < 100
```

---

## Inclinação perigosa

```python
inclinacao_graus > 15
```

---

## Manutenção atrasada

```python
manutencao_dias > 90
```

---

# Classificação inicial

Pontuação:

```txt
cada fator = +2 pontos
```

Regras:

```txt
>= 8 → alto
>= 4 → medio
< 4 → baixo
```

---

# Pré-processamento

Após gerar o dataset bruto, é executado:

```txt
pre_processamento.py
```

---

## Limpeza

Remove:

- duplicatas;
- valores ausentes;
- tipos inválidos;
- registros quebrados.

---

## Padronização

Corrige:

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

## Validação

Remove dados irreais:

```txt
temperatura < -10
temperatura > 60
chuva > 300
velocidade > 100
tempo_uso > 24
```

---

# Score final

Após tratamento:

Nova coluna:

```txt
score_risco
```

Faixa:

```txt
0 a 100
```

---

## Exemplo

```txt
chuva alta = +20
solo úmido = +20
velocidade alta = +20
```

---

# Classificação final

Nova coluna:

```txt
classificacao_risco
```

Regras:

```txt
>= 70 → alto
>= 40 → medio
< 40 → baixo
```

---

# Dataset final

Arquivo:

```txt
dataset_tratado.csv
```

Colunas adicionais:

- score_risco
- classificacao_risco

---

# Como executar

## Gerar dataset

```bash
python sompo-risk-config/gerar_dataset.py
```

---

## Tratar dataset

```bash
python sompo-risk-config/pre_processamento.py
```

---

# Evoluções futuras

Próximas melhorias:

- sensores reais ESP32;
- dados de GPS;
- mapas;
- dados de operação real;
- integração com dashboard;
- atualização em tempo real;
- pipeline automatizado.

---

# Observações técnicas

O dataset atual é adequado para:

✅ Machine Learning supervisionado  
✅ classificação multiclasse  
✅ testes de modelos  
✅ dashboards  
✅ prototipação rápida
