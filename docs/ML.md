# 🤖 Machine Learning — O Motor MAIA

A inteligência do MAIA baseia-se na capacidade de prever falhas operacionais antes que elas se tornem sinistros financeiros.

## 🧬 O Gêmeo Digital (Synthetic Twin)

Dada a natureza sensível de dados reais de frotas agrícolas, desenvolvemos um **Motor de Síntese de Dados**.

- **Rigor Físico:** Os dados simulados não são aleatórios. Implementamos correlações estatísticas onde a precipitação alta (Open-Meteo) eleva deterministicamente a probabilidade de solo saturado, emulando um cenário operacional real.
- **Volume:** O dataset atual conta com ~48.000 registros históricos, permitindo um treinamento robusto do modelo.

## 🧠 Modelagem: Random Forest Ensemble

Evoluímos da Árvore de Decisão (Sprint 2) para o **Random Forest**.

- **Técnica:** Utilizamos `class_weight='balanced'` para compensar o desequilíbrio natural de sinistros (incidentes são raros, mas críticos).
- **Resultado:** Alcançamos um **ROC-AUC de 0.7072**, um salto significativo de performance em relação ao baseline de 0.56.

## 🔍 Explicabilidade (XAI) com SHAP

Para o MAIA, o "quê" não é suficiente sem o "porquê".

- **Funcionamento:** Integramos o motor **SHAP (SHapley Additive exPlanations)** no backend. Para cada predição, a IA identifica os 3 fatores (ex: inclinação, umidade, velocidade) que mais contribuíram para o risco.
- **Filtro de Redundância:** Implementamos uma lógica de limpeza que prioriza indicadores binários sobre variáveis brutas, tornando o laudo técnico legível para o operador.

## 📊 Métricas de Validação

| Métrica           | Valor  | Significado                                                             |
| :---------------- | :----- | :---------------------------------------------------------------------- |
| **ROC-AUC**       | 0.7072 | Capacidade do modelo de distinguir risco de normalidade.                |
| **Risk Coverage** | 58.38% | Percentual de incidentes reais capturados nas faixas de Alerta/Atenção. |
| **Dataset**       | 47.950 | Total de amostras processadas pelo Gêmeo Digital.                       |

```
Open-Meteo API (clima real)
↓
scripts/popular_banco.py (telemetria sintética correlacionada)
↓
TB_RISCO_AGRICOLA_TRATADO (Oracle)
↓
machine_learning/treinar_modelo.py
↓
ml_assets/modelo_risco.pkl
↓
app/services/ml_service.py (inferência + SHAP)
↓
TB_PREVISAO_RISCO (score + explicação + hash)
```

## O Gêmeo Digital: Dados Reais + Simulação Correlacionada

O componente climático do dataset (temperatura, precipitação) vem diretamente da API Open-Meteo, para as 5 cidades monitoradas, com histórico desde janeiro de 2024. O componente operacional (velocidade, inclinação, proximidade de água, manutenção) é sintetizado, porque telemetria de frota real não estava disponível para este desafio — mas a síntese não é aleatória e desacoplada da realidade: variáveis operacionais são geradas com correlação física ao clima do dia (por exemplo, em dias de chuva elevada, a umidade do solo tende a valores mais altos).

A frota simulada é composta por **50 equipamentos fixos** (10 por cidade, padrão `EQP-{CIDADE}-{01-10}`), o que permite rastrear o histórico de cada equipamento individualmente ao longo do tempo — condição necessária para o ranking de criticidade e para a auditoria por equipamento.

Volume atual da base de treino: **48.050 registros** em `TB_RISCO_AGRICOLA_TRATADO`.

## Variável Alvo: Geração Probabilística

A variável `risco_operacional` (0 ou 1) não é uma regra fixa — ela é sorteada com base na quantidade de indicadores de risco ativos simultaneamente:

```python
if indicadores_ativos >= 4:
    probabilidade = 0.75
elif indicadores_ativos >= 2:
    probabilidade = 0.35
else:
    probabilidade = 0.08

risco_operacional = 1 if random() < probabilidade else 0
```

Essa abordagem reflete a realidade: nem toda condição de risco elevado resulta em incidente, e incidentes podem ocorrer mesmo com poucos indicadores ativos. A seed é fixada uma única vez por execução do script (não a cada linha), garantindo reprodutibilidade sem colapsar a variação estatística entre registros.

## Indicadores Binários

| Indicador                       | Regra                    |
| ------------------------------- | ------------------------ |
| `indicador_chuva_alta`          | chuva_mm > 30            |
| `indicador_solo_umido`          | umidade_solo > 70%       |
| `indicador_velocidade_alta`     | velocidade_kmh > 18      |
| `indicador_perto_agua`          | proximidade_agua_m < 100 |
| `indicador_inclinacao_alta`     | inclinacao_graus > 15°   |
| `indicador_manutencao_atrasada` | manutencao_dias > 90     |

## Modelo: Random Forest

