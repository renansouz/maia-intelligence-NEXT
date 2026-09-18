# MAIA - Evolução do Projeto

Este documento conta a trajetória do MAIA ao longo do desafio: como a proposta amadureceu, o que aprendemos em cada etapa, e como cada rodada de avaliação nos ajudou a construir um produto mais sólido do que tínhamos no início. Não escondemos os pontos que precisaram de ajuste, eles fazem parte de como um projeto de verdade evolui, e achamos que mostrar esse percurso é mais honesto (e mais forte) do que apresentar só o resultado final como se ele tivesse nascido pronto.

---

## Sprint 1 - Estruturando a ideia

Começamos com a proposta de usar dados de clima, solo e operação para antecipar riscos operacionais em equipamentos agrícolas, com foco inicial em máquinas atuando perto de corpos d'água. Nessa etapa, entregamos a arquitetura conceitual (diagrama de 8 camadas), a definição de personas e um dataset de exemplo ainda bastante enxuto. O feedback recebido foi claro sobre dois pontos de melhoria: as User Stories precisavam de critérios de aceite mais formais, e o volume de dado de exemplo era insuficiente para sustentar qualquer análise séria. Levamos os dois pontos para as sprints seguintes como prioridade.

## Sprint 2 - Da ideia ao motor de inteligência

Demos o salto mais importante da nossa jornada técnica: passamos de um dataset de exemplo praticamente vazio para um pipeline real, combinando dados climáticos reais (Open-Meteo) com um motor de geração de risco probabilístico, em vez de uma regra fixa de threshold, o modelo passou a aprender padrão de verdade a partir dos dados. Escolhemos Random Forest justamente pelo equilíbrio entre poder preditivo e possibilidade de explicação via SHAP, alinhado à necessidade real de uma seguradora de entender e auditar cada classificação de risco. O feedback dessa entrega reconheceu a maturidade metodológica do trabalho e apontou apenas ajustes de organização de documentação, nada estrutural.

## Sprint 3 - Integração de ponta a ponta

Consolidamos o sistema como um fluxo único e funcional: backend em FastAPI orquestrando a entrada de telemetria, o motor de risco e uma camada de auditoria baseada em hash encadeado, com frontend próprio já com a identidade visual da Sompo. Essa foi uma entrega ambiciosa, muito mais código, muito mais integração, e, junto com a ambição, veio o tipo de feedback que só aparece quando um sistema é testado de verdade sob a lupa técnica: identificamos, com a ajuda da avaliação recebida, que a cadeia de auditoria podia ser sobrescrita em vez de permanecer imutável, que uma rota de leitura estava alterando dados, que erros internos podiam vazar detalhe técnico, e que o controle de acesso ainda dependia de uma chave única compartilhada em vez de identidade real por usuário.

Encaramos isso não como retrocesso, mas como exatamente o tipo de auditoria rigorosa que uma seguradora de verdade faria antes de confiar num sistema, e tratamos cada ponto como prioridade máxima da etapa seguinte.

## Consolidação final - de protótipo a produto

Esta foi a fase em que transformamos o MAIA de um sistema funcional em uma plataforma completa, corrigindo com rigor cada ponto identificado e construindo, em cima dessa base mais sólida, tudo que faltava para o produto fazer sentido de ponta a ponta para os quatro perfis que o usam no dia a dia.

**Integridade e confiabilidade técnica.** Reescrevemos a cadeia de auditoria para que cada decisão do modelo gere sempre um novo registro, nunca uma sobrescrita, e, no processo de validar essa correção, encontramos e resolvemos também uma fonte sutil de colisão de hash que nem tinha sido apontada no feedback original, o que reforçou nossa cultura de testar cada correção contra cenários reais de concorrência, não apenas contra o caso feliz. Criamos também um endpoint dedicado que verifica a integridade de toda a cadeia sob demanda, uma prova concreta e reproduzível de que o histórico de decisões nunca foi adulterado.

**Semântica de API e tratamento de erro.** Separamos claramente as operações de leitura das operações que processam e gravam dado, e implementamos um tratamento centralizado de exceções: qualquer erro interno agora é registrado com um código de rastreio para investigação técnica, sem nunca expor detalhe de implementação para quem está usando o sistema.

**Identidade e controle de acesso reais.** Substituímos a chave de acesso única por um sistema completo de autenticação com login, senha protegida por hash e sessão por token, com três papéis (Sompo, Gestor, Operador) e uma hierarquia de criação de conta que espelha como a relação comercial funciona de verdade, a seguradora cadastra o gestor, o gestor administra a própria equipe. Cada rota do sistema passou a verificar não apenas o papel de quem está pedindo, mas também se aquela pessoa realmente tem vínculo com a máquina em questão.

**Do score ao ciclo completo de prevenção.** Foi aqui que o MAIA deixou de ser "um sistema que calcula risco" para virar uma plataforma de gestão de risco de verdade:

- Implementamos um sistema de ticket que permite ao operador relatar problemas reais observados na máquina, e fizemos esse relato retroalimentar automaticamente a próxima análise de risco gerada pelo modelo, fechando um ciclo entre observação humana e inteligência do sistema.
- Construímos o fluxo de manutenção externa, com geração de link único e temporário para o técnico responsável registrar o serviço realizado sem precisar de conta no sistema, e conectamos essa conclusão ao reprocessamento automático do score da máquina.
- Demos à Sompo um caminho direto de escalonamento: quando um ticket é, de fato, um sinistro, o gestor pode encaminhá-lo diretamente para a seguradora tratar, sem etapa manual no meio do caminho.
- Agregamos tickets e manutenções numa linha do tempo única por máquina, dando a qualquer pessoa autorizada uma visão completa da vida operacional daquele equipamento.
- Conectamos o sistema ao catálogo real de cobertura de apólice da Sompo (Básica, Adicional, Condições Particulares) e ao valor segurado de cada máquina, o que tornou possível calcular exposição financeira com dado real, não estimativa de mercado.
- Demos ao operador uma camada de contexto adicional, previsão climática das próximas horas, com alerta simples de chuva ou vento forte, reforçando a proposta de decisão preventiva na ponta mais crítica da operação.

---

## O que essa trajetória demonstra

Cada rodada de feedback que recebemos apontou algo real, e cada correção nos deixou tecnicamente mais maduros do que estávamos antes, não só corrigimos o que foi apontado, como em mais de uma ocasião fomos além, encontrando e resolvendo problemas adjacentes que a própria correção revelou. O MAIA de hoje carrega a marca dessa evolução: uma arquitetura testada sob pressão, uma hierarquia de acesso pensada para o negócio real de seguros, e um conjunto de funcionalidades que nasceram diretamente das lacunas que identificamos no caminho, não de uma lista de requisitos definida no primeiro dia.
