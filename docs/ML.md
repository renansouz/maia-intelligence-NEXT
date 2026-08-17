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
