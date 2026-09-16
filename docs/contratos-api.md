# Contratos de API - MAIA Frontend

Este documento define os payloads esperados para rotas que ainda estão sendo construídas no backend. O frontend usará dados mockados estruturados exatamente com estes formatos até a integração real.

## 1. GET /sompo/gestores-resumo

- **Descrição:** Retorna a lista de gestores da plataforma com contagem de fazendas, máquinas e status de risco agregado.
- **Response esperado (JSON):**

```json
[
  {
    "id_gestor": 1,
    "nome": "Carlos Mendes",
    "email": "carlos@fazendaboa.com",
    "total_fazendas": 3,
    "total_maquinas": 12,
    "tipo_cobertura": "COMPLETA",
    "status": "ATIVO",
    "maquinas_criticas": 2
  }
]
```

# 2. GET /gestor/fazendas-detalhe

- **Descrição:** Retorna as fazendas do gestor logado com suas respectivas máquinas e scores atuais.
- **Response esperado (JSON):**
  [
  {
  "id_fazenda": 1,
  "nome": "Fazenda Santa Rita",
  "cidade": "Ribeirão Preto",
  "latitude": -21.17,
  "longitude": -47.81,
  "maquinas": [
  { "equipamento_id": "EQP-RP-01", "tipo": "Trator", "score": 0.85, "classificacao": "ALTO" },
  { "equipamento_id": "EQP-RP-02", "tipo": "Colheitadeira", "score": 0.15, "classificacao": "BAIXO" }
  ]
  }
  ]
