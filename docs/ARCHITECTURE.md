# 📐 Arquitetura do Ecossistema MAIA

O sistema MAIA foi projetado seguindo o princípio de **Responsabilidade Única** e **Desacoplamento**, permitindo que a inteligência de dados evolua independentemente da interface de visualização.

## 🏗️ Diagrama de Solução (Ponta a Ponta)

```mermaid
flowchart TD
    subgraph "Camada de Ingestão (Gêmeo Digital)"
        A[Open-Meteo API] --> B[scripts/popular_banco.py]
        B -- "Correlação Física" --> C[(Oracle DB: TB_RISCO_TRATADO)]
    end

    subgraph "Core Backend (FastAPI)"
        D[main.py] -- "Middleware" --> L[(TB_LOG_ACESSO)]
        D -- "Service Layer" --> S[risco_service.py]
        S -- "Pooling" --> C
    end

    subgraph "Inteligência e Auditoria"
        S -- "XAI" --> ML[Random Forest + SHAP]
        S -- "Integridade" --> AC[Audit Service]
        ML -- "Score" --> DB2[(TB_PREVISAO_RISCO)]
        AC -- "Hash" --> DB2
    end

    subgraph "Interface Corporativa"
        UI[Frontend Vanilla JS/Tailwind] -- "REST /historico" --> D
        UI -- "REST /previsao" --> D
    end
```

## 🛠️ Decisões de Engenharia

### 1. Transição: Streamlit para Vanilla JS + Tailwind

Embora o Streamlit seja eficiente para protótipos rápidos, optamos pela migração para um **Frontend Estático** consumindo API REST.

- **Justificativa:** Garantir o controle total sobre a identidade visual da Sompo e eliminar o gargalo de re-renderização do Streamlit, proporcionando uma experiência de SPA (Single Page Application) fluida e de baixa latência.

### 2. FastAPI e Session Pooling

Diferente de scripts sequenciais, o backend utiliza o `oracledb.SessionPool`.

- **Justificativa:** Conexões com banco de dados Oracle são custosas. O pooling mantém conexões "vivas", permitindo que o sistema suporte múltiplas requisições simultâneas durante a operação de frota sem degradação de performance.

### 3. Middleware de Rastreabilidade

Implementamos um interceptor nativo no FastAPI que registra cada transação na tabela `TB_LOG_ACESSO`.

- **Justificativa:** Cumprir o requisito de conformidade da Sprint 3, permitindo auditoria técnica de quem acessou qual recurso, tempo de resposta e IP de origem.

### 4. Auto-Migration (config_db.py)

O sistema detecta o estado do banco no startup e aplica as correções de schema (colunas e PKs) automaticamente.

- **Justificativa:** Garantir que o projeto seja "Zero-Touch" para a banca examinadora e para o time de infraestrutura da Sompo.
