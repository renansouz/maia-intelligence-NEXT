# Dados do EDA no Oracle

O notebook `machine_learning/01_eda_tratores.ipynb` usa arquivos brutos para exploração. A aplicação, porém, deve consultar o Oracle configurado no `.env`. Para isso, o projeto possui uma camada canônica de ML:

- `TB_ML_DATASET`: identifica a fonte e sua frequência;
- `TB_ML_SESSAO`: identifica campo, operação, implemento e arquivo de origem;
- `TB_ML_TELEMETRIA`: armazena os sinais alinhados por significado;
- `VW_ML_TELEMETRIA_ALINHADA`: visão pronta para consultas;
- `VW_ML_RESUMO_SESSAO`: visão resumida para auditoria e dashboards.

As tabelas são separadas de `TB_RISCO_AGRICOLA_TRATADO`, que continua representando a telemetria simplificada usada pela API de risco operacional.

## Configuração

O banco é obtido pelo pool de `app/core/database.py` e usa:

```env
ORACLE_USER=...
ORACLE_PASSWORD=...
ORACLE_HOST=...
ORACLE_PORT=1521
ORACLE_SERVICE=...
```

Os arquivos ainda precisam existir localmente durante a importação. Depois da carga, as consultas não dependem deles. O caminho padrão é `machine_learning/data/raw/`.

## Criar estrutura e importar

Na raiz do projeto, com o ambiente virtual ativado:

```bash
python -m scripts.importar_datasets_eda --dataset tumosan
python -m scripts.importar_datasets_eda --dataset fendt
python -m scripts.importar_datasets_eda --dataset new_holland
```

Para carregar tudo:

```bash
python -m scripts.importar_datasets_eda
```

A carga é idempotente por padrão: sessões já existentes são ignoradas. Para recarregar uma sessão depois de substituir o arquivo:

```bash
python -m scripts.importar_datasets_eda --dataset tumosan --replace
```

O script usa lotes de 10.000 linhas, calcula SHA-256 do arquivo e preserva `DATASET`, `SESSAO`, `ARQUIVO_ORIGEM` e `LINHA_ORIGEM`. Nenhuma tabela da aplicação é apagada.

## Consultas SQL simples

### Quantidade por fonte e sessão

```sql
SELECT dataset, sessao, operacao, implemento, amostras
FROM VW_ML_RESUMO_SESSAO
ORDER BY dataset, sessao;
```

### Temperatura e carga de uma sessão

```sql
SELECT timestamp_origem, temp_coolant_c, temp_oleo_c,
       torque_pct, rpm, combustivel_l_h
FROM VW_ML_TELEMETRIA_ALINHADA
WHERE dataset = 'TUMOSAN'
  AND sessao = 'FIELD_8'
ORDER BY timestamp_origem;
```

### Leituras com temperatura disponível e rotação alta

```sql
SELECT dataset, sessao, timestamp_origem,
       temp_coolant_c, rpm, torque_pct
FROM VW_ML_TELEMETRIA_ALINHADA
WHERE temp_coolant_c IS NOT NULL
  AND rpm >= 1800
ORDER BY temp_coolant_c DESC;
```

### Comparar operações sem misturar sessões

```sql
SELECT dataset, operacao,
       COUNT(*) AS amostras,
       AVG(temp_coolant_c) AS coolant_medio_c,
       MAX(temp_coolant_c) AS coolant_max_c,
       AVG(torque_pct) AS torque_medio_pct,
       AVG(rpm) AS rpm_medio
FROM VW_ML_TELEMETRIA_ALINHADA
WHERE dataset = 'TUMOSAN'
GROUP BY dataset, operacao;
```

### Consultar apenas anomalias sintéticas

```sql
SELECT dataset, sessao, timestamp_origem,
       anomalia_sintetica, temp_admissao_c,
       ventoinha_pct, pressao_oleo_kpa, rpm
FROM VW_ML_TELEMETRIA_ALINHADA
WHERE anomalia_sintetica IS NOT NULL
ORDER BY timestamp_origem;
```

## Regra de interpretação

A coluna `ANOMALIA_SINTETICA` identifica benchmark injetado, não uma falha real. Tümosan e Fendt são dados operacionais reais sem rótulo de incêndio. O banco organiza e entrega as evidências; ele não transforma automaticamente uma temperatura alta em sinistro.
