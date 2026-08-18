# 🛡️ Segurança e Auditoria

No MAIA, segurança e rastreabilidade fazem parte da própria arquitetura da solução.

Como o sistema produz decisões automatizadas de risco, é importante preservar três propriedades:

- **controle de acesso** aos serviços;
- **rastreabilidade** das interações com a API;
- **integridade histórica** das previsões armazenadas.

## 🔗 Hash Chain — Integridade das Decisões

Cada previsão registrada em `TB_PREVISAO_RISCO` recebe um hash SHA-256 calculado a partir dos dados da própria previsão e do hash da previsão anterior:

```text
hash_atual = SHA256(equipamento_id + data_medicao + score + hash_anterior)
```

A dependência entre registros cria uma **cadeia verificável de integridade**.

Se um registro histórico for alterado depois de gravado, o hash calculado a partir daquele conteúdo deixa de corresponder ao valor armazenado. Como os registros seguintes dependem do hash anterior, a alteração também rompe a sequência subsequente.

A integridade pode, portanto, ser verificada recalculando a cadeia e comparando os valores armazenados.

> O mecanismo não impede fisicamente uma alteração no banco. Ele torna a adulteração histórica **detectável pela quebra do encadeamento criptográfico**.

### Concorrência e integridade transacional

A leitura do hash anterior e a gravação da nova previsão precisam ocorrer de forma serializada. Caso duas previsões sejam processadas simultaneamente, ambas poderiam tentar utilizar o mesmo hash anterior e gerar uma bifurcação na cadeia.

Para evitar esse cenário, o MAIA utiliza um **lock transacional do Oracle**:

```sql
SELECT hash_integridade FROM TB_PREVISAO_RISCO
WHERE ROWID = (
    SELECT rid FROM (
        SELECT ROWID as rid
        FROM TB_PREVISAO_RISCO
        ORDER BY data_previsao DESC, equipamento_id DESC
    ) WHERE ROWNUM = 1
)
FOR UPDATE
```

O `ROWID` é utilizado para viabilizar o bloqueio da linha correspondente ao último registro.

Assim, a leitura do hash anterior e a gravação do novo elo permanecem serializadas dentro da transação, preservando a sequência da cadeia mesmo quando previsões são processadas concorrentemente.

---

## 🔐 Controle de Acesso à API

Os endpoints protegidos utilizam autenticação por meio do header:

```text
X-API-KEY
```

A chave é comparada com a variável de ambiente `API_KEY`.

A validação segue o princípio **fail-closed**:

- chave ausente no ambiente → acesso negado;
- chave enviada incorretamente → acesso negado;
- chave válida → requisição processada.

O endpoint de saúde `/health` permanece disponível sem autenticação para permitir verificações básicas de disponibilidade da aplicação.

### Configuração de credenciais

As credenciais sensíveis do backend são mantidas em variáveis de ambiente e não são versionadas no Git.

O Oracle é acessado somente pelo backend, e o frontend não possui acesso direto ao banco de dados.

A configuração utilizada pelo frontend para autenticação da API também permanece fora do controle de versão.

> A chave utilizada pelo frontend deve ser tratada como credencial de acesso à API, e não como um segredo criptográfico, pois valores enviados ao navegador podem ser observados pelo cliente.

---

## 📋 Rastreabilidade de Uso

Um middleware intercepta as requisições HTTP recebidas pela API e registra em `TB_LOG_ACESSO`:

- método HTTP;
- rota;
- status da resposta;
- IP de origem;
- tempo de processamento.

Essa camada registra **o uso da aplicação**.

Ela é independente da Hash Chain:

| Mecanismo             | O que responde                                       |
| --------------------- | ---------------------------------------------------- |
| **Middleware de Log** | Quem acessou o sistema, qual rota e quando           |
| **Hash Chain**        | Se o conteúdo encadeado de uma previsão foi alterado |

As duas camadas trabalham de forma complementar para ampliar a rastreabilidade do sistema.

---

## 🧩 Segurança por Camadas

A arquitetura de segurança do MAIA combina diferentes mecanismos:

```text
Requisição
    ↓
API Key
    ↓
Validação da entrada
    ↓
Processamento
    ↓
Persistência Oracle
    ↓
Log de acesso
    ↓
Hash Chain da decisão
```

Cada mecanismo cobre uma necessidade diferente:

- **API Key:** controle de acesso;
- **Pydantic:** validação estrutural das entradas;
- **Oracle:** persistência e controle transacional;
- **Middleware:** rastreabilidade de uso;
- **SHA-256 + Hash Chain:** integridade histórica das previsões.

---

## 📌 Considerações de Auditabilidade

A combinação de **SHAP**, **logs de acesso** e **Hash Chain** foi projetada para tornar as decisões do MAIA mais transparentes e rastreáveis.

Para uma previsão armazenada, o sistema consegue associar:

```text
Equipamento
+ Dados utilizados
+ Score
+ Explicação
+ Momento da previsão
+ Hash de integridade
```

Isso permite reconstruir o contexto da decisão e verificar a integridade do encadeamento histórico.

Esses mecanismos **contribuem para requisitos de auditabilidade e transparência**, mas não substituem controles jurídicos, governança de dados, gestão de acessos ou políticas de conformidade que seriam necessários em um ambiente produtivo real.

---

## 🎯 Segurança como Parte do Produto

No MAIA, segurança não existe apenas para proteger a API.

Ela sustenta uma característica importante da solução:

> **uma decisão de risco precisa ser compreensível, rastreável e verificável.**

Por isso, a arquitetura combina **controle de acesso + rastreabilidade + explicabilidade + integridade histórica** em torno do mesmo fluxo de decisão.
