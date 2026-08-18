# 🤖 Machine Learning — O Motor MAIA

A inteligência do MAIA transforma dados ambientais e operacionais em uma estimativa probabilística de risco, permitindo antecipar situações que exigem atenção antes que evoluam para eventos operacionais.

## 🧬 O Gêmeo Digital (Synthetic Twin)

Para representar uma operação agrícola de forma consistente, desenvolvemos um **Motor de Síntese de Dados** baseado em relações físicas e operacionais plausíveis.

- **Dados climáticos reais:** utilizamos a API Open-Meteo como fonte de precipitação e temperatura para as cidades monitoradas.
- **Telemetria correlacionada:** velocidade, inclinação, proximidade de água, manutenção e umidade do solo são sintetizadas a partir de regras coerentes com o cenário agrícola.
- **Coerência física:** condições de maior precipitação elevam a probabilidade de solo mais úmido/saturado, evitando a geração de telemetria puramente aleatória.
- **Escala:** o ambiente atual possui **48.050 registros**, distribuídos entre **50 equipamentos** em **5 cidades**.

O Synthetic Twin permite construir um ambiente controlado de experimentação mantendo relações consistentes entre clima, operação e risco.

## 🧠 Modelagem: Random Forest Ensemble

Na evolução da Sprint 2, substituímos a Árvore de Decisão por um **Random Forest**, buscando um melhor equilíbrio entre capacidade preditiva e explicabilidade.

O modelo utiliza:

```python
RandomForestClassifier(
    class_weight="balanced"
)
```

O `class_weight="balanced"` reduz o impacto do desequilíbrio entre as classes, importante em cenários onde eventos de risco são menos frequentes.

## 🔍 Explicabilidade (XAI) com SHAP

Para o MAIA, o score de risco precisa ser compreensível.

Integramos **SHAP (SHapley Additive exPlanations)** ao backend para identificar, em cada predição, os fatores que mais contribuíram para o resultado.

O fluxo é:

```text
Dados → Predição → SHAP → Explicação operacional
```

Além disso, aplicamos um **filtro de redundância** que prioriza indicadores binários sobre variáveis brutas equivalentes, tornando a explicação mais legível para o usuário.

Assim, o MAIA não apresenta apenas:

> **"Qual é o risco?"**

Ele também responde:

> **"Quais fatores mais influenciaram essa avaliação?"**

## 📊 Benchmark de Modelos

A escolha do algoritmo foi baseada em um benchmark comparativo entre quatro modelos:

- Regressão Logística
- Árvore de Decisão
- Gradient Boosting
- Random Forest

A comparação utiliza o mesmo conjunto de dados e o mesmo conjunto de teste, com 20% dos registros e `random_state=42`.

| Modelo                   |    ROC-AUC | Cobertura ≥30% |
| ------------------------ | ---------: | -------------: |
| Regressão Logística      | **0.7095** |         27.06% |
| Árvore de Decisão        |     0.5675 |         35.25% |
| Gradient Boosting        |     0.7077 |     **60.87%** |
| **Random Forest (MAIA)** | **0.7054** |     **58.00%** |

O Random Forest não foi selecionado simplesmente pelo maior ROC-AUC. A diferença entre os três modelos de melhor desempenho é pequena, enquanto o Random Forest mantém **58% de cobertura nas faixas de Atenção/Crítico** e oferece uma combinação adequada entre desempenho, comportamento não linear e integração com SHAP.

A decisão final, portanto, considera o **conjunto do sistema**, e não uma única métrica isolada.

### ROC-AUC

Mede a capacidade do modelo de separar casos de maior risco de casos de menor risco, considerando diferentes pontos de corte.

### Cobertura de Risco

Mede, entre os registros classificados como risco real, quantos receberam probabilidade **≥30%** e entraram nas faixas de Atenção ou Crítico.

No modelo MAIA, essa cobertura é de **58,00%**.

## 🚦 Classificação em 3 Faixas

O MAIA utiliza a probabilidade retornada por `predict_proba()` para classificar o risco em três níveis:

| Faixa       | Probabilidade |
| ----------- | ------------: |
| **Baixo**   |         < 30% |
| **Atenção** |     30% – 70% |
| **Crítico** |         > 70% |

Essa abordagem preserva a natureza probabilística da previsão e permite representar diferentes níveis de prioridade operacional.

## 🎯 Variável-Alvo: Geração Probabilística

A variável `risco_operacional` não é definida por uma regra determinística.

A probabilidade do evento aumenta de acordo com a quantidade de indicadores de risco ativos:

```python
if indicadores_ativos >= 4:
    probabilidade = 0.75
elif indicadores_ativos >= 2:
    probabilidade = 0.35
else:
    probabilidade = 0.08

risco_operacional = 1 if random() < probabilidade else 0
```

