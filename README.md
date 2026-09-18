# MAIA 🌾 - Sistema de Gestão e Prevenção de Risco Agrícola

> Este README é o nosso documento de planejamento vivo pro Sprint 4. Aqui tem tudo: o que decidimos, o que já construímos, o que ainda falta, e por quê. Conforme formos avançando isso vira o README final de verdade.

<img src="./frontend/assets/preview.png" alt="Preview of the Site">
---

## 🎯 O que o MAIA é agora

O MAIA deixou de ser só um sistema de monitoramento que cospe um score de risco. Virou uma plataforma completa que a Sompo, os gestores de frota, os operadores e os técnicos de manutenção usam no dia a dia, com login de verdade, hierarquia de acesso, cadastro de máquina e fazenda, sistema de manutenção com histórico, ticket de problema, e (o motivo de tudo isso existir) prevenção de sinistro antes que ele aconteça.

A ideia surgiu de pesquisar a fundo o produto real da Sompo pra equipamentos agrícolas (Benfeitorias). Não estamos inventando um problema genérico de agro, estamos construindo em cima do que a própria Sompo já vende e cobre:

- **Cobertura Básica:** incêndio, raio, explosão, vendaval, tombamento, colisão, roubo, furto, quebra de vidro, dano em transporte.
- **Coberturas Adicionais:** danos elétricos, aluguel a terceiros, responsabilidade civil, despesas de salvamento.
- **Condições Particulares:** equipamento operando perto de água, equipamento alugado/operado por terceiro.

Isso mudou como pensamos o produto: o MAIA não é mais "um app de risco agrícola qualquer", é um app desenhado pra funcionar junto com uma apólice real da Sompo, e cada alerta que ele gera pode (e deve) ser cruzado com o que está coberto na apólice daquele cliente.

---

## 👥 As quatro personas

### Sompo (administrador do sistema)
- Vê todos os gestores de frota e todas as máquinas cadastradas.
- Cadastra as máquinas que fazem parte da apólice.
- Cria as contas dos gestores de frota.
- Acompanha sinistros, estatísticas, histórico completo de tudo.
- Gera relatórios (Excel/dashboard).
- Cobra os gestores, gerencia planos e cobertura.
- Vê o valor de exposição financeira (quanto risco em aberto representa em R$).

### Gestor de Frota
- Cadastra as fazendas dele.
- Cria as contas dos operadores dele.
- Vincula máquina à fazenda e vincula operador à máquina (um operador pode operar quantas máquinas o gestor quiser vincular).
- Vê o score de risco de todas as máquinas das fazendas dele.
- Recebe alerta de sinistro e de risco climático.
- Solicita manutenção e gera o link único que vai pro técnico.
- Aprova/acompanha os tickets abertos pelos operadores dele.
- Vê histórico completo das fazendas dele.
- A cobertura contratada (Básica/Adicional/Particular) fica vinculada ao gestor, isso decide quais tipos de alerta fazem sentido pra ele. Se um gestor só tem cobertura básica e o sistema identificar um risco de dano elétrico (que é adicional), o alerta pode vir acompanhado de "esse risco não está coberto na sua apólice atual", o que é também uma oportunidade de a Sompo oferecer upgrade de plano.

### Operador
- Vê só as máquinas que estão vinculadas a ele.
- Recebe alerta com explicação em linguagem simples (não é "SHAP value 0.34", é "risco alto por causa de X e Y").
- Abre ticket relatando problema real na máquina (categoria + observação livre).
- Esse ticket não é só suporte, ele retroalimenta o modelo. Quando o sistema for gerar a próxima análise daquela máquina, ele considera não só sensor e clima, mas o que o operador relatou de verdade. Isso fecha um ciclo que a maioria dos projetos parecidos não tem: humano validando e enriquecendo a máquina.

