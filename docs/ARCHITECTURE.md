# 📐 Arquitetura do MAIA

## Visão Geral do Fluxo de Dados

O MAIA é dividido em quatro camadas com responsabilidades isoladas: ingestão, orquestração, inteligência e apresentação. Cada camada se comunica apenas através de contratos bem definidos (API REST), o que permite que qualquer uma delas evolua sem quebrar as demais.

```mermaid
graph LR
    %% Definição de Cores Sompo
    classDef sompoRed fill:#DF082A,stroke:#9E1E24,color:#fff,stroke-width:2px;
    classDef sompoWine fill:#9E1E24,stroke:#000,color:#fff,stroke-width:1px;
    classDef database fill:#F2F4F7,stroke:#344054,color:#101828,stroke-width:2px;
    classDef logic fill:#fff,stroke:#DF082A,color:#101828,stroke-width:1px;

    %% 1. Ingestão
    subgraph Ingestao ["1. Ingestão de Dados (Gêmeo Digital)"]
        direction TB
        S1[Sensor / Mock]
        S2[Open-Meteo API]
        P_B[popular_banco.py]
        S2 --> P_B
    end

    %% 2. Orquestração
    subgraph Core ["2. Orquestração (Backend FastAPI)"]
        direction TB
        API[FastAPI Main]
        MID[Middleware Log]
        VAL[Validação Pydantic]
        API --- MID
        API --- VAL
    end

    %% 3. Inteligência e Auditoria
    subgraph Inteligencia ["3. Inteligência e Auditoria"]
        direction TB
        RS[risco_service.py]
        ML[ml_service.py]
        AC[audit_service.py]
        
        RS --> ML
        RS --> AC
        ML --> SHAP[Explicação SHAP]
        ML --> RF[Random Forest]
    end

    %% 4. Persistência
    subgraph Dados ["Camada de Dados (Oracle)"]
        direction TB
        DB_LOG[(TB_LOG_ACESSO)]
        DB_TRATADO[(TB_RISCO_TRATADO)]
        DB_PREV[(TB_PREVISAO_RISCO)]
    end

    %% 5. Apresentação
    subgraph UI ["4. Apresentação (Frontend)"]
        FRONT[SPA Vanilla JS + Tailwind]
    end

    %% Fluxos de Conexão (Organizados)
    S1 -->|"POST /telemetria"| API
    P_B -->|"Sync"| DB_TRATADO
    
    API -->|"Event"| RS
    MID -.-> DB_LOG
    VAL -.-> DB_TRATADO
    
    RS --> DB_PREV
    DB_PREV -->|"GET /historico"| API
    API --> FRONT

    %% Aplicação de Estilos
    class API,RS,ML,AC sompoRed;
    class P_B,FRONT sompoWine;
    class DB_LOG,DB_TRATADO,DB_PREV database;
    class S1,S2,VAL,MID,SHAP,RF logic;
```

## Fluxo de Entrada de Dados

Existem dois caminhos de entrada, com propósitos diferentes:

- **`POST /telemetria`** — endpoint de ingestão em tempo real. Recebe uma leitura de sensor/equipamento, valida via Pydantic e persiste em `TB_RISCO_AGRICOLA_TRATADO`. É o caminho que representa a operação real do sistema em produção.
- **`scripts/popular_banco.py`** — gera o histórico da frota simulada (50 equipamentos fixos, 5 cidades), combinando clima real (Open-Meteo) com telemetria sintética correlacionada. Usado para construir a base de treino do modelo e popular o ambiente de demonstração.

Os dois caminhos convergem na mesma tabela e no mesmo pipeline de inferência — não existe lógica duplicada entre ingestão em tempo real e ingestão em lote.

## Decisões de Engenharia

### FastAPI como orquestrador central

Toda a lógica de negócio (validação, chamada ao modelo, geração de hash, persistência) passa por um único ponto de entrada. Isso garante que qualquer cliente — o frontend, um script de teste, ou um sistema externo da Sompo — receba exatamente o mesmo tratamento e as mesmas garantias de segurança e auditoria.

### Frontend desacoplado (HTML + Tailwind + JavaScript)

O frontend é servido como arquivos estáticos pelo próprio FastAPI (`StaticFiles`) e se comunica com o backend exclusivamente via API REST, sem nunca ter acesso direto ao banco de dados ou às credenciais do Oracle. Essa separação significa que a interface pode ser hospedada separadamente do backend no futuro, sem qualquer alteração na lógica de negócio.

A ausência de um framework de frontend (React, Vue) foi uma escolha deliberada: sem processo de build, sem `node_modules`, sem passo de compilação — o projeto roda com um único comando, e o controle sobre a identidade visual da Sompo é total.

### Session Pooling no Oracle

Conexões com banco de dados relacional têm custo de abertura não-trivial. O `app/core/database.py` mantém um `SessionPool` do `oracledb`, reaproveitando conexões entre requisições em vez de abrir e fechar uma nova a cada chamada — essencial para que a API suporte múltiplas requisições simultâneas sem degradação.

### Migração de schema automática (`config_db.py`)

Ao subir, o backend verifica o estado real das tabelas no Oracle — quais existem, quais colunas faltam, se as chaves primárias estão corretas — e aplica as correções necessárias via `ALTER TABLE`, de forma idempotente. Isso garante que o projeto rode de forma consistente independentemente do estado anterior do banco, sem exigir intervenção manual de quem for executá-lo.

### Middleware de rastreabilidade

Toda requisição HTTP que chega à API é interceptada por um middleware que registra método, rota, status de resposta, IP de origem e tempo de processamento em `TB_LOG_ACESSO`. Isso é independente do hash chain de auditoria de decisões — o middleware rastreia _acesso ao sistema_, o hash chain garante _integridade do dado gravado_. São camadas complementares de rastreabilidade.

## Estrutura de Diretórios

```
app/
├── core/ → conexão Oracle, migração de schema
├── models/ → schemas Pydantic (contratos da API)
├── services/ → lógica de negócio (ML, auditoria, dados)
└── main.py → ponto de entrada, rotas e middleware

frontend/
├── assets/ → identidade visual (logo)
├── css/ → estilos
├── js/ → lógica da aplicação (uma view por arquivo)
└── index.html

machine_learning/
└── treinar_modelo.py → geração do modelo (fonte de treino)

ml_assets/ → binários do modelo treinado, versionados no Git

scripts/
├── validacao/ → benchmarks e provas científicas
├── popular_banco.py
└── popular_previsoes_historicas.py
```

## Segurança de Acesso

Todos os endpoints exigem uma API Key válida via header `X-API-KEY`. A validação é **fail-closed**: se a chave não estiver configurada no ambiente, ou não bater com a enviada, o acesso é bloqueado — o sistema nunca assume acesso liberado por ausência de configuração. Detalhes matemáticos de segurança e auditoria estão em [SECURITY.md](./SECURITY.md).
