<h1 align="center">MAIA 🌾🚜</h1>
<h3 align="center">Monitoramento e Análise Inteligente Agrícola</h3>

<p align="center">
  <img src="https://img.shields.io/badge/Status-Sprint%203%20Completo-DF082A?style=for-the-badge" />
  <img src="https://img.shields.io/badge/Stack-FastAPI%20%2B%20ML%20%2B%20Oracle-black?style=for-the-badge" />
  <img src="https://img.shields.io/badge/Parceria-Sompo%20Seguros-white?style=for-the-badge" />
</p>

## 🎥 Demonstração

Vídeo técnico da solução integrada (backend, inteligência artificial e auditoria):
**[LINK DO VÍDEO AQUI]**

---

> No agronegócio, o risco raramente avisa antes de acontecer. Um solo que parece firme pode estar saturado por baixo. Uma máquina que "sempre funcionou" pode estar a poucas horas de uma falha por manutenção negligenciada. O prejuízo, quando chega, já chega inteiro — na máquina, na safra e no sinistro.
>
> **O MAIA existe para tirar o risco desse ponto cego.**

---

## 👨‍🎓 Equipe

| Nome           | RM       |
| -------------- | -------- |
| Renan Souza    | RM568958 |
| Kevin Santiago | RM573808 |
| Thiese Novaes  | RM572659 |
| João Vitor     | RM572969 |
| Talles Duran   | RM572772 |

---

## 🔴 O Problema

A gestão de frotas agrícolas ainda opera, em grande parte, de forma reativa: a decisão de manutenção ou de mudança de rota acontece depois que o problema já apareceu. Fatores como umidade acumulada do solo, desgaste progressivo por horas de uso e inclinação do terreno raramente são cruzados em tempo real — e é justamente essa combinação que antecede a maioria dos incidentes operacionais.

Para uma seguradora, isso significa sinistros que poderiam ter sido evitados com poucas horas de antecedência. Para o produtor rural, significa prejuízo direto na operação e, eventualmente, na safra.

## 💡 A Solução

O MAIA é uma plataforma de **inteligência preditiva e auditoria digital** para risco operacional agrícola. Três pilares sustentam a solução:

1. **IA Explicável (XAI).** O motor de risco não entrega só um número — ele entrega o motivo. Usando **SHAP**, cada predição é decomposta nos fatores que mais pesaram (chuva acumulada, inclinação, manutenção atrasada), permitindo que um gestor entenda e confie na decisão da IA, não apenas a aceite às cegas.
2. **Auditoria imutável.** Cada predição gerada é encadeada matematicamente à anterior via hash SHA-256, criando um histórico que não pode ser alterado sem quebrar a cadeia — uma prova de integridade que dá segurança jurídica para decisões automatizadas.
3. **Arquitetura de produto real.** Backend em FastAPI com pooling de conexões, frontend dedicado com a identidade visual da Sompo, e um pipeline de dados que combina clima real (Open-Meteo) com simulação de telemetria fisicamente correlacionada — não dados aleatórios soltos.

## 👥 Para quem foi feito

| Persona             | Necessidade                    | O que o MAIA entrega                                         |
| ------------------- | ------------------------------ | ------------------------------------------------------------ |
| **Operador**        | Agir com segurança no campo    | Alertas com fatores explicados em linguagem simples          |
| **Gestor de Frota** | Priorizar manutenção com dados | Ranking de equipamentos críticos, atualizado continuamente   |
| **Seguradora**      | Antecipar sinistros            | Score de risco auditável, com histórico imutável de decisões |

---

## 🛠️ Stack Tecnológica

| Camada               | Tecnologia                             | Por quê                                                                               |
| -------------------- | -------------------------------------- | ------------------------------------------------------------------------------------- |
| **Backend**          | FastAPI + oracledb                     | Alta performance, validação nativa de dados, documentação automática (Swagger)        |
| **Banco de Dados**   | Oracle Database                        | Persistência corporativa com pooling de conexões                                      |
| **Inteligência**     | Random Forest + SHAP                   | Equilíbrio entre poder preditivo e explicabilidade auditável                          |
| **Segurança**        | SHA-256 (Hash Chain) + API Key         | Integridade de dados e controle de acesso                                             |
| **Frontend**         | HTML + Tailwind CSS + JavaScript (ES6) | Controle total sobre a identidade visual da Sompo, sem overhead de build ou framework |
| **Dados climáticos** | Open-Meteo API                         | Dados reais e verificáveis, sem custo de licenciamento                                |