### Técnico de Manutenção (sem login)
Não é usuário do sistema, é alguém externo que executa a manutenção física. O fluxo é:
1. O gestor (ou o próprio sistema, a partir de um alerta) solicita manutenção.
2. Gera-se um link único com token, sem necessidade de senha.
3. O técnico abre esse link, registra data, horário e um comentário sobre o que foi feito.
4. Isso vira um registro permanente de histórico de manutenção (data do problema, data da correção, o que foi feito).
5. Depois da manutenção registrada, o score daquela máquina é reprocessado.

Esse histórico de manutenção é exatamente o tipo de coisa que a Sompo pede em contrato: vencimento, evidência de manutenção, histórico. Se a gente seguir isso à risca, cobre uma exigência real de apólice, não só uma "boa prática" nossa.

---

## 🔐 Hierarquia e cadastro

```
SOMPO
  └── cria conta de GESTOR
  └── cadastra a MÁQUINA
       └── GESTOR cadastra FAZENDA
       └── GESTOR vincula MÁQUINA à FAZENDA
       └── GESTOR cria conta de OPERADOR
       └── GESTOR vincula OPERADOR à MÁQUINA
```

Cada papel só cria o papel/vínculo imediatamente abaixo dele. Ninguém pula hierarquia: a Sompo não cria operador direto, o gestor não cria outro gestor, o operador não cadastra nada.

---

## 📋 O que cada tela mostra, por persona

| Tela/funcionalidade | Sompo | Gestor | Operador |
|---|---|---|---|
| Mapa geral de máquinas | ✅ (todas) | ✅ (só as dele) | ❌ |
| Ranking de criticidade/manutenção | ✅ | ✅ | ❌ |
| Camada econômica (R$ de exposição) | ✅ | ❌ | ❌ |
| Compliance/auditoria (cadeia de hash) | ✅ (tudo) | ✅ (só dele) | ❌ |
| Alerta simples da própria máquina | ❌ | ❌ | ✅ |
| Chat com IA explicando o risco | ✅ | ✅ | ✅ |
| Abrir ticket de problema | ❌ | ❌ | ✅ |
| Ver tickets da equipe | ❌ | ✅ | ❌ (só os seus) |
| Cadastrar máquina | ✅ | ❌ | ❌ |
| Cadastrar fazenda / vincular operador | ❌ | ✅ | ❌ |
| Solicitar manutenção / gerar link do técnico | ❌ | ✅ | ❌ |

O que cada um vê ao logar, antes de navegar pra qualquer tela:
- **Sompo:** total de máquinas em risco crítico agora, exposição financeira total.
- **Gestor:** quantas máquinas dele estão em atenção/crítico, tickets pendentes da equipe.
- **Operador:** status da própria máquina, direto, tipo "Trator 03: Atenção, verifique antes de operar".

---

## 💡 Qual sinistro estamos resolvendo (e por quê)

Pesquisamos os problemas mais comuns do setor e não vamos tentar resolver todos com a mesma profundidade, isso é receita pra não terminar nada bem em um mês.

**Incêndio e superaquecimento: problema principal.** É o mais simples de resolver de forma completa dentro do prazo: sensor de temperatura do motor (simulável no Wokwi), cruzado com tempo de uso contínuo. É causa e efeito fácil de explicar pra qualquer pessoa ("acumulou palha seca perto do motor quente, o sistema avisa antes de virar incêndio"), e é uma das coberturas básicas da apólice real da Sompo.

**Solo úmido / proximidade de água: evolução do que já existe.** Já era a base do motor de risco original. A evolução é trazer dado de satélite real via radar SAR (Sentinel-1, Google Earth Engine), que enxerga o solo mesmo com nuvem/chuva cobrindo tudo, isso vem de um projeto nosso anterior (Vigia.IA) que já validamos tecnicamente, só estamos adaptando pro contexto do MAIA. Essa condição também bate com uma das "Condições Particulares" da apólice real (equipamento operando perto de água).

**Indicador de estabilidade/tombamento: complemento pra demonstração.** Tombamento é o maior volume de sinistro do setor, mas resolver ele por completo (física de estabilidade, giroscópio, peso de carga) é trabalho grande demais pro prazo. A saída foi: calcular um indicador de estabilidade a partir de inclinação + umidade do solo como feature nova do modelo que já existe (sem virar uma rede neural nova do zero), e usar um sensor de giroscópio (MPU6050) no Wokwi pra mostrar isso funcionando ao vivo. Não resolve o problema inteiro, mas é uma fatia honesta e demonstrável.

