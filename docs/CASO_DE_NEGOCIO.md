# MAIA — Caso de Negócio

Este documento existe para explicar por que o MAIA não é apenas um exercício técnico, mas uma solução com valor comercial real e mensurável para a Sompo Seguros e para o setor de seguros de equipamentos agrícolas como um todo.

---

## O problema real por trás do produto

A Sompo já vende um produto chamado Equipamentos Agrícolas — Benfeitorias, com cobertura para incêndio, tombamento, colisão, roubo, danos elétricos, entre outros riscos. O que esse produto não tem hoje é visibilidade contínua sobre o estado de cada máquina segurada. A seguradora só fica sabendo de um problema depois que ele já virou sinistro — quando o prejuízo já está feito e a única alternativa é pagar a indenização.

Isso tem um custo direto: sinistros de equipamento agrícola envolvem valores altos (uma colheitadeira ou trator de grande porte pode valer centenas de milhares de reais), e boa parte desses eventos — incêndio por superaquecimento, dano por falta de manutenção, colisão por condição de solo desfavorável — tem sinais que aparecem antes do sinistro acontecer. O problema não é falta de informação; é falta de um sistema que capture e aja sobre essa informação a tempo.

O MAIA foi desenhado para preencher exatamente essa lacuna: transformar a gestão de risco de reativa (paga-se depois do prejuízo) para preventiva (evita-se o prejuízo antes de acontecer).

---

## Como o MAIA gera valor para cada parte envolvida

### Para a Sompo (a seguradora)

- **Redução de sinistralidade.** Cada sinistro evitado é economia direta — o valor de uma indenização de equipamento agrícola frequentemente ultrapassa R$ 300 mil. Evitar uma fração desses eventos ao longo de uma carteira de apólices já paga o investimento na plataforma muitas vezes.
- **Visibilidade de carteira em tempo real.** A Sompo enxerga, num único painel, quantas máquinas seguradas estão em risco crítico agora e qual o valor total de capital exposto — informação que hoje simplesmente não existe de forma consolidada.
- **Argumento comercial para retenção e upsell.** Quando o sistema identifica um risco que não está coberto pela apólice atual do cliente (por exemplo, um alerta relacionado a dano elétrico quando o gestor só tem cobertura básica), isso vira uma oportunidade natural de oferecer upgrade de plano — o produto vende a si mesmo no momento certo.
- **Evidência documentada para negociação de sinistro.** Quando um sinistro acontece de fato, a Sompo tem em mãos o histórico completo de manutenção, os relatos do operador e a cadeia de decisões do modelo — reduzindo disputa e acelerando a análise.

### Para o Gestor de Frota (o cliente segurado)

- **Menos tempo parado, menos prejuízo operacional.** Uma máquina parada por quebra não planejada custa tanto quanto o próprio reparo, às vezes mais, em uma safra com janela de tempo apertada.
- **Priorização objetiva de manutenção.** Em vez de decidir "no feeling" qual máquina revisar primeiro, o gestor tem um ranking real baseado em risco.
- **Prova de diligência.** Ter um histórico documentado de manutenção e resposta a alertas é exatamente o tipo de evidência que facilita a relação com a seguradora em caso de sinistro.

### Para o Operador (quem está no campo)

- **Decisão de segurança em tempo real**, sem precisar interpretar dado técnico — só a informação de que precisa para decidir se é seguro continuar operando.
- **Voz ativa no sistema.** O relato de um problema observado no campo não se perde — ele entra diretamente na próxima análise de risco daquela máquina, fazendo o operador parte ativa da inteligência do sistema, não apenas receptor de alerta.

---

## O ciclo completo de prevenção

O que diferencia o MAIA de um simples painel de score é que ele fecha um ciclo real de ação:

```
Sensor/telemetria + relato do operador
        ↓
Modelo de risco processa e explica o motivo
        ↓
Alerta chega ao Gestor (e, se necessário, à Sompo)
        ↓
Gestor solicita manutenção → técnico executa → registro fica documentado
        ↓
Score é reprocessado com a manutenção já considerada
        ↓
Se o problema for sinistro real, o Gestor escala diretamente para a Sompo tratar
```

Nenhuma etapa fica solta. O dado vira ação, a ação vira registro, e o registro retroalimenta a próxima decisão.

---

## Estimativa de impacto financeiro (exercício de ordem de grandeza)

Este é um exercício ilustrativo, não uma projeção comercial formal, mas serve para dimensionar a escala do problema:

- Um trator ou colheitadeira de médio a grande porte segurado costuma ter valor declarado entre R$ 200 mil e R$ 500 mil.
- Incêndio por superaquecimento é uma causa de sinistro conhecida no setor e, na maioria dos casos, precedida por sinais detectáveis (temperatura do motor fora da faixa segura, uso contínuo prolongado).
- Se a antecipação de um único evento de incêndio evitar a perda total de uma máquina de valor médio de R$ 350 mil, esse único caso já justifica o investimento em monitoramento de uma frota inteira por vários anos.
- Ao multiplicar esse raciocínio por uma carteira com centenas ou milhares de equipamentos segurados, a redução de poucos pontos percentuais na sinistralidade já representa economia na casa dos milhões de reais para a seguradora.

---

## Por que este é um produto, não um protótipo

O MAIA já resolve, hoje, os requisitos que transformam uma prova de conceito em algo com caminho real para produção:

- Hierarquia de acesso real (Sompo, Gestor, Operador, Técnico), cada um vendo exatamente o que precisa.
- Cadastro de ativos vinculado a valor real de apólice, não dado fictício.
- Catálogo de cobertura idêntico ao produto real da Sompo (Básica, Adicional, Condições Particulares).
- Auditoria com cadeia de integridade verificável — decisão relevante para o contexto regulatório de seguros.
- Fluxo de manutenção com evidência documentada, atendendo a uma exigência contratual real do setor.
- Sistema de escalonamento de sinistro direto da operação para a seguradora, sem intermediário manual.

Esse é o argumento central do caso de negócio do MAIA: não construímos uma demonstração de machine learning. Construímos o esqueleto de um produto de seguros que uma seguradora poderia, com ajustes incrementais, colocar em operação real.
