# MAIA 🌾 - Monitoramento e Análise Inteligente Agrícola

> Este README é o nosso documento de planejamento vivo pro Sprint 4. Esquece a versão de tecnologia antiga por enquanto, aqui vai tudo que discutimos até agora: estrutura de login, personas, ideias de sinistro avaliadas, e o que falta decidir. Conforme formos avançando, isso vira o README final de verdade.

---

## 🎯 O que o MAIA precisa ser

Uma plataforma que a Sompo, os gestores de frota e os operadores realmente usam no dia a dia, não um sistema que só existe pra gerar nota de sprint. Ela precisa antecipar sinistro, ser auditável (comprovação jurídica de que o aviso foi dado), e se comunicar entre as três pontas.

---

## 🔐 Estrutura de Login e Personas

### Hierarquia (quem enxerga quem)

```
SOMPO (seguradora)
  └── vê todos os Gestores e todas as máquinas do sistema
       └── GESTOR DE FROTA
            └── vê os Operadores dele e as máquinas atribuídas a ele
                 └── OPERADOR
                      └── vê só a(s) máquina(s) atribuída(s) a ele
```

Não são sistemas separados, é a mesma base de dados, com visão recortada por papel (RBAC de verdade).

### Quem cadastra o quê

| Ação                                   | Quem faz                          |
| -------------------------------------- | --------------------------------- |
| Criar conta de Gestor                  | Sompo                             |
| Criar conta de Operador                | Gestor (do próprio time)          |
| Cadastrar máquina nova                 | Gestor propõe → **Sompo aprova**  |
| Vincular máquina a um Operador         | Gestor                            |
| Abrir ticket de problema/observação    | Operador                          |
| Ver histórico de auditoria/compliance  | Sompo (tudo) e Gestor (só o dele) |
| Ver camada econômica (R$ de exposição) | Sompo                             |
| Desativar/remover gestor ou máquina    | Sompo                             |

**Por quê a máquina precisa de aprovação da Sompo:** essas máquinas fazem parte da apólice de seguro da Sompo. Não faz sentido o Gestor simplesmente cadastrar e já valer, é igual seguro de verdade, ninguém está coberto só porque preencheu um formulário. Fluxo: Gestor cadastra → status **pendente** → Sompo aprova → status **ativa** (só aí conta pro sistema de risco valer pra seguro). Isso também vira um ponto de auditoria: fica registrado quem aprovou e quando.

### Dados essenciais no cadastro de uma máquina

| Campo                                        | Por quê                                                        |
| -------------------------------------------- | -------------------------------------------------------------- |
| ID/identificador do equipamento              | Chave de tudo                                                  |
| Tipo de máquina (trator, colheitadeira etc.) | Referência pra features específicas no futuro                  |
| Fazenda/localização (coordenada real)        | Resolve o problema do mapa com posição fake que tínhamos antes |
| Ano/modelo                                   | Contexto de manutenção                                         |
| Gestor responsável                           | Vínculo hierárquico                                            |
| Operador(es) vinculado(s)                    | Vínculo hierárquico                                            |
| Data da última manutenção                    | Alimenta indicador de manutenção atrasada                      |
| Status                                       | pendente / ativa / inativa                                     |

### Tela de login

Um único formulário (usuário/senha). O backend identifica o papel (JWT com claim de role) e redireciona pro dashboard certo. Cada papel pode ter uma cor de destaque sutil pra facilitar identificar durante a demo (Sompo = vermelho Sompo, Gestor = azul, Operador = verde).

### Telas e funcionalidades por persona

| Tela/funcionalidade                 | Sompo      | Gestor          | Operador        |
| ----------------------------------- | ---------- | --------------- | --------------- |
| Mapa geral de máquinas              | ✅ (todas) | ✅ (só as dele) | ❌              |
| Ranking de criticidade/manutenção   | ✅         | ✅              | ❌              |
| Camada econômica (R$ exposição)     | ✅         | ❌              | ❌              |
| Compliance/auditoria (hash chain)   | ✅ (tudo)  | ✅ (só dele)    | ❌              |
| Alerta simples da própria máquina   | ❌         | ❌              | ✅              |
| Chat com IA (explicação do risco)   | ✅         | ✅              | ✅              |
| Abrir ticket de problema/observação | ❌         | ❌              | ✅              |
| Ver tickets abertos da equipe       | ❌         | ✅              | ❌ (só os seus) |
| Aprovar cadastro de máquina         | ✅         | ❌              | ❌              |
| Cadastrar máquina/operador          | ❌         | ✅ (propõe)     | ❌              |

### Página principal por persona (o que vê ao logar)

- **Sompo:** total de máquinas em risco crítico agora + exposição financeira total + cadastros pendentes de aprovação.
- **Gestor:** quantas máquinas dele estão em atenção/crítico + tickets pendentes da equipe.
- **Operador:** status da(s) máquina(s) dele, simples — ex: "Trator 03: Atenção — verifique antes de operar".

---

## 🎫 Sistema de Tickets (feedback do operador)

Ideia: o operador pode abrir um ticket relatando um problema real na máquina (categorias pré-definidas + campo de observação livre, podendo ser até por email). Isso não é só um canal de suporte, **esse dado retroalimenta a IA**. Quando o modelo for gerar a análise de risco, ele passa a considerar não só sensor e clima, mas o **estado real relatado pelo operador**. Isso fecha um loop que praticamente nenhum outro grupo vai ter: humano validando e enriquecendo a máquina.