**Danos elétricos — fora do escopo por enquanto.** Pesquisamos e não achamos um caminho técnico razoável de resolver isso com o tempo e o conhecimento que temos agora. Fica de fora dessa entrega.

---

## 🛡️ Segurança, login e auditoria (o que já está pronto)

O sistema de login e controle de acesso já está funcionando de ponta a ponta:

- Login por email/senha, com senha protegida por hash (bcrypt), token de sessão (JWT) válido por 24 horas.
- Três papéis reais no token: SOMPO, GESTOR, OPERADOR, cada rota da API confere o papel antes de deixar passar.
- Controle de acesso por máquina: um gestor só processa/vê o score das máquinas vinculadas às fazendas dele; um operador só vê as máquinas vinculadas a ele. Isso já foi testado na prática, inclusive o caso de alguém tentar acessar uma máquina que não é dele (bloqueado corretamente).
- Cadastro de máquina, fazenda, e os vínculos (máquina↔fazenda, máquina↔operador) todos funcionando via API, cada um com a checagem de que a pessoa é realmente dona daquilo que está tentando vincular.
- A cadeia de hash de auditoria (que prova que uma previsão de risco não foi alterada depois de gerada) foi corrigida, testada, e tem um endpoint que verifica a integridade de toda a cadeia sob demanda.
- Toda requisição que falha é logada no servidor com um código de rastreio, mas o usuário só recebe uma mensagem genérica, nenhum detalhe técnico interno vaza pra fora.
- A tela de login já existe no frontend, protegendo o acesso ao restante do sistema, sem token válido, a pessoa é redirecionada pro login antes de ver qualquer tela.

O que ainda falta nessa frente: sistema de ticket (operador abre, gestor resolve), geração do link único do técnico de manutenção sem login, e reprocessamento automático do score depois que uma manutenção é registrada.

---

## 🎫 Sistema de ticket (retroalimentação do modelo)

Categoria pré-definida + observação livre, aberto pelo operador direto na máquina dele. O ponto principal não é o ticket em si, é o que ele alimenta: a próxima vez que o modelo for gerar uma análise daquela máquina, ele deve considerar o que foi relatado, não só sensor e clima. Isso ainda está para ser desenhado e implementado.

---

## ✅ Como isso atende o que o Sprint 4 pede

- Refinamento de código/arquitetura e tratamento de exceção, feito nos pontos identificados no feedback da sprint anterior (ver `docs/estado-atual.md`).
- Refinamento de dado e modelo, dado real de satélite/clima substituindo parte do dado sintético, indicador de estabilidade novo.
- Validação de integração com fontes reais/simuladas, sensor via Wokwi e APIs públicas reais.
- Segurança e rastreabilidade, login por papel, controle de acesso por máquina, cadeia de auditoria corrigida e verificável.
- Relatórios e visualização por persona, telas diferentes pra Sompo, Gestor e Operador, de acordo com o que cada um precisa decidir.
- Documentação, este README e o `docs/estado-atual.md` mostrando a evolução real desde as sprints anteriores.

---

## 📌 Em aberto

- Sistema de ticket completo (operador abre, gestor resolve, alimenta o modelo).
- Geração do link único de manutenção pro técnico sem login, e reprocessamento do score depois da manutenção registrada.
- Telas novas do frontend por persona (dashboard Sompo, dashboard Gestor, tela do Operador, formulário do técnico).
- Cadastro de fazenda e vínculo fazenda/máquina/operador no frontend (hoje só existe via API).
- Integração do dado de satélite real (Sentinel-1) no motor de risco.
- Fórmula exata do indicador de estabilidade (tombamento), a definir com pesquisa técnica.
- Qual sensor virtual usar no Wokwi pra cada problema (temperatura pro incêndio, giroscópio pra estabilidade).
- Se o chatbot (watsonx) entra nesta sprint ou fica como extra se sobrar tempo.
- Campo de tipo de cobertura do gestor influenciando o conteúdo do alerta.

