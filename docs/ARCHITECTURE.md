# Arquitetura
```text
ESP32/CAN → janela 60 s → MODELO OPERACIONAL → score + explicação
                               │
                               ├→ histórico bruto
                               │    └→ candidatos aprovados → perfil individual
                               │
Cadastro/manutenção/clima/feedback ─→ MOTOR CONTEXTUAL
                               │
                               └────────→ SAÚDE GLOBAL
```

O modelo da máquina não recebe penalização arbitrária. Ele deve selecionar o perfil operacional adequado.

### Evolução do perfil
1. INITIAL: Tümosan/família é referência principal.
2. ADAPTING: histórico individual já permite treinar um candidato, mas o baseline continua como decisão principal.
3. INDIVIDUAL: após validação, o perfil da unidade pode assumir a referência principal; baseline permanece como fallback.

Retreino deve ser versionado e em lote, nunca a cada pacote CAN.
