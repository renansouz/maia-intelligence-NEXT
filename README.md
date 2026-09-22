<p align="center">
  <img src="./frontend/assets/preview.png" alt="Preview do MAIA" width="100%">
</p>

<h1 align="center">MAIA 🌾</h1>
<h3 align="center">Monitoramento, Análise e Inteligência Agrícola</h3>
<p align="center"><i>Do conhecimento sobre a natureza à inteligência sobre o risco.</i></p>

---

O **MAIA** é uma plataforma avançada de prevenção de riscos operacionais e ambientais em frotas de equipamentos agrícolas, desenvolvida em parceria com a **Sompo Seguros**. A proposta central do sistema é transformar a gestão de seguros de uma atuação reativa (pagamento de sinistro após o prejuízo) para uma abordagem preventiva (antecipação de falhas e mitigação de perdas antes que o evento ocorra).

---

## 🎥 Apresentação

> 🔗 Assista à demonstração completa de ponta a ponta do sistema (até 5 minutos): [Acesse o Vídeo no YouTube (Não Listado)](https://youtube.com/link-do-video-aqui)

---

## 🎯 O Problema & A Solução

Atualmente, seguradoras de equipamentos agrícolas (como tratores e colheitadeiras de grande porte) registram sinistros de alto valor — como incêndios por superaquecimento, tombamentos e danos estruturais, sem visibilidade contínua do estado operacional dos ativos.

O **MAIA** conecta dados de telemetria real (CAN/J1939), relatórios de operadores em campo e as regras contratuais da apólice (Sompo Benfeitorias) em um ecossistema unificado:
$$\text{Telemetria / Sensor} \longrightarrow \text{Motor de IA (Anomalia)} \longrightarrow \text{Alerta Explicado} \longrightarrow \text{Ação Preventiva (Ticket/Manutenção)} \longrightarrow \text{Auditoria Imutável}$$

---

## 👥 As Quatro Personas do Ecossistema

| Persona                      | Papel e Atuação no Sistema                                                                                                                                                |
| :--------------------------- | :------------------------------------------------------------------------------------------------------------------------------------------------------------------------ |
| 🏢 **Sompo (Administrador)** | Visão executiva global, acompanhamento de exposição financeira em R$, análise de sinistros escalados, cadastro central de máquinas e emissão de diretrizes de apólice.    |
| 👔 **Gestor de Frota**       | Gestão de propriedades rurais (fazendas), vinculação de operadores a ativos, acompanhamento de tickets da equipe, e geração de ordens de manutenção com links exclusivos. |
| 🧑‍🌾 **Operador de Campo**     | Painel operacional simplificado focado em segurança, exibindo o status do ativo em linguagem natural e permitindo o reporte imediato de falhas (tickets).                 |
| 🔧 **Técnico de Manutenção** | Acesso externo e sem fricção por link único protegido por token (sem necessidade de login), permitindo o registro rápido de intervenções mecânicas.                       |

---

## 🧠 O Motor de Inteligência Artificial

O sistema emprega uma abordagem estatística e de aprendizado de máquina não supervisionado projetada especificamente para cenários industriais sem histórico rotulado de falhas:

- **Isolation Forest + RobustScaler:** Processa variáveis CAN (temperatura de arrefecimento, óleo, pressão, torque, RPM, combustível e velocidade) para aprender o comportamento multivariado normal do maquinário, detectando desvios operacionais.
- **Perfil Evolutivo por Unidade:** Evolui de uma referência inicial de domínio (_Tümosan_) para perfis comportamentais individuais conforme cada máquina acumula histórico confiável.
- **Explicabilidade (SHAP / Fatores):** Traduz desvios matemáticos complexos em fatores de influência claros para a tomada de decisão humana.

📄 _Detalhes metodológicos completos:_ [docs/MODELO_IA.md](docs/MODELO_IA.md)

---

## 🏗️ Arquitetura e Fluxo de Ponta a Ponta

O sistema é construído sobre uma arquitetura desacoplada e modular:

- **Backend:** FastAPI assíncrono conectado a um banco de dados relacional **Oracle Cloud**, utilizando pool de conexões otimizado.
- **Segurança e Rastreabilidade:** Autenticação por Tokens JWT com controle de acesso baseado em papéis (RBAC) de duas camadas (papel + vínculo direto com o ativo) e uma **Cadeia de Auditoria Baseada em Hash (SHA-256)** que garante a imutabilidade do histórico de decisões.
- **Frontend:** Single Page Application (SPA) em JavaScript puro (ES6 Modules) estilizada com Tailwind CSS, Leaflet.js e Plotly.js, sem dependência de build steps complexos.

📄 _Especificações arquiteturais completas:_ [docs/ARQUITETURA.md](docs/ARQUITETURA.md)

---

## 📚 Documentação Técnica Complementar

| Documento                                                      | Descrição e Conteúdo                                                                |
| :------------------------------------------------------------- | :---------------------------------------------------------------------------------- |
| [docs/CASO_DE_NEGOCIO.md](docs/CASO_DE_NEGOCIO.md)             | Viabilidade comercial, redução de sinistralidade e impacto financeiro para a Sompo. |
| [docs/ARQUITETURA.md](docs/ARQUITETURA.md)                     | Fluxo de dados end-to-end, diagramas, hierarquia RBAC e decisões de engenharia.     |
| [docs/MODELO_IA.md](docs/MODELO_IA.md)                         | Metodologia de Machine Learning, features CAN, validação e limitações do modelo.    |
| [docs/SEGURANCA_E_AUDITORIA.md](docs/SEGURANCA_E_AUDITORIA.md) | Mecanismos de criptografia bcrypt, tokens JWT e integridade da cadeia de hash.      |
| [docs/EVOLUCAO_DO_PROJETO.md](docs/EVOLUCAO_DO_PROJETO.md)     | Trajetória evolutiva da Sprint 1 à Sprint 4 e resiliência frente aos feedbacks.     |

---

## 🔧 Guia de Execução Local

### Pré-requisitos

- Python 3.11 ou 3.12 instalado.
- Credenciais de acesso ao banco Oracle Cloud da FIAP.

### Passo a passo para execução:

```bash
# 1. Clonar o repositório
git clone https://github.com/renansouz/maia-intelligence-NEXT.git
cd maia-intelligence-NEXT

# 2. Criar e ativar o ambiente virtual
python3.12 -m venv venv
source venv/bin/activate  # No Windows (PowerShell): .\venv\Scripts\Activate.ps1

# 3. Instalar as dependências do projeto
pip install -r requirements.txt

# 4. Configurar as variáveis de ambiente
cp .env.example .env
# Edite o arquivo .env preenchendo ORACLE_*, API_KEY, JWT_SECRET_KEY, ADMIN_EMAIL, ADMIN_SENHA e GEE_PROJECT_ID

# 5. Configurar o banco de dados e popular o cenário de demonstração
python3 -m app.core.config_db
python3 -m scripts.popular_demo

# 6. Iniciar a aplicação
uvicorn app.main:app --reload
```

Acesse o sistema no navegador através de: **`http://127.0.0.1:8000/login.html`**

---

<p align="center"><i>Enterprise Challenge — FIAP & Sompo Seguros — 2026</i></p>
