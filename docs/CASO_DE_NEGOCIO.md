# MAIA — Caso de Negócio

Este documento explica por que o MAIA não é apenas um exercício técnico, mas uma solução com valor comercial real e mensurável para a Sompo Seguros e para o setor de seguros de equipamentos agrícolas como um todo.

---

## O problema real por trás do produto

A Sompo comercializa o produto **Equipamentos Agrícolas — Benfeitorias**, que oferece cobertura para incêndio, tombamento, colisão, roubo e danos elétricos. O gargalo estrutural desse modelo no mercado atual é a **falta de visibilidade contínua** sobre o estado operacional de cada ativo segurado. A seguradora via de regra toma conhecimento de uma falha apenas após a consolidação do sinistro — quando a única alternativa remanescente é a liquidação da indenização.

Isso gera um impacto financeiro severo: sinistros envolvendo colheitadeiras e tratores de grande porte atingem facilmente centenas de milhares de reais. Contudo, eventos críticos como superaquecimento de motor com risco de incêndio, desgaste excessivo por falha de manutenção ou operação em solo instável emitem sinais precursores rastreáveis.

O MAIA preenche essa lacuna ao transicionar o modelo de gestão de risco de **reativo** (indenização pós-sinistro) para **preventivo** (mitigação baseada em telemetria e IA explicável).

---

## Como o MAIA gera valor para o ecossistema

### Para a Sompo (a seguradora)

- **Redução de Sinistralidade (Loss Ratio):** A prevenção de uma fração dos eventos críticos em uma carteira de apólices gera economia direta, considerando que o valor médio de reposição de um ativo supera R$ 350 mil.
- **Visibilidade de Carteira em Tempo Real:** Um painel executivo centralizado que consolida o volume de máquinas em risco crítico e a exposição financeira total da carteira.
- **Argumento Comercial para Upsell:** O cruzamento automático entre o risco detectado e a apólice do cliente (ex: alerta de dano elétrico em apólice com cobertura estritamente básica) viabiliza ofertas direcionadas de upgrade de plano.
- **Segurança Jurídica e Regulatória (Auditoria por Hash):** Em caso de sinistro contestado, a seguradora dispõe de uma cadeia criptográfica imutável (Hash Chain) comprovando o histórico de alertas emitidos e as manutenções executadas, acelerando a regulação.

### Para o Gestor de Frota (o cliente segurado)

- **Mitigação do Tempo de Inatividade (_Downtime_):** Prevenção de quebras catastróficas em janelas de safra apertadas.
- **Manutenção Baseada em Condição:** Substituição de manutenções baseadas em "feeling" por um ranking objetivo de criticidade gerado por aprendizado de máquina.
- **Conformidade Contratual:** Histórico digital auditável que respalda o cumprimento das obrigações de conservação exigidas pela seguradora.

### Para o Operador (quem está no campo)

- **Segurança Operacional em Tempo Real:** Alertas traduzidos para linguagem natural e intuitiva, sem a exigência de interpretação de métricas estatísticas complexas.
- **Voz Ativa no Sistema:** O relato de um problema observado em campo retroalimenta diretamente o motor de risco da unidade, integrando o fator humano à inteligência preditiva.

---

## O ciclo completo de prevenção (Human-in-the-Loop)

O diferencial competitivo do MAIA reside no fechamento do ciclo operacional:

```
Telemetria CAN / Sensor + Relato do Operador
        ↓
Motor de IA (Isolation Forest + SHAP) processa e explica o desvio
        ↓
Alerta direcionado ao Gestor de Frota e à Seguradora
        ↓
Gestor gera link único e seguro para o Técnico externo
        ↓
Técnico registra a manutenção; o sistema reprocessa automaticamente o score de risco
        ↓
Se necessário, o Gestor escala o evento diretamente como sinistro para a Sompo
```

---

## Estimativa de impacto financeiro (Ordem de Grandeza)

- O valor venal de tratores e colheitadeiras de médio e grande porte varia entre R$ 200 mil e R$ 800 mil.
- Incêndios decorrentes de superaquecimento e acúmulo de material combustível são precedidos por desvios térmicos prolongados identificáveis pelo modelo operacional.
- A antecipação de eventos dessa natureza evita perdas totais de ativos, garantindo viabilidade econômica imediata à adoção da plataforma em escala de portfólio.

---

## Prontidão Comercial e Tecnológica

O MAIA supera o estágio de prova de conceito acadêmica por incorporar:

- Controle de acesso robusto com separação estrita por papéis e vínculos relacionais (RBAC).
- Catálogo de coberturas idêntico ao produto comercial real da Sompo.
- Trilha de auditoria criptográfica verificável sob demanda.
- Esteira automatizada de tickets, chamados externos e escalonamento para sinistros.

---

<p align="center"><i>Enterprise Challenge — FIAP & Sompo Seguros — 2026</i></p>
