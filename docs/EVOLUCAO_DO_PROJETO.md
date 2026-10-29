# MAIA - Evolução do Projeto

Este documento registra a trajetória evolutiva do MAIA ao longo do Challenge FIAP (Sprints 1 a 4). O histórico demonstra como a proposta amadureceu de uma concepção conceitual até um MVP funcional, validado e integrado, incorporando as diretrizes e feedbacks de cada entrega.

---

## Sprint 1 - Estruturação e Concepção do Problema

### O Ponto de Partida

O projeto nasceu da necessidade de endereçar a baixa previsibilidade de riscos operacionais em frotas agrícolas seguradas pela **Seguradora** (foco no produto _Agricultura Benfeitorias_). O cenário inicial focava em mitigar perdas em equipamentos operando em condições adversas, como proximidade de corpos d'água após períodos de chuva.

### Entregáveis da Etapa

- Arquitetura conceitual inicial em diagrama de camadas.
- Definição preliminar das quatro personas (Seguradora, Gestor, Operador e Técnico).
- Estruturação teórica de variáveis de risco ambiental e operacional.

### Feedback e Aprendizados

A avaliação destacou a clareza do escopo e das personas, mas pontuou a necessidade de formalizar as _User Stories_ com critérios de aceite rigorosos e de expandir o conjunto de dados para além de registros estáticos. Esses apontamentos orientaram diretamente o planejamento técnico das sprints seguintes.

---

## Sprint 2 - Engenharia de Dados e Motor Preditivo

### Evolução Técnica

Nesta fase, a solução ganhou base quantitativa real. Abandonamos as regras puramente estáticas de limiar (_threshold_) e estruturamos a base analítica com dados reais de barramento CAN (J1939) combinados a indicadores climáticos. Diferente de classificadores supervisionados tradicionais (inviáveis pela ausência de massa rotulada de falhas reais), optamos por algoritmos não supervisionados de detecção de anomalias (*Isolation Forest* com *RobustScaler*), permitindo identificar desvios multivariados do comportamento normal do maquinário com alta interpretabilidade.

### Entregáveis da Etapa

- Pipeline de ingestão e persistência de dados estruturados em banco relacional (Oracle).
- Implementação dos scripts de modelagem estatística e cálculo de scores de aderência por equipamento.
- Relatórios iniciais de validação de acurácia e correlação de variáveis críticas.

### Feedback e Aprendizados

O trabalho foi reconhecido pela maturidade metodológica ao empregar uma abordagem estatística coerente com a auditoria de apólices. Os apontamentos concentraram-se na consistência das referências cruzadas da documentação técnica no repositório.

---

## Sprint 3 - Integração End-to-End e Arquitetura de Serviços

### Evolução Técnica

O desafio da Sprint 3 foi a integração sistêmica. Unimos o backend em **FastAPI**, o banco de dados **Oracle**, o motor preditivo e uma interface web inicial refletindo a identidade visual da Seguradora.

### O Ponto de Virada (Auditoria Crítica)

A avaliação técnica sob rigorosa lupa apontou vulnerabilidades cruciais que uma seguradora real jamais aceitaria:

1. **Mutabilidade de Hash:** A cadeia de auditoria anterior realizava `MERGE` nas previsões diárias, sobrescrevendo registros e quebrando o encadeamento histórico.
2. **Semântica REST Inadequada:** Uma rota `GET` de consulta estava processando e gravando novas previsões colateralmente.
3. **Segurança Genérica:** O acesso dependia de uma chave única global (`API_KEY`) compartilhada, sem distinção de papéis ou rastreabilidade de quem executava cada ação.
4. **Perda de Telemetria:** A rotina de salvamento descartava campos secundários ao atualizar leituras do mesmo dia.

Encaramos esses apontamentos não como falhas isoladas, mas como o teste de estresse essencial para um produto corporativo de seguros. Cada item foi classificado como prioridade absoluta para a consolidação.

---

## Sprint 4 e Consolidação Final - De Protótipo a Produto de Mercado

A etapa final representou a consolidação estrutural, eliminando débitos técnicos e elevando o MAIA ao padrão de um MVP corporativo pronto para produção.

### Principais Marcos da Consolidação

1. **Imutabilidade e Verificabilidade da Cadeia de Auditoria:**
   - O serviço de risco (`risco_service.py` e `audit_service.py`) foi reescrito para operar exclusivamente com inserções sequenciais (`INSERT`), garantindo que o histórico de decisões do modelo seja imutável.
   - Implementação de um mecanismo de verificação de integridade sob demanda que recalcula a cadeia criptográfica (SHA-256) bloco a bloco.

2. **Segurança Corporativa com RBAC e JWT:**
   - Substituição da chave única por um sistema robusto de autenticação baseada em tokens **JWT** com papéis restritos (`SEGURADORA`, `GESTOR`, `OPERADOR`) e senhas protegidas por **hash bcrypt**.
   - Implementação de autorização em duas camadas (validação de papel combinada ao escopo relacional de propriedade/vínculo do ativo).

3. **Arquitetura de Motor Duplo (Mecânico + Ambiental):**
   - Além do motor operacional baseado em CAN (*Isolation Forest*), consolidou-se a camada de análise geoespacial de solo e terreno (*PCA Ambiental* via dados orbitais do Sentinel-1/GEE), atendendo diretamente às cláusulas de proximidade hídrica da apólice da Seguradora.

4. **Ciclo Completo de Prevenção e Retroalimentação Humana:**
   - **Tickets Operacionais:** Operadores relatam ocorrências no campo por meio de interface simplificada; os registros alimentam o contexto de risco analisado nas previsões subsequentes do modelo.
   - **Manutenção Externa Desimpedida:** Geração de links seguros com tokens de uso único (`manutencao.html`) permitindo que técnicos externos registrem serviços sem fricção de login.
   - **Escalonamento Direto de Sinistros:** Gestores podem encaminhar tickets críticos diretamente para a esteira de regulação da Seguradora com um único clique.
   - **Valoração de Apólice Real:** Integração com o catálogo de coberturas do produto _Benfeitorias_ e com o valor segurado dos ativos, permitindo o cálculo real de exposição financeira em Reais (R$).

---

## O que a Trajetória Demonstra

A evolução do MAIA reflete um ciclo real de desenvolvimento de software corporativo. Cada rodada de auditoria e feedback transformou o protótipo acadêmico em uma plataforma resiliente, com arquitetura testada sob pressão, governança de dados alinhada ao setor de seguros e fluxos operacionais desenhados para mitigar riscos reais no campo.
