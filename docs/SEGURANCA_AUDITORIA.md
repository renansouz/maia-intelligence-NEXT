# 🛡️ MAIA — Segurança e Auditoria

Este documento descreve como o MAIA protege o acesso ao sistema e garante que as decisões de risco geradas pelo modelo não possam ser alteradas sem deixar rastro. Para uma seguradora, essas duas coisas — quem pode ver/fazer o quê, e prova de que uma decisão não foi manipulada depois — não são detalhes técnicos, são requisito de confiança do próprio negócio.

---

## 🔐 Autenticação de Usuários

O acesso ao MAIA aos painéis web é feito por login com email e senha, nunca por uma chave genérica compartilhada. A senha nunca é armazenada em texto puro — passa por **hash bcrypt** antes de ir para o banco, o que significa que mesmo em caso de acesso indevido ao banco de dados, a senha original não é recuperável.

Ao autenticar, o usuário recebe um **token JWT** (JSON Web Token) contendo:
- sua identidade (`id_usuario`);
- seu papel (`SEGURADORA`, `GESTOR` ou `OPERADOR`);
- tempo de expiração de 24 horas.

Esse token precisa ser enviado em toda chamada subsequente (`Authorization: Bearer <token>`). Passadas as 24 horas, o token deixa de ser aceito automaticamente, e o usuário precisa autenticar novamente — o que limita a janela de risco caso um token seja exposto ou esquecido em algum dispositivo.

---

## 📡 Autenticação de Dispositivos (API Key para Ingestão IoT)

Enquanto o acesso humano à plataforma exige credenciais individuais e tokens JWT, a camada de ingestão de telemetria em tempo real (utilizada por sensores ESP32, scripts simuladores ou hardware em campo na rota `POST /telemetria`) opera de forma autônoma utilizando uma chave de dispositivo dedicada enviada via header (`X-API-KEY`). 

Esta separação arquitetural garante que:
- Dispositivos físicos de campo não precisem gerenciar sessões de usuários ou armazenar credenciais sensíveis.
- O vazamento eventual de uma chave de sensor limite-se estritamente à escrita de dados brutos de telemetria (`TB_RISCO_AGRICOLA_TRATADO`), sem conceder privilégios de leitura, gestão de frotas ou administração de contas.

---

## 🧑‍🤝‍🧑 Controle de Acesso por Papel e por Vínculo (RBAC)

Ter um papel corporativo não é suficiente para acessar qualquer recurso dentro dele — o sistema verifica **duas camadas** em cada requisição:

1. **Papel correto para a ação:** Por exemplo, apenas a Seguradora pode cadastrar uma máquina na base global; apenas o Gestor pode cadastrar propriedades ou operadores.
2. **Vínculo real com o recurso pedido:** Um Gestor só consegue processar ou visualizar a previsão de risco de uma máquina que esteja vinculada a uma fazenda sob sua gestão; um Operador só acessa explicitamente a(s) máquina(s) atribuída(s) a ele no campo.

Essa segunda camada diferencia um "controle de acesso decorativo" de um modelo corporativo seguro, tendo sido testada contra tentativas de quebra de escopo horizontal e vertical.

| Papel | Escopo de Acesso |
| :--- | :--- |
| 🏢 **Seguradora** | Visão global — todos os gestores, todas as frotas, exposição financeira consolidada e sinistros. |
| 👔 **Gestor** | Apenas suas propriedades rurais, suas máquinas, seus operadores e os tickets da própria equipe. |
| 🧑‍🌾 **Operador** | Apenas a(s) máquina(s) vinculada(s) a ele no campo. |
| 🔧 **Técnico de Manutenção** | Acesso restrito e sem login — exclusivo ao formulário de uma ordem de serviço específica via link com token único (validade de 7 dias). |

---

## 🔗 Cadeia de auditoria (Hash Chain)

Cada previsão de risco gerada pelo modelo é registrada com um **hash SHA-256** calculado a partir do conteúdo da própria previsão somado ao hash da previsão imediatamente anterior:

```
hash_atual = SHA256(equipamento + data + score + hash_anterior)
```

Essa dependência sequencial cria uma corrente criptográfica: qualquer tentativa de alteração retroativa em um registro histórico rompe a validade matemática de toda a cadeia subsequente, tornando a adulteração detectável de forma imediata.

O sistema conta com um endpoint e rotinas dedicadas de verificação que percorrem a cadeia, recalculam cada hash na ordem de criação e confirmam a integridade sob demanda, o que atende plenamente aos requisitos de regulação e disputa de sinistros.

Além do hash, cada previsão armazena a **explicação descritiva dos fatores de risco** e o contexto de tickets de campo abertos, garantindo a rastreabilidade integral do "porquê" de cada decisão do sistema.

---

## 🧾 Rastreabilidade e Tratamento de Erros

- **Log de Acessos:** Toda requisição HTTP direcionada à API — bem-sucedida ou com falha — é registrada permanentemente no banco Oracle (`TB_LOG_ACESSO`), contendo método, rota, status, IP de origem e tempo de processamento.
- **Tratamento de Exceções Seguro:** Falhas internas inesperadas são capturadas por um tratador global de exceções. O cliente recebe apenas uma resposta genérica acompanhada de um código de rastreio único para depuração, mantendo a estrutura interna do código totalmente oculta de agentes externos.

---

## 📌 Resumo dos Princípios Aplicados

- Identidade real em vez de credenciais genéricas compartilhadas.
- Autorização estrita em duas camadas (Papel + Vínculo de Ativo).
- Isolação de autenticação autônoma para hardware IoT (`X-API-KEY`).
- Senhas protegidas por hash irrecuperável (`bcrypt`).
- Sessões controladas por token com expiração automática (24h).
- Decisões operacionais de risco auditáveis e verificáveis a qualquer momento via Hash Chain.
- Tratamento de exceções sem exposição de engenharia reversa.
- Acesso externo restrito por token temporário de uso único.

Esses princípios consolidados sustentam o pilar de segurança corporativa que orientou o desenvolvimento do MAIA.
