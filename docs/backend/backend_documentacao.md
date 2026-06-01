# ⚙️ Documentação do Backend — SompoRisk AI

## Objetivo

Este documento descreve a camada backend atual do projeto **SompoRisk AI**.

O backend é responsável por:

- coletar dados climáticos históricos reais via API Open-Meteo;
- gerar dados operacionais simulados;
- criar indicadores binários para futura etapa de Machine Learning;
- persistir dados brutos no banco Oracle;
- realizar limpeza e padronização dos dados;
- salvar dados tratados em uma tabela específica para uso no modelo de IA.

Nesta etapa, o backend ainda opera em modo batch, ou seja, com execução manual dos scripts. Porém, a estrutura já foi pensada para evoluir futuramente para automação, API própria e dashboard.

---

# 🏗 Arquitetura backend

Fluxo atual:

```txt
Open-Meteo API
      ↓
api_clima.py
      ↓
gerar_dataset.py
      ↓
Oracle Database
TB_RISCO_AGRICOLA
      ↓
pre_processamento.py
      ↓
Oracle Database
TB_RISCO_AGRICOLA_TRATADO
      ↓
Machine Learning
      ↓
Dashboard
```

---

# 📁 Estrutura

```txt
sompo-risk-config/
│
├── api_clima.py
├── gerar_dataset.py
└── pre_processamento.py
```

---

# 🛠 Stack utilizada

## Linguagem

```txt
Python 3.x
```

## Bibliotecas principais

```txt
requests
pandas
oracledb
python-dotenv
random
datetime
```

---

# 🔐 Variáveis de ambiente

As credenciais do banco Oracle ficam em um arquivo `.env`, que não deve ser enviado para o GitHub.

Exemplo:

```env
ORACLE_USER=seu_usuario
ORACLE_PASSWORD=sua_senha
ORACLE_HOST=oracle.fiap.com.br
ORACLE_PORT=1521
ORACLE_SERVICE=ORCL
```

O arquivo `.env` deve estar listado no `.gitignore`.

---

# 1️⃣ api_clima.py

## Responsabilidade

O arquivo `api_clima.py` é responsável pela comunicação com a API pública **Open-Meteo**.

Ele atua como uma camada de acesso externo, separando a lógica de coleta climática do restante da aplicação.

---

## Funções principais

### buscar_coordenadas(cidade)

Converte o nome da cidade em latitude e longitude.

Entrada:

```python
cidade = "São Paulo"
```

Saída esperada:

```python
{
    "latitude": -23.55,
    "longitude": -46.63
}
```

---

### buscar_clima_historico_intervalo(latitude, longitude)

Busca dados climáticos históricos de uma localidade.

Consulta:

```txt
01/01/2024 até a data atual do sistema
```

Retorno esperado:

```python
[
    {
        "data": "2025-02-11",
        "temperatura": 27.3,
        "chuva_mm": 18.2
    }
]
```

---

## Papel no sistema

Esse módulo funciona como um gateway entre a aplicação e a API externa.

Benefícios:

- facilita manutenção;
- permite trocar a API futuramente;
- melhora a organização do projeto;
- facilita testes e simulações.

---

# 2️⃣ gerar_dataset.py

## Responsabilidade

O arquivo `gerar_dataset.py` constrói o dataset bruto do projeto e insere os dados na tabela Oracle:

```txt
TB_RISCO_AGRICOLA
```

Esse módulo combina:

- dados climáticos reais;
- dados operacionais simulados;
- indicadores binários para Machine Learning;
- persistência em banco Oracle.

---

# Fluxo interno

## 1. Seleção de cidades

Lista atual:

```txt
São Paulo
Campinas
Ribeirão Preto
Sorocaba
Piracicaba
Araraquara
São José dos Campos
Ribeirão Pires
Taquaritinga
```

---

## 2. Busca climática histórica

Para cada cidade, o sistema executa:

```txt
buscar coordenadas
      ↓
buscar histórico climático
      ↓
percorrer registros históricos
      ↓
gerar dados operacionais simulados
      ↓
inserir no Oracle
```

O histórico climático é obtido desde:

```txt
01/01/2024 até a data atual do sistema
```

---

## 3. Dados reais utilizados

Os dados reais vêm da API Open-Meteo:

```txt
data_medicao
temperatura
chuva_mm
```

---

## 4. Dados simulados

Como ainda não há sensores físicos conectados, algumas variáveis são simuladas:

```txt
umidade_solo
velocidade_kmh
proximidade_agua_m
inclinacao_graus
tempo_uso_horas
manutencao_dias
```

Essas variáveis simulam condições operacionais de uma máquina agrícola.

---

## 5. Indicadores binários

Nesta versão, o sistema não gera mais uma classificação final de risco.

Em vez disso, são criados indicadores binários que serão usados futuramente pelo modelo de Machine Learning.

Os indicadores têm valores:

```txt
0 = condição não presente
1 = condição presente
```

Indicadores gerados:

```txt
indicador_chuva_alta
indicador_solo_umido
indicador_velocidade_alta
indicador_perto_agua
indicador_inclinacao_alta
indicador_manutencao_atrasada
```

Exemplos:

```python
indicador_chuva_alta = int(chuva_mm > 30)
indicador_solo_umido = int(umidade_solo > 70)
indicador_velocidade_alta = int(velocidade_kmh > 18)
```

---

## Por que usar indicadores?

Os indicadores ajudam o modelo de Machine Learning a enxergar eventos importantes de forma mais clara.

Eles não definem o risco final. Eles apenas representam sinais que podem influenciar a previsão futura do modelo.

Assim, o ML poderá aprender padrões a partir da combinação entre:

- dados brutos;
- dados climáticos reais;
- dados operacionais simulados;
- indicadores auxiliares.

