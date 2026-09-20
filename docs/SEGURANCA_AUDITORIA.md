# 🛡️ MAIA — Segurança e Auditoria

Este documento descreve como o MAIA protege o acesso ao sistema e garante que as decisões de risco geradas pelo modelo não possam ser alteradas sem deixar rastro. Para uma seguradora, essas duas coisas — quem pode ver/fazer o quê, e prova de que uma decisão não foi manipulada depois — não são detalhes técnicos, são requisito de confiança do próprio negócio.

---

## 🔐 Autenticação

O acesso ao MAIA é feito por login com email e senha, nunca por uma chave genérica compartilhada. A senha nunca é armazenada em texto puro — passa por **hash bcrypt** antes de ir para o banco, o que significa que mesmo em caso de acesso indevido ao banco de dados, a senha original não é recuperável.

Ao autenticar, o usuário recebe um **token JWT** (JSON Web Token) contendo:

- sua identidade (`id_usuario`);
- seu papel (`SOMPO`, `GESTOR` ou `OPERADOR`);
- tempo de expiração de 24 horas.

Esse token precisa ser enviado em toda chamada subsequente (`Authorization: Bearer <token>`). Passadas as 24 horas, o token deixa de ser aceito automaticamente, e o usuário precisa autenticar novamente — isso limita a janela de risco caso um token seja exposto ou esquecido em algum dispositivo.

---

## 🧑‍🤝‍🧑 Controle de acesso por papel e por vínculo (RBAC)

Ter um papel não é suficiente para acessar qualquer coisa dentro dele — o sistema verifica **duas camadas** em cada requisição:

1. **Papel correto para a ação.** Por exemplo, só a Sompo pode cadastrar uma máquina; só o Gestor pode cadastrar uma propriedade.
2. **Vínculo real com o recurso pedido.** Um Gestor só consegue processar ou visualizar a previsão de risco de uma máquina que esteja em uma propriedade dele; um Operador só acessa a(s) máquina(s) explicitamente vinculada(s) a ele.

Essa segunda camada é o que faz a diferença entre "controle de acesso decorativo" e controle de verdade — foi testada explicitamente durante o desenvolvimento, incluindo o cenário de um usuário tentando acessar um equipamento fora do próprio escopo (resultado: acesso negado, como esperado).

| Papel                    | Escopo de acesso                                                                                                                   |
| ------------------------ | ---------------------------------------------------------------------------------------------------------------------------------- |
| 🏢 Sompo                 | Tudo — todos os gestores, todas as máquinas, exposição financeira consolidada                                                      |
| 👔 Gestor                | Apenas suas propriedades, suas máquinas, seus operadores e os tickets da própria equipe                                            |
| 🧑‍🌾 Operador              | Apenas a(s) máquina(s) vinculada(s) a ele                                                                                          |
| 🔧 Técnico de Manutenção | Nenhum acesso ao sistema — apenas ao formulário de uma manutenção específica, por link com token de uso único e validade de 7 dias |

---

## 🔗 Cadeia de auditoria (Hash Chain)

Cada previsão de risco gerada pelo modelo é registrada com um **hash SHA-256** calculado a partir do conteúdo da própria previsão somado ao hash da previsão imediatamente anterior:

```
hash_atual = SHA256(equipamento + data + score + hash_anterior)
```

Essa dependência entre registros cria uma corrente: se alguém tentasse alterar um registro histórico, o hash daquele ponto em diante deixaria de bater com o valor recalculado — a adulteração se torna detectável, mesmo que o dado tenha sido alterado diretamente no banco.

O sistema conta com um endpoint dedicado de verificação, que percorre toda a cadeia, recalcula cada hash na ordem em que os registros foram criados, e confirma (ou aponta exatamente onde) a integridade se mantém.

> A cadeia não impede fisicamente uma alteração no banco — ela torna essa alteração **detectável e demonstrável**, que é o que importa do ponto de vista de auditoria e disputa de sinistro.

Além do hash em si, cada previsão registra a **explicação legível dos fatores que levaram àquele resultado**, incluindo o contexto de tickets abertos relatados pelo operador — ou seja, a auditoria não guarda só "qual foi a decisão", guarda também "por quê".

---

## 🧾 Rastreabilidade de uso

Toda requisição feita à API — com sucesso ou com falha — é registrada em um log de acesso, contendo método, rota, status de resposta, origem e tempo de processamento. Isso garante visibilidade de uso mesmo em cenários de erro, que são justamente os casos mais importantes de investigar.

## 🚫 Tratamento de erro sem exposição de dado sensível

Qualquer falha interna do sistema é capturada por um tratador central de exceções. O usuário recebe apenas uma mensagem genérica de erro acompanhada de um código de rastreio; o detalhe técnico completo (incluindo qualquer informação de estrutura interna do sistema) fica registrado somente no log do servidor, nunca exposto para fora.

---

## 🔧 Manutenção externa sem comprometer segurança

O técnico de manutenção não precisa de conta no sistema, mas isso não significa acesso livre: o link que ele recebe carrega um **token único, aleatório e de uso único**, com validade de 7 dias. Depois de usado uma vez (ou expirado), o mesmo link deixa de funcionar — impedindo reaproveitamento indevido do formulário.

---

## 📌 Resumo dos princípios aplicados

- Identidade real em vez de chave compartilhada.
- Autorização em duas camadas: papel e vínculo com o recurso.
- Senha nunca armazenada em texto puro.
- Sessão com expiração automática.
- Decisões de risco auditáveis e verificáveis a qualquer momento.
- Erros tratados sem vazamento de informação técnica.
- Acesso externo (técnico) restrito por token temporário de uso único.

Esses princípios, juntos, sustentam o pilar de "arquitetura enterprise com segurança e governança" que orientou o desenvolvimento do MAIA desde o início do desafio.
