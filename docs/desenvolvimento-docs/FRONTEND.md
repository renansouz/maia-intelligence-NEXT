# 🌾 Documentação Técnica e Arquitetura do Frontend - MAIA

Este documento consolida as escolhas arquiteturais, a estrutura de código, o design system e os princípios de engenharia aplicados no desenvolvimento de todo o ecossistema frontend do **MAIA (Sistema de Gestão e Prevenção de Risco Agrícola)**, construído em parceria com a **seguradora Seguros**.

---

## 🏛️ Visão Geral e Contexto de Produto

O MAIA foi concebido para transformar a gestão de risco de equipamentos agrícolas de uma postura puramente reativa para uma atuação preventiva, em total aderência às Condições Gerais de apólices reais (como o produto _seguradora Benfeitorias_).

Nós estruturamos a aplicação considerando que diferentes usuários possuem urgências e níveis de literacia digital distintos. Por isso, o sistema não é apenas um painel genérico de dados, mas um produto segmentado por **quatro personas reais**, garantindo que cada usuário encontre exatamente o que precisa para decidir em poucos segundos.

---

## 🛠️ Stack Tecnológica

Optamos por manter uma arquitetura moderna, ágil e de alta performance, sem a complexidade desnecessária de steps de build pesados:

- **Core:** JavaScript puro (ES6 Modules nativos), garantindo separação limpa de escopo e reutilização.
- **Estilização:** Tailwind CSS via CDN, customizado com variáveis globais para a identidade visual corporativa.
- **Mapas:** Leaflet.js para visualização geográfica e espacial de riscos.
- **Gráficos e Indicadores:** Plotly.js para gauges de risco (XAI) e gráficos estatísticos de frota.
- **Ícones:** Lucide Icons para suporte visual semântico em toda a interface.
- **Servidor:** Servido nativamente de forma estática pelo backend integrado em FastAPI.

---

## 🗂️ Estrutura de Pastas do Frontend

Nós organizamos o diretório `frontend/` de forma modular, separando a lógica central de infraestrutura web das telas específicas de cada persona:

```text
frontend/
├── assets/
│   └── seguradora-logo.webp        → Identidade visual oficial da seguradora Seguros
├── css/
│   └── styles.css             → Variáveis de cores globais e classes utilitétricas
├── js/
│   ├── core/                  → Núcleo técnico da aplicação
│   │   ├── api.js             → Camada centralizada de fetch, headers e interceptação de 401
│   │   ├── auth.js            → Gerenciamento de sessão, tokens JWT e papéis (localStorage)
│   │   └── router.js          → Roteador SPA base-hash com suporte a drill-down
│   ├── views/                 → Telas e módulos de interface por persona
│   │   ├── seguradora/
│   │   │   ├── dashboard.js   → Central de Risco Executiva (Visão Global e Exposição)
│   │   │   └── cadastros.js   → Módulo de cadastro de ativos na apólice
│   │   ├── gestor/
│   │   │   ├── dashboard.js   → Painel de Propriedades (Fazendas) e Frota
│   │   │   ├── tickets.js     → Central de Tickets e Alertas da Equipe
│   │   │   └── cadastros.js   → Cadastro de fazendas e criação de operadores
│   │   ├── operador/
│   │   │   └── painel.js      → Painel enxuto de campo integrado a previsão do tempo
│   │   └── shared/
│   │       ├── compliance.js  → Auditoria de Decisões e cadeia de hash imutável
│   │       ├── detalhe-maquina.js → detalhes e laudo técnico compartilhado (seguradora, Gestor e Operador)
│   │       └── mapa.js        → Mapeamento de distribuição de frotas
│   └── manutencao.js          → Script isolado para o fluxo do técnico externo
├── app.html                 → Ponto de entrada SPA (protegido por autenticação JWT)
├── login.html                 → Tela de autenticação com tratamento de erros por `detail`
└── manutencao.html            → Página isolada do Técnico de Manutenção (sem login/token na URL)
```

---

## 👥 Arquitetura de Navegação e Jornada por Persona

Nós implementamos o conceito de que **a tela inicial (Home) de cada persona deve responder imediatamente à sua pergunta mais urgente**, eliminando a necessidade de navegação profunda para tomadas de decisão diárias.

### 1. seguradora (Administrador / Seguradora)

- **Home (Central de Risco):** Exibe 4 indicadores executivos de decisão (Risco Crítico, Exposição Financeira em R$, Sinistros em Aberto, Gestores Ativos), seguidos por uma listagem prioritária dos ativos mais vulneráveis e um mini-mapa de dispersão geográfica.
- **Abas de Investigação:** Gestores Ativos, Auditoria de Decisões (Compliance com cadeia de hash) e Gestão de Apólices/Cadastros.

### 2. Gestor de Frota

- **Home (Meu Painel):** Resumo imediato de frotas em atenção, tickets pendentes da equipe e status da apólice contratada.
- **Navegação em Drill-down:** Listagem natural organizada por Propriedades (Fazendas), onde o gestor pode inspecionar os equipamentos vinculados, gerar links exclusivos de manutenção para o técnico de campo e gerenciar ocorrências da equipe.

### 3. Operador de Máquinas

- **Home (Painel Operacional):** Desenvolvida propositalmente de forma enxuta e direta, sem gráficos ou jargões estatísticos. Apresenta o status do ativo atribuído em linguagem natural de negócio (ex: _"Atenção: verifique antes de operar"_) e um card meteorológico integrado com alertas preventivos para a janela de trabalho.
- **Ação Rápida:** Botão dedicado para reportar problemas em campo através de um sistema de tickets categorizados.

### 4. Técnico de Manutenção (Sem Login)

- **Fluxo Externo (`manutencao.html?token=XYZ`):** Uma página completamente isolada, acessada via link único gerado pelo gestor. O técnico visualiza o ativo e o motivo da manutenção, preenche o relatório de execução e encerra o ciclo, sem qualquer fricção de senha ou navegação pelo sistema.

---

## 🎨 Princípios de Design, UI/UX e Engenharia Aplicados

Nós conduzimos o desenvolvimento sob rigorosos padrões de qualidade de produtos digitais modernos (referências em usabilidade direta como Stripe, Linear e Apple):

1. **Estados Visuais Assíncronos:** Todas as requisições assíncronas possuem tratamento completo com três estados definidos: carregando (skeletons ou spinners discretos), sucesso (renderização de dados) e erro formatado.
2. **Propagação de Erros da API:** As mensagens de erro exibidas ao usuário refletem exatamente o atributo `detail` retornado pelo backend em FastAPI, garantindo transparência técnica. Se houver falha de rede, uma mensagem amigável de conexão é acionada.
3. **Segurança e Resiliência de Sessão:** O ecossistema valida o token JWT em todas as transações protegidas. Caso ocorra expiração (código HTTP 401), a aplicação limpa o armazenamento local e redireciona o usuário para o login de forma transparente.
4. **Formatação de Dados de Negócio:** Valores monetários seguem estritamente o padrão brasileiro (`R$ 000.000,00`), assim como datas e horários (`dd/mm/aaaa`), garantindo familiaridade para o operador no campo e para o analista na seguradora.
5. **Desempenho e Leveza:** A ausência de frameworks monolíticos pesados garante carregamento instantâneo, baixo consumo de banda em campo e total independência de ferramentas complexas de compilação.
