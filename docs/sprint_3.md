# 📋 Estado final do MAIA no Sprint 3 (Ponto de Partida do Sprint 4)

> Este documento existe pra qualquer pessoa do time entender, em 10 minutos, onde o projeto está, o que já funciona, o que está quebrado, e por quê. Serve como mapa antes de mexer em qualquer código.

---

## 🗂️ Estrutura de Pastas — o que tem em cada uma

```
app/
├── core/
│   ├── database.py       → conexão com o Oracle (pool de conexões)
│   └── config_db.py      → cria/atualiza as tabelas do banco automaticamente
├── models/
│   └── schemas.py        → define o formato dos dados que a API aceita (Pydantic)
├── services/
│   ├── data_service.py         → salva/busca telemetria no banco
│   ├── processamento_service.py → calcula indicadores de risco (chuva alta, solo úmido etc.)
│   ├── ml_service.py           → carrega o modelo de IA e gera o score + explicação (SHAP)
│   ├── audit_service.py        → gera o hash de auditoria (cadeia de integridade)
│   └── risco_service.py        → orquestra tudo: chama o ML, gera o hash, salva no banco
└── main.py                → onde ficam as rotas da API (endpoints)

docs/                      → documentação técnica (será reorganizada nesta sprint)

frontend/
├── assets/                → logos e imagens
├── css/styles.css         → cores e identidade visual da Sompo
├── js/
│   ├── api.js             → faz as chamadas pro backend
│   ├── operacional.js     → tela do mapa e status geral
│   ├── gestao.js          → tela de gráficos e ranking
│   ├── diagnostico.js     → tela de laudo individual (SHAP + gauge)
│   ├── compliance.js      → tela de auditoria/histórico
│   └── config.example.js  → onde fica a chave de API do frontend
└── index.html             → estrutura da página e navegação entre telas

machine_learning/
└── treinar_modelo.py      → treina o Random Forest com os dados do banco

ml_assets/
└── modelo_risco.pkl       → o modelo já treinado, usado em produção

scripts/
├── popular_banco.py               → gera dados de telemetria (clima real + resto simulado)
└── popular_previsoes_historicas.py → roda o modelo em massa pra popular o histórico de previsões
```

---

## 🔴 Problemas Identificados no Feedback da Sprint 3

Isso **não é crítica pelo trabalho feito** — a nota foi 8.37/9, nos entregamos algo funcional e bem comunicado. Mas o professor encontrou falhas reais que precisamos resolver antes de qualquer coisa nova:

### 1. A cadeia de hash não é imutável de verdade

**Onde:** `risco_service.py`, no comando `MERGE`.
**O problema:** se alguém consulta o risco do mesmo equipamento duas vezes no mesmo dia, o sistema **sobrescreve** o registro antigo e recalcula um hash novo. Isso quebra a cadeia de auditoria, a mesma coisa que devia provar que "nada foi alterado" está sendo alterada pelo próprio sistema.
**O que precisa mudar:** cada previsão deve virar um **registro novo**, nunca sobrescrever o anterior.

### 2. Uma consulta (GET) está alterando dados

**Onde:** `main.py`, rota `GET /previsao/{equipamento_id}`.
**O problema:** um GET deveria só _ler_ informação. Mas essa rota está processando e **gravando** uma nova previsão no banco toda vez que é chamada. Isso viola a lógica básica de API REST.
**O que precisa mudar:** separar isso, talvez um endpoint de leitura (GET) e outro de processamento (POST).

### 3. Mensagens de erro cruas voltam pro usuário

**Onde:** `main.py`, em `/telemetria` e `/historico` (`detail=str(e)`).
**O problema:** se algo falha no servidor, o erro técnico completo (que pode revelar detalhes internos do sistema) aparece pra quem está usando a API.
**O que precisa mudar:** capturar o erro internamente (logar) e devolver uma mensagem genérica pro usuário.

### 4. Não existe identidade de quem acessa

**Onde:** `main.py`, função `verificar_key` (chave única `API_KEY`).
**O problema:** todo mundo usa a mesma senha/chave. O sistema sabe _que alguém_ acessou, mas não sabe _quem_. Não existe separação entre operador, gestor e seguradora.
**O que precisa mudar:** login de verdade, com identidade e papel (role) de cada usuário.

### 5. A telemetria perde informação quando atualizada

**Onde:** `data_service.py`, função `salvar_telemetria_db`.
**O problema:** o `MERGE` só atualiza 3 campos (temperatura, chuva, umidade) quando já existe leitura do dia, os outros 6 campos enviados são descartados.
**O que precisa mudar:** ou atualizar todos os campos, ou (melhor) permitir múltiplas leituras por dia.

### 6. Só é possível ter uma leitura por equipamento por dia

**Onde:** `config_db.py`, chave primária `(EQUIPAMENTO_ID, DATA_MEDICAO)`.
**O problema:** um sensor de verdade manda dado várias vezes ao dia. Essa trava impede isso.
**O que precisa mudar:** repensar a chave, talvez incluir hora/timestamp, não só data.

### 7. O mapa mostra localização que não existe

**Onde:** `frontend/js/operacional.js`, função `initMap` (`Math.random()` somado à coordenada da cidade).
**O problema:** os pontos no mapa são posições aleatórias em volta do centro da cidade, não é a localização real do equipamento.
**O que precisa mudar:** usar coordenada real cadastrada por máquina (isso já está sendo resolvido com o novo cadastro de máquina que vamos desenhar).

---

## ✅ O que já está bom e não precisa mudar

- Separação em camadas (`ml_service`, `audit_service`, `risco_service`, `data_service`), arquitetura limpa, só corrigir o conteúdo, não a estrutura.
- O uso de SHAP no `ml_service.py`, incluindo o filtro de redundância entre variável bruta e indicador, detalhe fino, mantém.
- O frontend já tem identidade visual da Sompo e 4 telas funcionais com gráficos reais (Plotly) e mapa (Leaflet).
- O pool de conexões Oracle (`database.py`) está bem implementado.

---

## 🎯 Por onde começar

A prioridade nesta sprint é: **primeiro corrigir os 7 pontos acima, depois evoluir com as ideias novas** (login/personas, dado real, ideias de sinistro). Não adianta construir coisa nova em cima de uma base que ainda tem furo de segurança e integridade.
