<p align="center">
  <img src="./frontend/assets/preview.png" alt="Preview do MAIA">
</p>

<h1 align="center">MAIA 🌾</h1>
<h3 align="center">Monitoramento, Análise e Inteligência Agrícola</h3>
<p align="center"><i>Do conhecimento sobre a natureza à inteligência sobre o risco.</i></p>

---

A civilização maia observava o céu e os ciclos da terra para decidir com mais segurança. O MAIA segue o mesmo princípio, com dados reais de sensor, clima e operação no lugar da observação do céu, transformando informação agrícola em inteligência de risco para seguradoras.

## 🎯 O problema

Seguradoras de equipamento agrícola descobrem o sinistro depois que ele já aconteceu. Motor superaquecendo, manutenção atrasada, solo saturado, os sinais existem antes do prejuízo, mas raramente chegam a quem decide a tempo.

## 💡 A solução

Uma plataforma que liga telemetria real da máquina, relato do operador em campo e regras da apólice num fluxo só: detectar o desvio, explicar o porquê, e colocar seguradora, gestor e operador na mesma página antes do sinistro.


Telemetria da máquina → Motor de IA → Alerta explicado → Ação (manutenção/ticket) → Auditoria


---

## 👥 Quem usa

| Persona | Faz o quê |
|---|---|
| 🏢 *Sompo* | Cadastra máquinas e gestores, vê exposição financeira real, trata sinistros escalados |
| 👔 *Gestor* | Cadastra propriedades/operadores, vincula máquinas, solicita manutenção |
| 🧑🌾 *Operador* | Vê a própria máquina em linguagem simples, relata problemas |
| 🔧 *Técnico* | Sem login, link único e temporário para registrar manutenção |

---

## 🧠 O motor de IA

Treinado com telemetria *real* de operação agrícola via CAN/J1939 (dataset Tümosan). Usa *Isolation Forest, não um classificador de "sinistro sim/não", porque não existe base real rotulada de falha, e fingir que existe seria desonesto. O modelo aprende o comportamento normal multivariado da máquina e aponta o desvio, com **perfil evolutivo* (cada máquina passa de uma referência geral para um perfil só dela conforme acumula histórico). Validado com leave-one-session-out, a forma correta de validar dado temporal sem vazamento entre treino e teste.

📄 Detalhes completos: [docs/MODELO_IA.md](docs/MODELO_IA.md)

---

## ✅ Status do projeto

*Pronto e testado:* login com RBAC real por máquina, cadastro completo de ativos (máquina↔️gestor↔️propriedade↔️operador), motor de IA com explicação, cadeia de auditoria com hash verificável, sistema de ticket com escalonamento para a Sompo, manutenção externa com reprocessamento automático de score, histórico agregado por máquina, catálogo de cobertura real da apólice, exposição financeira real, clima operacional, frontend completo para as 4 personas.

*Em andamento:* sensor físico (ESP32 conectado ao CAN), segundo modelo de risco (solo úmido/proximidade de água com dado de satélite real), deploy em ambiente público, retreino automático de perfil por máquina.

---

## 🛠️ Stack

| Camada | Tecnologia |
|---|---|
| Backend | FastAPI + Oracle |
| Auth | JWT + bcrypt |
| IA | Isolation Forest + RobustScaler (scikit-learn) |
| Frontend | HTML + JS (ES6 Modules) + Tailwind, sem build step |

---

## 📚 Documentação

| Doc | Conteúdo |
|---|---|
| [docs/CASO_DE_NEGOCIO.md](docs/CASO_DE_NEGOCIO.md) | Por que isso importa pra Sompo, impacto financeiro |
| [docs/ARQUITETURA.md](docs/ARQUITETURA.md) | Fluxo de dados, estrutura, decisões técnicas |
| [docs/MODELO_IA.md](docs/MODELO_IA.md) | Dataset, metodologia, validação, limitações |
| [docs/SEGURANCA_E_AUDITORIA.md](docs/SEGURANCA_E_AUDITORIA.md) | Auth, RBAC, hash chain, rastreabilidade |

---

## 🔧 Como executar

bash
git clone https://github.com/renansouz/maia-intelligence-NEXT.git
cd maia-intelligence-NEXT
python3.12 -m venv venv && source venv/bin/activate
pip install -r requirements.txt
cp .env.example .env   # preencha ORACLE_*, API_KEY, JWT_SECRET_KEY, ADMIN_EMAIL, ADMIN_SENHA
python3 -m app.core.config_db
python3 -m scripts.popular_demo   # opcional: dados de demonstração
uvicorn app.main:app --reload


Acesse http://127.0.0.1:8000/login.html.

---

<p align="center"><i>Enterprise Challenge — FIAP & Sompo Seguros — 2026</i></p>