O modelo em produção é um `RandomForestClassifier` (scikit-learn), treinado sobre 14 features (8 variáveis contínuas + 6 indicadores binários), com `class_weight='balanced'` para compensar o desequilíbrio natural entre classes de risco.

### Por que Random Forest

Um modelo de árvore de decisão única foi avaliado como baseline. O ensemble de Random Forest apresentou ganho substancial de performance sem perda relevante de explicabilidade — a interpretabilidade que antes vinha da árvore única passou a ser garantida pela camada SHAP, aplicada sobre o modelo em produção.

### Benchmark formal

Comparação feita sobre o mesmo conjunto de teste (20% dos dados, `random_state=42`), reproduzível via `scripts/validacao/comparativo_modelos.py`:

| Modelo            | ROC-AUC    | Cobertura de Risco Real (≥30% de probabilidade) |
| ----------------- | ---------- | ----------------------------------------------- |
| Árvore de Decisão | 0.5625     | 35.06%                                          |
| **Random Forest** | **0.7072** | **58.38%**                                      |

- **ROC-AUC** mede a capacidade do modelo de ordenar corretamente casos de risco acima de casos normais, independente de qualquer limiar fixo — métrica coerente com o funcionamento do MAIA, que nunca decide em um único ponto de corte binário.
- **Cobertura de Risco Real** mede, entre os casos que realmente eram de risco no conjunto de teste, quantos o modelo atribuiu probabilidade ≥30% (ou seja, quantos caíram nas faixas Atenção/Alerta do sistema, em vez de passarem despercebidos como Baixo). O Random Forest captura 58% desses casos, contra 35% da árvore — um ganho de aproximadamente 66% em cobertura.

## Classificação em 3 Faixas

O sistema não expõe uma decisão binária (0/1). A probabilidade contínua retornada por `predict_proba` é convertida em três faixas:

| Faixa           | Probabilidade |
| --------------- | ------------- |
| Baixo           | < 30%         |
| Médio (Atenção) | 30% – 70%     |
| Alto (Crítico)  | > 70%         |

Essa decisão foi tomada após observar que, no dataset, a maior parte dos casos reais de risco cai justamente na faixa intermediária de probabilidade — forçar uma decisão binária nesse ponto descartaria informação real de incerteza. O modelo comunica a incerteza em vez de escondê-la atrás de um "sim ou não".

## Explicabilidade: SHAP

Para cada predição, o backend calcula os valores SHAP de todas as features e seleciona os fatores de maior contribuição positiva para o risco. Para evitar redundância no laudo apresentado ao usuário, variáveis contínuas que já possuem um indicador binário correspondente no top de importância são descartadas da explicação final (por exemplo, se `indicador_perto_agua` e `proximidade_agua_m` aparecem juntos, apenas o indicador — mais legível — é mostrado).

## Validação Histórica: São Paulo, Fevereiro de 2024

Para verificar a coerência do modelo contra clima real, a inferência foi rodada retroativamente sobre o histórico bruto de fevereiro de 2024 em São Paulo — mês com precipitação acima da média (`scripts/validacao/simulacao_historica.py`, dados extraídos de `TB_RISCO_AGRICOLA_TRATADO`, chamando `ml_service` diretamente, sem depender de previsões pré-calculadas):

| Data      | Score Médio   | Status                    |
| --------- | ------------- | ------------------------- |
| 02/02     | 30.4%         | Atenção                   |
| 04/02     | 36.2%         | Atenção                   |
| 10/02     | 31.1%         | Atenção                   |
| 13/02     | 36.7%         | Atenção                   |
| 19–20/02  | 35.1% / 36.1% | Atenção                   |
| **22/02** | **41.6%**     | **Atenção (pico do mês)** |
| 25/02     | 8.3%          | Estável (mínimo do mês)   |
| 27/02     | 30.5%         | Atenção                   |
| 29/02     | 32.1%         | Atenção                   |

Ao longo dos 29 dias, 9 (31%) caíram em Atenção e 20 (69%) em Estável — nenhum dia atingiu a faixa Crítica, resultado coerente para um mês de chuva elevada porém não extrema. O ponto relevante é a correlação temporal: os picos de score acompanham os dias de maior precipitação real registrada pela Open-Meteo, e o menor score do mês (25/02) coincide com um dia de estiagem — evidência de que o modelo reage a variação climática real, e não a um valor médio artificial.

## Volume de Dados

- Base de treino/simulação: **48.050 registros** (`TB_RISCO_AGRICOLA_TRATADO`)
- Previsões auditadas com hash de integridade: **2.500 registros** (`TB_PREVISAO_RISCO`)
- Frota simulada: **50 equipamentos** em 5 cidades

## Reprodutibilidade

```bash
python3 -m machine_learning.treinar_modelo          # Retreinar o modelo
python3 -m scripts.validacao.comparativo_modelos    # Benchmark formal
python3 -m scripts.validacao.simulacao_historica     # Validação histórica
```
