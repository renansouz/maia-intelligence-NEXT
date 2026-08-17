<h1 align="center">MAIA 🌾🚜</h1>
<h3 align="center">Monitoramento e Análise Inteligente Agrícola</h3>

<p align="center">
  <img src="https://img.shields.io/badge/Status-Sprint%203%20Completo-DF082A?style=for-the-badge" />
  <img src="https://img.shields.io/badge/Stack-FastAPI%20%2B%20ML%20%2B%20Oracle-black?style=for-the-badge" />
  <img src="https://img.shields.io/badge/Empresa-Sompo%20Seguros-white?style=for-the-badge&logo=sompo" />
</p>

## 🎥 Demonstração MAIA

Assista ao vídeo técnico da solução integrada (Backend, IA e Auditoria):
[LINK DO VÍDEO AQUI]

---

> **No agronegócio, o custo do "ponto cego" operacional é medido em milhões.**
> Um solo saturado ou uma inclinação excessiva não avisam antes de um tombamento.
> O MAIA foi desenvolvido para transformar o silêncio dos dados em decisões preventivas,
> garantindo que a Sompo Seguros e seus segurados estejam sempre à frente do risco.

---

## 👨‍🎓 Equipe MAIA

| Nome           | RM       |
| -------------- | -------- |
| Renan Souza    | RM568958 |
| Kevin Santiago | RM573808 |
| Thiese Novaes  | RM572659 |
| João Vitor     | RM572969 |
| Talles Duran   | RM572772 |

---

## 🔴 O Problema: A Cultura Reativa no Campo

Atualmente, a gestão de frotas agrícolas opera sob demanda. O monitoramento humano é falho ao correlacionar variáveis invisíveis: a umidade profunda do solo, o desgaste cumulativo por horas de uso e a instabilidade geométrica do terreno.

Quando o incidente ocorre, o prejuízo já é total. Para a **Sompo Seguros**, isso significa alta sinistralidade; para o produtor, o comprometimento da safra.

## 💡 A Resposta: Ecossistema MAIA

O MAIA é uma plataforma de **Inteligência Preditiva e Auditoria Digital** que elimina o ponto cego operacional. Diferente de soluções de BI tradicionais, o MAIA atua em três camadas críticas:

1.  **Gêmeo Digital (Synthetic Twin):** Desenvolvemos um motor de síntese de dados que emula o comportamento mecânico e ambiental real, validado por correlações físicas (Chuva x Saturação de Solo).
2.  **Motor XAI (Explainable AI):** Através do algoritmo **SHAP**, a IA do MAIA justifica cada score de risco, permitindo que a seguradora audite o motivo técnico de cada alerta.
3.  **Protocolo de Auditoria Imutável:** Cada predição é selada via **Hash Chain (SHA-256)**, criando um histórico de conformidade à prova de violações.

---

## 🛠️ Stack Tecnológica

| Camada             | Tecnologia            | Justificativa                                                             |
| ------------------ | --------------------- | ------------------------------------------------------------------------- |
| **Backend**        | FastAPI + oracledb    | Alta performance e suporte a Session Pooling para conexões Oracle.        |
| **Banco de Dados** | Oracle Database       | Padrão corporativo para persistência de dados críticos e logs de acesso.  |
| **Intelligence**   | Random Forest + SHAP  | Equilíbrio perfeito entre poder preditivo e explicabilidade técnica.      |
| **Segurança**      | Criptografia SHA-256  | Implementação de Hash Chain para garantia de integridade jurídica.        |
| **Frontend**       | Vanilla JS + Tailwind | UI customizada com a identidade Sompo, focada em UX corporativa e leveza. |

---

## 📊 Resultados e Rigor Científico

O motor de risco do MAIA foi validado através de benchmark formal, superando significativamente o baseline em precisão e inteligência.

| Métrica                    | Árvore de Decisão | Random Forest |        Impacto        |
| :------------------------- | :---------------: | :-----------: | :-------------------: |
| **ROC-AUC**                |      0.5625       |  **0.7072**   | **+25% de precisão**  |
| **Risk Coverage (>= 30%)** |      35.06%       |  **58.38%**   | **+66% de cobertura** |

> O modelo MAIA foi calibrado para priorizar a **Cobertura de Risco**, garantindo que 58% dos incidentes reais sejam detectados precocemente dentro das zonas de Atenção ou Alerta.

---

## 🕐 Simulação Histórica: São Paulo - Fev/2024