Essa abordagem permite que condições semelhantes produzam resultados diferentes, preservando a variabilidade esperada em eventos operacionais.

A seed é definida uma única vez por execução do processo, garantindo reprodutibilidade sem eliminar a variação estatística entre registros.

## 📐 Indicadores Binários

| Indicador                       | Regra                    |
| ------------------------------- | ------------------------ |
| `indicador_chuva_alta`          | chuva_mm > 30            |
| `indicador_solo_umido`          | umidade_solo > 70%       |
| `indicador_velocidade_alta`     | velocidade_kmh > 18      |
| `indicador_perto_agua`          | proximidade_agua_m < 100 |
| `indicador_inclinacao_alta`     | inclinacao_graus > 15°   |
| `indicador_manutencao_atrasada` | manutencao_dias > 90     |

O modelo utiliza **14 features**, combinando variáveis contínuas e os seis indicadores binários.

## 🔗 Pipeline de Inteligência

```text
Open-Meteo API
      ↓
scripts/popular_banco.py
      ↓
Synthetic Twin
      ↓
TB_RISCO_AGRICOLA_TRATADO
      ↓
machine_learning/treinar_modelo.py
      ↓
Benchmark de Modelos
      ↓
Random Forest
      ↓
ml_assets/modelo_risco.pkl
      ↓
app/services/ml_service.py
      ↓
Predição + SHAP
      ↓
TB_PREVISAO_RISCO
      ↓
Score + Explicação + Hash de Auditoria
```

## 🧪 Validação Estatística

Além do benchmark dos modelos, analisamos a relação entre precipitação e risco no dataset.

| Métrica                  |         Resultado |
| ------------------------ | ----------------: |
| Correlação Chuva × Risco |        **0.0473** |
| P-value                  | **3.083 × 10⁻²⁵** |

O p-value extremamente baixo indica uma associação estatisticamente significativa entre as variáveis no conjunto analisado.

Ao mesmo tempo, a correlação de **0.0473** possui baixa magnitude. Isso reforça uma característica importante do MAIA: **chuva isoladamente não determina o risco**. O score resulta da combinação de múltiplos fatores ambientais e operacionais.

## 🌧️ Validação Histórica: São Paulo, Fevereiro de 2024

Para observar o comportamento temporal do modelo diante de condições climáticas reais, executamos a inferência sobre o histórico de fevereiro de 2024 em São Paulo.

Os maiores scores médios ocorreram em:

| Data      | Score Médio | Status                    |
| --------- | ----------: | ------------------------- |
| 07/02     |      34,12% | Atenção                   |
| 13/02     |      32,38% | Atenção                   |
| 19/02     |      35,25% | Atenção                   |
| 20/02     |      37,00% | Atenção                   |
| **22/02** |  **39,37%** | **Atenção — pico do mês** |

O menor score observado foi:

| Data      | Score Médio | Status                      |
| --------- | ----------: | --------------------------- |
| **25/02** |  **12,50%** | **Estável — mínimo do mês** |

Nos 29 dias analisados:

- **5 dias** ficaram em Atenção;
- **24 dias** permaneceram Estáveis;
- **nenhum dia** atingiu a faixa Crítico.

O resultado demonstra que o score acompanha a variação das condições observadas no período, em vez de permanecer em um nível constante.

## 🗃️ Volume Atual

| Componente          | Quantidade |
| ------------------- | ---------: |
| Registros tratados  | **48.050** |
| Previsões auditadas |  **2.500** |
| Equipamentos        |     **50** |
| Cidades             |      **5** |

As previsões armazenadas em `TB_PREVISAO_RISCO` são utilizadas pela aplicação e pela camada de auditoria, preservando o score, a explicação e o hash correspondente.

## ♻️ Reprodutibilidade

Os principais processos podem ser executados pelos scripts versionados no projeto:

```bash
# Treinamento
python3 -m machine_learning.treinar_modelo

# Benchmark dos modelos
python3 -m scripts.validacao.comparativo_modelos

# Validação histórica
python3 -m scripts.validacao.simulacao_historica
```

Os artefatos do modelo treinado ficam versionados em:

```text
ml_assets/
```

permitindo reproduzir o processo de inferência utilizado pela aplicação.

## 🎯 O Papel do ML no MAIA

O Machine Learning é o motor de risco, mas não é o produto inteiro.

O fluxo completo é:

```text
DADOS
  ↓
RISCO
  ↓
EXPLICAÇÃO
  ↓
DECISÃO
  ↓
AUDITORIA
```

**Random Forest** responde:

> Qual é a probabilidade de risco?

**SHAP** responde:

> Quais fatores influenciaram essa avaliação?

A camada de auditoria responde:

> Como comprovar que essa decisão permaneceu íntegra?

É essa integração entre **predição, explicabilidade e rastreabilidade** que transforma o modelo em um componente de uma solução de gestão preventiva de risco agrícola.