---

## 💡 Avaliação das Ideias de Sinistro

A pergunta mais importante do projeto inteiro é: **qual sinistro a gente realmente vai resolver?** Levantamos 4 problemas reais do setor e fui analisando cada um.

### 1. Acidentes operacionais (colisão, tombamento, capotamento)

Esse é o maior em volume, mais de 50% dos casos, então dá muita vontade de ser esse o foco. Mas sendo sincero comigo mesmo: é o mais difícil de resolver de forma 100% funcional no tempo que temos. Envolve física de estabilidade, sensor de inclinação/giroscópio, e um monte de variável (peso da carga, tipo de terreno, velocidade em curva). Se a gente tentar abraçar isso inteiro corre risco real de não terminar funcionando de ponta a ponta, que é exatamente o que o enunciado da Sprint 4 mais cobra. Minha conclusão: não vamos tentar resolver o tombamento inteiro, mas dá pra pegar uma fatia boa dele, um indicador de estabilidade calculado a partir de inclinação + umidade do solo (sem virar uma rede neural nova, só uma feature física a mais no modelo que já temos) e usar um sensor de giroscópio (MPU6050) no Wokwi pra mostrar isso ao vivo na demo. Não é o produto inteiro resolvido, é uma fatia honesta e demonstrável.

### 2. Incêndio e superaquecimento

Pesquisei e essa acho que é a nossa melhor aposta como problema **principal**. É mais simples de resolver de forma completa: sensor de temperatura do motor (dá pra simular no Wokwi com um DHT22 ou sensor de temperatura mesmo), cruzado com tempo de uso contínuo e talvez umidade baixa do ambiente (palha seca é mais perigosa em dia seco). É causa-e-efeito fácil de explicar pra qualquer pessoa leiga no pitch ("acumulou palha seca perto do motor quente, sistema avisa antes de virar incêndio"), e dá pra deixar 100% funcional de verdade dentro do prazo que temos. Motivo pelo qual acho que deveríamos priorizar esse como o problema central da nossa história.

### 3. Danos elétricos

Pesquisei e não achei um caminho claro de como resolver isso com o que temos de tempo e conhecimento no time. Minha recomendação: descartar essa opção por enquanto.

### 4. Solo úmido / proximidade de rio

Esse é basicamente o que o MAIA já resolve hoje (o motor de risco atual usa exatamente isso). A diferença é que dava pra deixar isso muito mais forte usando o projeto Vigia.IA que fizemos antes: em vez de só usar previsão de chuva (Open-Meteo), dá pra puxar dado de satélite real via radar SAR (Sentinel-1, através do Google Earth Engine), que enxerga o solo mesmo com nuvem/chuva forte cobrindo tudo. Isso transforma uma parte que já é "ok" em algo com dado real de peso, sem que a gente precise inventar do zero, é só trazer essa tecnologia que já validei em outro projeto pro contexto do MAIA.

### Conclusão dessa análise

Não vamos tentar resolver os 4 ao mesmo tempo com a mesma profundidade, isso é o caminho certo pra não terminar nada bem. A ideia é: **incêndio/superaquecimento como problema central e mais completo**, **solo úmido/proximidade de água potencializado com dado de satélite real** como a evolução natural do que já existe, e **um indicador simples de estabilidade/tombamento** como algo a mais pra impressionar na demo, sem virar o produto inteiro. Dano elétrico fica de fora dessa entrega.

---

## 🛡️ Segurança e Auditoria (o que muda)

- Login real com papel (JWT), substituindo a chave única compartilhada.
- Cadeia de hash corrigida: cada evento vira registro novo (nunca sobrescreve), com endpoint de verificação da cadeia.
- Separação correta entre rotas de leitura (GET) e rotas que processam/gravam (POST).
- Mensagens de erro genéricas pro usuário final, log completo só internamente.
- Registro de aprovação de máquina pela Sompo também entra na cadeia de auditoria — reforça a ideia de "comprovação jurídica" que discutimos.

---

## ✅ Como isso atende o que o Sprint 4 pede

- Refinamento de código/arquitetura e tratamento de exceção → correção dos 7 pontos do feedback da Sprint 3.
- Refinamento de dado e modelo → dado real (satélite/clima) substituindo parte do sintético, novo indicador de estabilidade.
- Validação de integração com fontes reais/simuladas → sensor via Wokwi + APIs públicas reais rodando juntas.
- Segurança e rastreabilidade → login por papel, hash chain corrigido, aprovação de máquina auditada.
- Relatórios e visualização por persona → dashboards diferentes pra Sompo, Gestor e Operador.
- Documentação final → este README mostrando a evolução real desde as ultimas sprints.

---

## 📌 Em aberto (o que ainda vamos decidir juntos)

- Fórmula exata do indicador de estabilidade (tombamento) — a definir com pesquisa técnica.
- Qual sensor virtual usar no Wokwi pra cada problema (temperatura pro incêndio, giroscópio pra estabilidade).
- Se o chatbot (watsonx) entra nesta sprint ou fica como extra se sobrar tempo.
- Detalhamento final do schema novo do banco (login, tickets, aprovação de máquina, leitura contínua de sensor).


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
