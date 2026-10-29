# MAIA — Caso de Negócio e Viabilidade Comercial

Este documento consolida a tese de valor comercial, o alinhamento regulatório e o impacto financeiro mensurável que o MAIA traz para o mercado de seguros de equipamentos agrícolas.

---

## 1. O Problema Estrutural no Setor de Seguros Agrícolas

A Seguradora comercializa o produto **Equipamentos Agrícolas — Benfeitorias / Penhor Rural**, oferecendo coberturas vitais como incêndio, tombamento, colisão, roubo e danos elétricos. O gargalo estrutural desse modelo no mercado tradicional é a **cegueira operacional crônica**: a seguradora assume o risco no ato da emissão da apólice e só volta a interagir com o segurado quando um sinistro de alta monta já ocorreu.

Isso gera um impacto severo no _Loss Ratio_ (sinistralidade): a indenização de um único trator ou colheitadeira de grande porte varia entre R$ 200 mil e R$ 800 mil. Contudo, os principais motivadores desses sinistros — superaquecimento térmico com risco de incêndio, degradação mecânica por falha de manutenção ou operação em solos instáveis e margens de rios — emitem sinais precursores rastreáveis muito antes do evento catastrófico.

O MAIA resolve essa assimetria de informação ao transicionar a gestão de risco de **reativa** (indenização pós-prejuízo) para **preventiva e contínua** (mitigação em tempo real baseada em telemetria e inteligência orbital).

---

## 2. Proposta de Valor para o Ecossistema

### Para a seguradora (A Seguradora)

- **Redução Sistemática da Sinistralidade:** A antecipação de falhas mecânicas e de condições críticas de terreno evita perdas totais de ativos segurados, preservando diretamente a margem técnica da carteira.
- **Vistoria Digital e Contínua:** Para frotas onde a inspeção física prévia é dispensada por regra de aceitação (ex: tratores com menos de 2 anos), o MAIA atua como um inspetor virtual contínuo desde o primeiro dia de vigência.
- **Mitigação da Cláusula de Proximidade de Água:** Utilizando monitoramento orbital via satélite (Sentinel-1 SAR / GEE), o sistema valida se o equipamento está operando em áreas de risco hídrico em conformidade com as Condições Particulares da apólice.
- **Argumento Comercial para Upsell:** O cruzamento automatizado entre o risco detectado e a apólice do cliente (ex: detecção de anomalia elétrica em apólice com cobertura estritamente básica) viabiliza ofertas direcionadas de upgrade de plano.
- **Segurança Jurídica na Regulação (Hash Chain):** Em caso de contestação de sinistro, a seguradora dispõe de uma trilha de auditoria criptográfica imutável que comprova o envio de alertas preventivos e o histórico de manutenções.

### Para o Gestor de Frota (O Cliente Segurado)

- **Eliminação do _Downtime_ Não Planejado:** Prevenção de quebras catastróficas em janelas críticas de plantio e colheita.
- **Manutenção Baseada em Condição:** Substituição de manutenções empíricas por um ranking objetivo de criticidade gerado por aprendizado de máquina (_Isolation Forest_).
- **Conformidade Contratual Facilitada:** Histórico digital auditável que simplifica e acelera a comprovação de diligência perante a seguradora.

### Para o Operador (Quem está no Campo)

- **Segurança Operacional em Tempo Real:** Alertas traduzidos para linguagem natural e intuitiva, assegurando tomada de decisão rápida sob pressão.
- **Canal Direto de Relato (_Human-in-the-Loop_):** O reporte de falhas em campo retroalimenta diretamente o motor de inteligência da unidade, integrando a percepção humana ao modelo preditivo.

---

## 3. O Ciclo Completo de Governança e Prevenção

O diferencial competitivo do MAIA reside no fechamento absoluto do ciclo operacional:

```
Telemetria CAN (IoT) + Satélite SAR + Relato do Operador
        ↓
Motor de IA (Isolation Forest + PCA Ambiental + SHAP) processa e explica
        ↓
Alerta direcionado ao Gestor de Frota e à Seguradora
        ↓
Gestor gera link único e seguro para o Técnico externo atuar
        ↓
Técnico conclui o serviço; o sistema reprocessa automaticamente o score de risco
        ↓
Se necessário, o Gestor escala o evento diretamente como sinistro para a Seguradora
```

---

## 4. Estimativa de Impacto Financeiro (Ordem de Grandeza)

- Considerando um valor médio de reposição de **R$ 350.000,00** por ativo agrícola de médio/grande porte:
- A prevenção de **um único evento de incêndio ou perda total por capotagem** em decorrência de alerta antecipado já neutraliza o custo de implantação e monitoramento da plataforma em uma frota inteira por múltiplos anos.
- Em escala de portfólio para a Seguradora, a supressão de pontos percentuais na sinistralidade representa economia na casa de **milhões de reais**, elevando a competitividade da companhia no agronegócio.

---

## 5. Prontidão para Escala Comercial

O MAIA supera o estágio de protótipo acadêmico por incorporar os requisitos fundamentais para implantação corporativa:

- Hierarquia de acesso real (Seguradora, Gestor, Operador, Técnico) blindada por RBAC de duas camadas.
- Catálogo de coberturas aderente ao produto comercial real da Seguradora.
- Trilha de auditoria baseada em hash SHA-256 para atendimento regulatório.
- Esteira automatizada de tickets, chamados externos e escalonamento para sinistros sem fricção manual.

---

<p align="center"><i>Enterprise Challenge — FIAP — 2026</i></p>