---

## Saída

Tabela de destino:

```txt
TB_RISCO_AGRICOLA
```

Essa tabela representa os dados brutos do projeto.

---

# 3️⃣ pre_processamento.py

## Responsabilidade

O arquivo `pre_processamento.py` prepara os dados para a etapa de Machine Learning.

Ele lê os dados da tabela bruta:

```txt
TB_RISCO_AGRICOLA
```

aplica limpeza, validação e padronização, e salva o resultado na tabela tratada:

```txt
TB_RISCO_AGRICOLA_TRATADO
```

---

# Etapas do pré-processamento

## 1. Leitura do banco

Entrada:

```txt
TB_RISCO_AGRICOLA
```

---

## 2. Padronização de colunas

As colunas vindas do Oracle são convertidas para letras minúsculas para facilitar o uso no Pandas.

Exemplo:

```txt
TEMPERATURA → temperatura
CHUVA_MM → chuva_mm
```

---

## 3. Limpeza de dados

Remove:

- registros duplicados;
- valores ausentes;
- dados inválidos;
- registros corrompidos.

---

## 4. Padronização textual

Normaliza textos como cidade.

Exemplo:

```txt
são paulo → São Paulo
```

---

## 5. Conversão de datas

Converte a coluna `data_medicao` para formato de data.

```python
pd.to_datetime(df["data_medicao"], errors="coerce")
```

---

## 6. Conversão numérica

Converte colunas numéricas com:

```python
pd.to_numeric()
```

Colunas tratadas:

```txt
temperatura
chuva_mm
umidade_solo
velocidade_kmh
proximidade_agua_m
inclinacao_graus
tempo_uso_horas
manutencao_dias
indicador_chuva_alta
indicador_solo_umido
indicador_velocidade_alta
indicador_perto_agua
indicador_inclinacao_alta
indicador_manutencao_atrasada
```

---

## 7. Regras de sanidade

Remove valores fora da realidade.

Exemplos:

```txt
temperatura entre -10 e 60
chuva entre 0 e 300
umidade_solo entre 0 e 100
velocidade entre 0 e 100
proximidade_agua entre 0 e 5000
inclinação entre 0 e 90
tempo_uso entre 0 e 24
manutenção entre 0 e 365
```

---

## 8. Salvamento no banco

Saída:

```txt
TB_RISCO_AGRICOLA_TRATADO
```

Essa tabela será usada como base para o treinamento do modelo de Machine Learning.

---

# 🗄 Banco de Dados

O projeto utiliza **Oracle Database** como camada de persistência.

## Tabelas principais

### TB_RISCO_AGRICOLA

Tabela bruta.

Armazena os dados gerados pelo `gerar_dataset.py`.

Contém:

- dados climáticos reais;
- dados operacionais simulados;
- indicadores binários.

---

### TB_RISCO_AGRICOLA_TRATADO

Tabela tratada.

Armazena os dados limpos e validados pelo `pre_processamento.py`.

Será usada como base para:

- Machine Learning;
- análises;
- dashboard.

---

# ▶ Execução

## 1. Instalar dependências

```bash
pip install -r requirements.txt
```

---

## 2. Configurar `.env`

Criar o arquivo `.env` na raiz do projeto com as credenciais do Oracle.

---

## 3. Gerar dados brutos

```bash
python sompo-risk-config/gerar_dataset.py
```

---

## 4. Executar pré-processamento

```bash
python sompo-risk-config/pre_processamento.py
```

---

# ⚠ Tratamento de erros

## API indisponível

Possíveis causas:

- sem internet;
- timeout;
- indisponibilidade da Open-Meteo.

Mitigações futuras:

```txt
retry automático
cache persistente
fallback local
```

---

## Erro de conexão Oracle

Possíveis causas:

- credenciais incorretas;
- `.env` ausente;
- host ou service name incorretos;
- indisponibilidade do banco.

Solução:

- conferir variáveis de ambiente;
- verificar conexão com a internet;
- validar usuário e senha.

---

## Tabela inexistente

Erro comum:

```txt
ORA-00942: table or view does not exist
```

Solução:

- criar as tabelas no Oracle;
- verificar se o nome está correto;
- conferir permissões do usuário.

---

## Dados inválidos

Tratamento aplicado:

```txt
drop_duplicates
dropna
pd.to_numeric
pd.to_datetime
filtros de faixa
```

---

# Limitações atuais

Nesta fase:

✅ banco Oracle integrado  
✅ dados climáticos reais  
✅ indicadores binários  
✅ pipeline batch funcional  

Ainda não há:

❌ API REST própria  
❌ autenticação de usuários  
❌ filas de processamento  
❌ execução automática  
❌ logs estruturados  
❌ modelo de Machine Learning treinado  
❌ dashboard final  

---

# Evolução planejada

## Machine Learning

Próxima etapa:

- carregar dados da `TB_RISCO_AGRICOLA_TRATADO`;
- definir variável alvo;
- treinar modelo;
- avaliar métricas;
- prever riscos operacionais.

---

## API própria

Possíveis tecnologias:

```txt
FastAPI
Flask
```

Possíveis rotas futuras:

```txt
POST /prever-risco
GET /equipamentos
GET /dashboard
```

---

## Dashboard

Futuro:

- visualização de indicadores;
- gráficos;
- filtros por cidade;
- análise temporal;
- alertas operacionais.

---

## Tempo real

Futuro:

```txt
ESP32
MQTT
WebSocket
```

---

# Resumo

O backend atual fornece a base operacional do projeto:

✅ integração com Open-Meteo  
✅ geração de dataset climático-operacional  
✅ indicadores binários para IA  
✅ integração com Oracle Database  
✅ pipeline de limpeza e validação  
✅ dados preparados para Machine Learning
