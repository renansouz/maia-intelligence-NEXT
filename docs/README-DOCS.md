# 📚 Documentação Técnica — Ecossistema MAIA

Esta documentação detalha as decisões de engenharia, os resultados estatísticos e a arquitetura de segurança que sustentam o projeto **MAIA**.

## 🏗️ Arquitetura do Sistema

O MAIA foi desenhado para ser resiliente e performático. Migramos de uma estrutura monolítica em Streamlit para uma **Arquitetura Desacoplada**:

```mermaid
flowchart TD
    subgraph "Camada de Ingestão (Sensores)"
        A[Sensores/Scripts] -- "POST /telemetria" --> B[FastAPI Backend]
    end

    subgraph "Core API & Persistência"
        B -- "Middleware" --> L[(TB_LOG_ACESSO)]
        B -- "Repository" --> DB1[(Oracle DB: TB_RISCO_TRATADO)]
    end

    subgraph "Inteligência & Segurança"
        B -- "SHAP" --> ML[Random Forest Model]
        B -- "Hash Chain" --> AC[Audit Service]
        ML -- "Score" --> DB2[(TB_PREVISAO_RISCO)]
        AC -- "Hash Integrity" --> DB2
    </div>

    subgraph "Visualização Corporativa"
        DB2 -- "GET /historico" --> D[Frontend Vanilla JS/Tailwind]
    end
```

### Por que esta stack?

- **FastAPI:** Escolhido pela alta performance e geração automática de documentação (Swagger), essencial para integração com sistemas legados da Sompo.
- **Vanilla JS (ES6+):** Optamos por não usar frameworks pesados (React/Vue) para manter o frontend leve, rápido e com controle total sobre a identidade visual da Sompo, sem as restrições de layout do Streamlit.
- **Oracle Session Pool:** Implementamos pooling de conexões para garantir que o banco da FIAP suporte múltiplas requisições simultâneas durante a demo.

---

## 🤖 Machine Learning: O Salto de Performance

Na Sprint 2, utilizamos uma Árvore de Decisão básica. No MAIA, evoluímos para um **Random Forest com Class Weighting**.

### Benchmark de Modelos

Rode o script `python3 -m scripts.validacao.comparativo_modelos` para validar estes números:

| Métrica                                | Árvore de Decisão | Random Forest (MAIA) | Melhoria |
| :------------------------------------- | :---------------- | :------------------- | :------- |
| **ROC-AUC**                            | 0.5625            | **0.7072**           | **+25%** |
| **Cobertura de Risco (Recall >= 30%)** | 35.06%            | **58.38%**           | **+66%** |

**Justificativa:** O modelo anterior falhava em identificar riscos altos devido ao desequilíbrio das classes. O Random Forest, aliado ao peso balanceado, permitiu que o sistema identificasse 66% mais situações críticas dentro da zona de alerta/atenção.

### Explicabilidade (XAI)

Utilizamos **SHAP (SHapley Additive exPlanations)**. Em vez de prever apenas um número, o backend decompõe o score e identifica os 3 principais fatores de influência. Isso resolve o problema da "Caixa Preta" na IA.

---

## 🛡️ Protocolo de Segurança e Auditoria

### Hash Chain (Blockchain Simplificado)

Para garantir que os dados de risco nunca sejam manipulados, implementamos um encadeamento de hash no Oracle:
`Novo_Hash = SHA256(Equipamento + Data + Score + Hash_Anterior)`

Ao ler o hash anterior com `FOR UPDATE` e `ROWID` lock, garantimos que a cadeia seja única e global, mesmo sob alta concorrência.

### Rastreabilidade de Uso

Todas as chamadas de API são registradas via **Middleware** na tabela `TB_LOG_ACESSO`, capturando:

- IP de Origem
- Tempo de processamento (ms)
- Status HTTP e Rota chamada.

---

## 🧪 Validação Histórica: São Paulo (Fev/2024)

Para provar a eficácia, rodamos o MAIA retroativamente sobre o mês de Fevereiro de 2024 em São Paulo, período marcado por tempestades severas.

**Resultado:**

- O sistema gerou status **WARNING (Amarelo)** em 42% do período.
- Os picos de score (ex: 10/02 e 22/02) coincidiram com dados de precipitação elevada fornecidos pela Open-Meteo.
- Isso prova que a IA é sensível a variações climáticas reais, validando sua aplicação no mundo real.

---

## 🚀 Como Executar

### Pré-requisitos

- Python 3.11+
- Oracle Instant Client (opcional, usamos modo Thin)
- VPN FIAP ativa

### Instalação

1.  Instalar dependências: `pip install -r requirements.txt`
2.  Configurar `.env` (use o `.env.example` como base).
3.  Sincronizar banco: `python3 -m app.core.config_db`
4.  Treinar modelo: `python3 -m machine_learning.treinar_modelo`
5.  Popular histórico: `python3 -m scripts.popular_banco` e `python3 -m scripts.popular_previsoes_historicas`

### Inicialização

```bash
# Rodar Backend e Frontend juntos
python3 -m uvicorn app.main:app --reload
```

Acesse: `http://127.0.0.1:8000/`
