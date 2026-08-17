# 🛡️ Protocolo de Segurança e Auditoria

A segurança no MAIA é tratada como um requisito de negócio, focada na **Imutabilidade** e no **Controle de Acesso**.

## 🔗 Hash Chain (Cadeia de Integridade)

Implementamos uma estrutura de dados inspirada em Blockchain para selar as decisões da IA.
Cada registro na tabela `TB_PREVISAO_RISCO` contém uma coluna `HASH_INTEGRIDADE`.

**A Matemática por trás:**
`Hash_Atual = SHA256(ID_Equipamento + Data + Score + Hash_Anterior)`

- **Propriedade:** Se um único byte de um registro antigo for alterado, o hash desse registro mudará, quebrando automaticamente todos os hashes subsequentes na cadeia.
- **Concorrência:** Utilizamos o lock transacional do Oracle (`SELECT ... FOR UPDATE` via `ROWID`) para garantir que mesmo com múltiplos equipamentos enviando dados, a cadeia permaneça única e sequencial.

## 🔐 Segurança de API

O acesso aos dados e ao motor de predição é protegido por uma camada de **API Key**.

- **Fail-Closed:** Se a chave não for configurada no ambiente ou for enviada incorretamente, o sistema bloqueia o acesso com `HTTP 403 Forbidden`.
- **Implementação:** Header customizado `X-API-KEY` validado por dependência injetada no FastAPI.

## ⚖️ Conformidade e Direito Digital

O MAIA foi desenhado prevendo os requisitos de **Auditabilidade** exigidos pela SUSEP e pela LGPD (Direito à Explicação):

1.  **Imutabilidade:** Prova matemática de que os logs de risco não foram adulterados.
2.  **Transparência:** Laudo SHAP que explica a lógica por trás da decisão automatizada.
3.  **Rastreabilidade:** Log completo de IPs e tempos de acesso de cada requisição.
