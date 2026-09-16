# 📋 Estado Atual do MAIA

> Este documento existe pra qualquer pessoa do time entender, em 10 minutos, onde o projeto está, o que já foi corrigido, e o que ainda falta. Serve como mapa antes de mexer em qualquer código.

---

## 🗂️ Estrutura de Pastas — o que tem em cada uma

```
app/
├── core/
│   ├── database.py       → conexão com o Oracle (pool de conexões)
│   └── config_db.py      → cria/atualiza todas as tabelas do banco
├── models/
│   └── schemas.py        → formato dos dados aceitos pela API
├── services/
│   ├── data_service.py         → telemetria (salvar/buscar)
│   ├── processamento_service.py → cálculo de indicadores de risco (chuva alta, solo úmido etc.)
│   ├── ml_service.py           → modelo de IA, score e explicação (SHAP)
│   ├── audit_service.py        → geração do hash de auditoria
│   ├── risco_service.py        → orquestra ML + hash + persistência
│   ├── auth_service.py         → hash de senha, geração/validação de JWT, controle de papel
│   ├── user_service.py         → cadastro/busca de usuário, criação do usuário Sompo inicial
│   ├── fazenda_service.py      → cadastro e listagem de fazenda
│   └── maquina_service.py      → cadastro de máquina, vínculos, controle de acesso por equipamento
└── main.py                → rotas da API

frontend/
├── assets/
│   └── sompo-logo.webp
├── css/
│   └── styles.css
├── js/
│   ├── core/
│   │   ├── api.js             → chamadas pro backend, autenticadas
│   │   ├── auth.js            → sessão do usuário (token, papel, logout)
│   │   └── router.js          → roteamento e controle de navegação por persona
│   ├── views/
│   │   ├── sompo/
│   │   │   ├── dashboard.js   → visão executiva e central de risco da seguradora
│   │   │   └── cadastros.js   → cadastro de máquinas na apólice
│   │   ├── gestor/
│   │   │   ├── dashboard.js   → gestão de fazendas e frota
│   │   │   ├── tickets.js     → gerenciamento de tickets da equipe
│   │   │   └── cadastros.js   → cadastro de fazendas e operadores
│   │   ├── operador/
│   │   │   └── painel.js      → status simplificado da máquina e abertura de ticket
│   │   └── shared/
│   │       ├── compliance.js  → auditoria e cadeia de hash
│   │       ├── diagnostico.js → laudo técnico explicável (XAI/SHAP)
│   │       └── mapa.js        → visualização geográfica de incidentes
    └── manutencao.js          → script da tela externa do técnico
├── index.html                 → aplicação principal SPA (protegida por login)
├── login.html                 → tela de autenticação
└── manutencao.html            → página isolada do técnico de manutenção (sem login)

machine_learning/
└── treinar_modelo.py      → treina o Random Forest com os dados do banco

ml_assets/
└── modelo_risco.pkl       → modelo já treinado, usado em produção

scripts/
├── popular_banco.py               → gera dados de telemetria (clima real + resto simulado)
└── popular_previsoes_historicas.py → roda o modelo em massa pra popular o histórico
```

---

## 🔧 Problemas do feedback da sprint anterior — o que foi corrigido

A nota da última sprint foi alta, entregamos algo funcional e bem comunicado. Mas o professor encontrou falhas reais, e aqui está o que foi feito com cada uma.

### A cadeia de hash não era imutável de verdade — ✅ corrigido

**Onde estava:** `risco_service.py`, no comando `MERGE`.
**O problema:** consultar o risco do mesmo equipamento duas vezes no mesmo dia sobrescrevia o registro antigo e recalculava um hash novo, quebrando a cadeia de auditoria.
**Como foi corrigido:** `risco_service.py` agora usa `INSERT` sempre, nunca sobrescreve. Durante o teste encontramos um bug extra que não estava no feedback original: a busca pelo "último hash" em `audit_service.py` podia empatar quando várias previsões eram geradas no mesmo segundo, causando hashes repetidos. Corrigido usando o identificador sequencial do registro em vez de data/hora. Criamos também um endpoint (`verificar_integridade_cadeia`) que audita a cadeia inteira sob demanda.

