# 🛡️ Segurança e Auditoria

A segurança no MAIA é tratada como requisito de negócio, não apenas técnico: uma seguradora precisa poder provar, tecnicamente, que uma decisão automatizada foi tomada com base em dados íntegros, em um momento específico, e que esse registro não foi alterado depois.

## Hash Chain — Integridade das Decisões

Cada previsão gravada em `TB_PREVISAO_RISCO` recebe um hash SHA-256 calculado a partir dos dados da própria previsão **e do hash da previsão anterior**:

```
hash_atual = SHA256(equipamento_id + data_medicao + score + hash_anterior)
```

Essa dependência encadeada — cada hash depende do anterior — é o que torna a cadeia auditável: se um único registro histórico for alterado depois de gravado, o hash daquele registro deixa de corresponder ao conteúdo, e todos os hashes gravados depois dele também deixam de bater, porque foram calculados a partir de um valor que não existe mais. A alteração de um registro antigo é detectável recalculando a cadeia, não porque o sistema "avisa", mas porque a matemática deixa de fechar.

### Concorrência e integridade transacional

Ler o "hash anterior" e gravar o novo registro precisam acontecer como uma operação atômica — caso contrário, duas previsões geradas ao mesmo tempo (por exemplo, dois equipamentos diferentes) poderiam ler o mesmo hash anterior e gerar uma bifurcação na cadeia. Isso é resolvido com lock transacional do Oracle:

```sql
SELECT hash_integridade FROM TB_PREVISAO_RISCO
WHERE ROWID = (
    SELECT rid FROM (
        SELECT ROWID as rid FROM TB_PREVISAO_RISCO
        ORDER BY data_previsao DESC, equipamento_id DESC
    ) WHERE ROWNUM = 1
)
FOR UPDATE
```

O lock via `ROWID` (em vez de `FETCH FIRST ... FOR UPDATE`, que o Oracle não permite combinar) garante que a leitura do último hash e a gravação do novo aconteçam de forma serializada, mantendo a cadeia única e sequencial mesmo sob concorrência.

## Controle de Acesso à API

Todos os endpoints exigem autenticação via header `X-API-KEY`, validado contra a variável de ambiente `API_KEY`.

A validação é **fail-closed**: se a chave não estiver configurada no ambiente (`None`), ou não bater com a enviada, o acesso é recusado com `403 Forbidden`. O sistema nunca assume acesso liberado na ausência de configuração — comportamento inverso (fail-open) já foi identificado e corrigido durante o desenvolvimento, e passou a ser tratado como requisito de teste, não apenas de implementação.

A chave usada pelo frontend fica isolada em `frontend/js/config.js`, arquivo explicitamente excluído do controle de versão — o mesmo padrão aplicado ao `.env` do backend.

## Rastreabilidade de Uso

Um middleware intercepta toda requisição HTTP recebida pela API e registra, em `TB_LOG_ACESSO`: método, rota, status de resposta, IP de origem e tempo de processamento. Essa camada é independente do hash chain — ela responde "quem acessou o quê e quando", enquanto o hash chain responde "esse dado foi alterado depois de gravado?". Juntas, cobrem o requisito de rastreabilidade de entradas, saídas e decisões do sistema.

## Considerações de Conformidade

O desenho do sistema — explicabilidade via SHAP, imutabilidade via hash chain, e rastreabilidade via log de acesso — endereça diretamente os princípios de transparência algorítmica e auditabilidade previstos na LGPD para decisões automatizadas: o titular do dado (ou o órgão regulador) pode obter, para qualquer predição, os fatores que a motivaram e a prova de que o registro não foi alterado após sua geração.