---

## 📊 Rigor Científico: Comparação de Modelos

O motor de risco do MAIA foi validado formalmente contra um modelo de árvore de decisão única, usando o mesmo conjunto de dados e a mesma métrica de avaliação usada em produção — ROC-AUC (capacidade de separar corretamente risco de normalidade) e cobertura de risco real dentro das faixas de alerta do sistema (≥30% de probabilidade).

| Modelo                   | ROC-AUC    | Cobertura de Risco Real (≥30%) |
| ------------------------ | ---------- | ------------------------------ |
| Árvore de Decisão        | 0.5625     | 35.06%                         |
| **Random Forest (MAIA)** | **0.7072** | **58.38%**                     |

Um ROC-AUC de 0,56 está muito próximo do acaso (0,50 = aleatório); 0,71 representa um modelo com poder de separação real. Na prática, isso significa que o Random Forest identifica **quase o dobro** de incidentes reais dentro das zonas de Atenção e Alerta, comparado ao modelo anterior — um ganho relativo de aproximadamente 25,7% no poder de separação (ROC-AUC) e 66% na cobertura de risco.

---

## 🕐 Validação Histórica: São Paulo, Fevereiro de 2024

Para verificar se o modelo reage de forma coerente a condições climáticas reais, rodamos a inferência do MAIA retroativamente sobre o histórico real de chuva de fevereiro de 2024 em São Paulo — mês com precipitação acima da média na região.

| Métrica do período                         | Resultado               |
| ------------------------------------------ | ----------------------- |
| Dias em condição Estável (score < 30%)     | 20 de 29 dias (69%)     |
| Dias em condição de Atenção (score 30–70%) | 9 de 29 dias (31%)      |
| Score mais alto do mês                     | 41,6% — 22 de fevereiro |
| Score mais baixo do mês                    | 8,3% — 25 de fevereiro  |

O sistema não emitiu nenhum alerta de risco crítico (>70%) no período — resultado coerente, já que fevereiro de 2024 em São Paulo teve chuva elevada, mas não um evento extremo isolado. O ponto relevante é a **correlação temporal**: os picos de score (10, 13, 19–20 e 22 de fevereiro) acompanham diretamente os dias de maior precipitação registrada pela Open-Meteo, e os menores scores (25 e 28 de fevereiro) coincidem com dias de estiagem dentro do mês. Isso demonstra que o modelo reage a variação climática real, não a um valor médio fixo.

---

## 📖 Documentação Técnica

Para o detalhamento de arquitetura, decisões de engenharia e a matemática por trás da auditoria, consulte:

| Documento                                    | Conteúdo                                                                                         |
| -------------------------------------------- | ------------------------------------------------------------------------------------------------ |
| [📐 ARCHITECTURE.md](./docs/ARCHITECTURE.md) | Diagrama de solução, decisões de arquitetura, pooling de conexões, middleware de rastreabilidade |
| [🤖 ML.md](./docs/ML.md)                     | Pipeline de dados, engenharia de features, explicabilidade SHAP, métricas completas              |
| [🛡️ SECURITY.md](./docs/SECURITY.md)         | Hash chain, controle de acesso, conformidade com auditoria                                       |

---

## 🔧 Como Executar Localmente

**Pré-requisitos:**

- **Python:** Recomendado **3.11** ou **3.12** (Versões Estáveis).
  - _Nota: Versões experimentais como 3.13 ou 3.14 exigem compiladores C++ extras e não são recomendadas._
- **Git:** Para clonagem do repositório.
- **Credenciais Oracle:** Acesso ao Oracle da FIAP (fornecidas pela instituição).

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
# O comando 'py -3.12' garante que você use a versão correta instalada no Windows
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

---

Enterprise Challenge - FIAP & Sompo Seguros - 2026