---

## 🗂️ Estrutura de pastas atual

```
app/
├── core/
│   ├── database.py       → conexão com o Oracle (pool de conexões)
│   └── config_db.py      → cria/atualiza todas as tabelas do banco
├── models/
│   └── schemas.py        → formato dos dados aceitos pela API
├── services/
│   ├── data_service.py         → telemetria (salvar/buscar)
│   ├── processamento_service.py → cálculo de indicadores de risco
│   ├── ml_service.py           → modelo de IA, score e explicação (SHAP)
│   ├── audit_service.py        → geração do hash de auditoria
│   ├── risco_service.py        → orquestra ML + hash + persistência
│   ├── auth_service.py         → hash de senha, geração/validação de JWT, controle de papel
│   ├── user_service.py         → cadastro e busca de usuário, criação do usuário Sompo inicial
│   ├── fazenda_service.py      → cadastro e listagem de fazenda
│   └── maquina_service.py      → cadastro de máquina, vínculos, controle de acesso por equipamento
└── main.py                → rotas da API

docs/
└── estado-atual.md        → o que já foi corrigido desde a sprint anterior e o que falta

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
└── treinar_modelo.py

ml_assets/
└── modelo_risco.pkl

scripts/
├── popular_banco.py
└── popular_previsoes_historicas.py
```

---

## 🔧 Como Executar Localmente

**Pré-requisitos:**

- **Python:** Recomendado **3.11** ou **3.12**.
  - *Nota: Versões experimentais como 3.13 ou 3.14 exigem compiladores C++ extras e não são recomendadas.*
- **Git:** Para clonagem do repositório.
- **Credenciais Oracle:** Acesso ao Oracle da FIAP.

### 1. Clonar o repositório

```bash
git clone https://github.com/renansouz/maia-intelligence-NEXT.git
cd maia-intelligence-NEXT
```

### 2. Criar e ativar o ambiente virtual

**macOS / Linux:**
```bash
python3.12 -m venv venv
source venv/bin/activate
```

**Windows (PowerShell):**
```powershell
py -3.12 -m venv venv
.\venv\Scripts\Activate.ps1
# Se houver erro de permissão de execução de scripts no Windows:
# Set-ExecutionPolicy -ExecutionPolicy RemoteSigned -Scope CurrentUser
```

### 3. Instalar dependências

```bash
pip install -r requirements.txt
```

### 4. Configurar variáveis de ambiente

```bash
cp .env.example .env
```

```dotenv
ORACLE_USER="seu_usuario"
ORACLE_PASSWORD="sua_senha"
ORACLE_HOST="oracle.fiap.com.br"
ORACLE_PORT=1521
ORACLE_SERVICE="ORCL"

API_KEY="chave-para-ingestao-de-telemetria-por-sensor"

JWT_SECRET_KEY="uma-string-longa-e-aleatoria-so-sua"
ADMIN_EMAIL="email-do-usuario-sompo-inicial"
ADMIN_SENHA="senha-do-usuario-sompo-inicial"
```

### 5. Popular o banco de dados

```bash
python3 -m app.core.config_db
python3 -m scripts.popular_banco
python3 -m scripts.popular_previsoes_historicas
```

> O segundo comando consulta a API pública Open-Meteo. Em caso de erro de rede/limite de requisições, aguarde ~1 minuto e rode novamente.

### 6. Iniciar o sistema

```bash
uvicorn app.main:app --reload
```

Acessa **http://127.0.0.1:8000/login.html** no navegador. No primeiro start, um usuário Sompo é criado automaticamente com o email/senha definidos em `ADMIN_EMAIL`/`ADMIN_SENHA`, é esse que você usa pra logar a primeira vez e começar a cadastrar gestor, máquina, etc.

---

Enterprise Challenge - FIAP & Sompo Seguros - 2026