### Uma consulta (GET) estava alterando dados — ✅ corrigido

**Onde estava:** `main.py`, rota `GET /previsao/{equipamento_id}`.
**O problema:** a rota processava o modelo e gravava uma previsão nova a cada chamada, violando a lógica de API REST (GET deveria ser só leitura).
**Como foi corrigido:** separado em duas rotas: `POST /previsao/{id}` (processa e grava uma previsão nova) e `GET /previsao/{id}/ultima` (só lê a previsão mais recente, sem processar nada de novo). Testado chamando a rota de leitura várias vezes seguidas e confirmando que o hash retornado nunca muda.

### Mensagens de erro cruas voltavam pro usuário — ✅ corrigido

**Onde estava:** `main.py`, em `/telemetria` e `/historico`.
**O problema:** erro técnico completo do servidor aparecia pra quem estava usando a API.
**Como foi corrigido:** adicionado um tratador global de exceção — qualquer erro não previsto retorna mensagem genérica + código de rastreio pro cliente, com o detalhe técnico completo só no log do servidor. Encontramos um efeito colateral no meio do caminho: o registro de log de acesso não gravava nada quando a requisição falhava (a exceção "vazava" antes do registro rodar). Corrigido também.

### Não existia identidade de quem acessava — ✅ corrigido

**Onde estava:** `main.py`, chave única `API_KEY` compartilhada por todo mundo.
**O problema:** o sistema sabia que alguém tinha acessado, mas não sabia quem, nem separava operador de gestor de seguradora.
**Como foi corrigido:** sistema de login completo (email/senha com hash bcrypt, token JWT com papel), com hierarquia real de criação de usuário (Sompo cria Gestor, Gestor cria Operador) e controle de acesso por máquina baseado em vínculo real (fazenda do gestor, vínculo direto do operador). Testado com casos de acesso permitido e negado, incluindo tentativa de um papel acessar rota de outro papel.

### A telemetria perdia informação quando atualizada — ✅ corrigido

**Onde estava:** `data_service.py`, função `salvar_telemetria_db`.
**O problema:** o `MERGE` só atualizava 3 de 9 campos quando já existia leitura do dia, descartando o resto.
**Como foi corrigido:** trocado por `INSERT` sempre, preservando todos os campos de cada leitura enviada. Testado inserindo duas leituras do mesmo equipamento no mesmo dia com valores diferentes em todos os campos, e confirmando que nenhum campo se perdeu.

### Só era possível ter uma leitura por equipamento por dia — ✅ corrigido

**Onde estava:** `config_db.py`, chave primária composta por equipamento e data.
**O problema:** um sensor de verdade manda dado várias vezes ao dia, e essa trava impedia isso.
**Como foi corrigido:** trocada a chave primária composta por um identificador sequencial próprio em cada tabela (previsão, telemetria, dado bruto). Essa mudança foi a base que permitiu corrigir os dois problemas de cadeia de hash e perda de telemetria também, já que os dois dependiam dessa mesma limitação.

---

## ✅ O que já estava bom e não precisou mudar

- Separação em camadas (`ml_service`, `audit_service`, `risco_service`, `data_service`), arquitetura limpa.
- O uso de SHAP no `ml_service.py`, incluindo o filtro de redundância entre variável bruta e indicador.
- O pool de conexões Oracle (`database.py`).

---

## 🎯 Onde estamos agora

Com a base técnica corrigida e testada, e o sistema de login/hierarquia/controle de acesso funcionando de ponta a ponta, o foco passa a ser o que está descrito no README principal: sistema de ticket, manutenção com link pro técnico, telas novas por persona, e a evolução do motor de risco com dado real de satélite e indicador de estabilidade.

**Lembrete técnico:** o histórico de previsões precisa ser regenerado (`popular_previsoes_historicas.py`) antes de qualquer demonstração final, já que parte dele eu apaguei durante os testes de correção da cadeia de hash.