Validamos o MAIA contra o evento real de chuvas extremas em São Paulo. O sistema identificou corretamente a progressão de risco da frota:

| Período       | Condição Real    | Resultado MAIA      | Status     |
| ------------- | ---------------- | ------------------- | ---------- |
| 01/02 a 09/02 | Estabilidade     | 20.4% Avg Score     | 🟢 ESTÁVEL |
| 10/02         | Tempestade Local | 31.1% Avg Score     | 🟡 ATENÇÃO |
| 19/02 a 22/02 | Chuvas Intensas  | **41.6% Avg Score** | 🔴 ALERTA  |

---

## 📖 Documentação Técnica em Camadas

Para um mergulho profundo nas decisões de engenharia, acesse nossos documentos dedicados:

| Documento                                    | O que você vai encontrar                                                                        |
| -------------------------------------------- | ----------------------------------------------------------------------------------------------- |
| [📐 ARCHITECTURE.md](./docs/ARCHITECTURE.md) | Detalhamento do desacoplamento, Session Pooling, Middleware de Logging e Diagrama Mermaid.      |
| [🤖 MACHINE_LEARNING.md](./docs/ML.md)       | Análise do Gêmeo Digital, engenharia de features, explicabilidade SHAP e métricas de validação. |
| [🛡️ SECURITY.md](./docs/SECURITY.md)         | Matemática do Hash Chain, proteção de API Key e conformidade com auditoria Sompo.               |

---

## 🔧 Como Executar Localmente

**Pré-requisitos:** Python 3.11+, Git, credenciais de acesso ao Oracle da FIAP (fornecidas pela instituição). Não é necessário Node.js nem VPN — o banco Oracle da FIAP é acessível remotamente.

### 1. Clonar o repositório

```bash
git clone https://github.com/renansouz/maia-intelligence-NEXT.git
cd maia-intelligence-NEXT
```

### 2. Criar e ativar o ambiente virtual

**macOS / Linux:**

```bash
python3 -m venv venv
source venv/bin/activate
```

**Windows (PowerShell):**

```powershell
python -m venv venv
.\venv\Scripts\Activate.ps1
# Se der erro de permissão, rode antes:
# Set-ExecutionPolicy -ExecutionPolicy RemoteSigned -Scope CurrentUser
```

### 3. Instalar dependências

```bash
pip install -r requirements.txt
```

### 4. Configurar variáveis de ambiente

Copie `.env.example` para `.env` e preencha com suas credenciais:

```bash
# macOS/Linux
cp .env.example .env
# Windows
copy .env.example .env
```

```dotenv
ORACLE_USER="seu_usuario"
ORACLE_PASSWORD="sua_senha"
ORACLE_HOST="oracle.fiap.com.br"
ORACLE_PORT=1521
ORACLE_SERVICE="ORCL"
API_KEY="escolha-uma-chave-qualquer"
```

### 5. Configurar a chave de API no frontend

O frontend precisa da mesma `API_KEY` definida no `.env`, num arquivo separado (não versionado):

```bash
cp frontend/js/config.example.js frontend/js/config.js
```

Edite `frontend/js/config.js` e garanta que o valor seja **idêntico** ao `API_KEY` do seu `.env`.

### 6. Popular o banco de dados

> O modelo de Machine Learning já vem treinado e versionado em `ml_assets/`. Só é necessário retreinar se quiser regenerar do zero (veja seção de ML).

```bash
python3 -m app.core.config_db
python3 -m scripts.popular_banco
python3 -m scripts.popular_previsoes_historicas
```

> ⚠️ O segundo comando consulta a API pública Open-Meteo. Em caso de erro de rede/limite de requisições, aguarde ~1 minuto e rode novamente.

### 7. Iniciar o sistema

```bash
python3 -m uvicorn app.main:app --reload
```

Acesse **http://127.0.0.1:8000/** no navegador.

### Problemas comuns

- **Aviso `pandas only supports SQLAlchemy...`** no terminal: inofensivo, pode ignorar.
- **Alterações no frontend não aparecem:** o navegador cacheia agressivamente arquivos `.js`. Use `Cmd+Shift+R` (Mac) ou `Ctrl+Shift+R` (Windows) para forçar recarregamento.
- **`403 Forbidden` ao acessar dados:** confira se `frontend/js/config.js` existe e se a chave bate exatamente com o `.env`.

---

Enterprise Challenge - FIAP & Sompo Seguros - 2026
