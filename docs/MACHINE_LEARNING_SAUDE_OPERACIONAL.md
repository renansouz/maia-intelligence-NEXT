# Machine Learning --- Saúde Operacional das Máquinas

## 1. O que construímos

A ideia principal do nosso Machine Learning é responder:

> **"Essa máquina está operando de forma parecida com o comportamento
> considerado normal para ela?"**

Nosso modelo **não prevê incêndio**, não afirma que uma peça vai quebrar
e o score não é uma "probabilidade de falha".

Ele analisa os dados operacionais recebidos da máquina e mede o quanto o
comportamento atual está aderente ao padrão aprendido.

A arquitetura ficou dividida em duas partes:

``` text
DADOS DA MÁQUINA
     CAN/J1939
         │
         ▼
MODELO OPERACIONAL
Isolation Forest
         │
         ▼
Score Operacional 0–100
         │
         ▼
SCORE CONTEXTUAL
         │
         ├── Manutenção
         ├── Idade
         ├── Ambiente
         └── Feedback do operador
         │
         ▼
SCORE GLOBAL 0–100
```

Portanto, temos:

1.  **Saúde Operacional:** vem principalmente do Machine Learning e dos
    dados CAN.
2.  **Saúde Global/Contextual:** combina o resultado operacional com
    informações externas da máquina.

------------------------------------------------------------------------

## 2. Como testar o que fizemos

Hoje temos dois testes principais:

``` text
scripts/
└── validacao/
    ├── exemplo_maquina_sem_historico.py
    └── exemplo_maquina_com_historico.py
```

### Teste 1 --- Máquina nova, sem histórico

Execute pela raiz do projeto:

``` powershell
python scripts/validacao/exemplo_maquina_sem_historico.py
```

Esse cenário representa uma máquina que acabou de entrar no sistema.

``` text
Máquina entra no sistema
        ↓
Não possui histórico
        ↓
Stage = INITIAL
        ↓
Usa Tümosan como referência inicial
        ↓
Recebe dados CAN
        ↓
Calcula saúde operacional
        ↓
Começa a guardar histórico
```

### Teste 2 --- Máquina com histórico

Execute:

``` powershell
python scripts/validacao/exemplo_maquina_com_historico.py
```

Nesse caso simulamos uma máquina que já acumulou histórico suficiente:

``` text
Tümosan
   ↓
Referência inicial
   ↓
Máquina começa a operar
   ↓
Histórico próprio cresce
   ↓
Dados confiáveis são selecionados
   ↓
Criação de perfil individual
   ↓
Machine Learning passa a conhecer
o comportamento daquela máquina
```

No arquivo de validação usamos histórico sintético para demonstrar a
arquitetura sem precisar esperar meses de telemetria real. Esses dados
não devem ser apresentados como validação real do modelo.

------------------------------------------------------------------------

## 3. Como alterar os dados CAN manualmente

Dentro de:

``` text
scripts/validacao/exemplo_maquina_com_historico.py
```

a leitura atual pode ser definida manualmente assim:

``` python
telemetry_atual = {
    "EngCoolantTemp": 78.0,
    "EngOilTemp1": 90.0,
    "EngOilPress": 300.0,
    "ActualEngine_PercTorque": 65.0,
    "EngineSpeed": 1800.0,
    "EngFuelRate": 12.0,
    "WheelBasedVehicleSpeed": 6.0,
}
```

Esses valores representam a leitura que futuramente chegaria do
ESP32/CAN.

Para simular um comportamento mais distante do padrão:

``` python
telemetry_atual = {
    "EngCoolantTemp": 95.0,
    "EngOilTemp1": 110.0,
    "EngOilPress": 220.0,
    "ActualEngine_PercTorque": 90.0,
    "EngineSpeed": 2300.0,
    "EngFuelRate": 18.0,
    "WheelBasedVehicleSpeed": 9.0,
}
```

Depois basta executar novamente o script e observar o score operacional,
o status, os principais desvios e o score global.

------------------------------------------------------------------------

## 4. Quais informações usamos do CAN

O primeiro modelo trabalha com sete variáveis:

  Variável                    Significado
  --------------------------- -----------------------------------------
  `EngCoolantTemp`            Temperatura do líquido de arrefecimento
  `EngOilTemp1`               Temperatura do óleo
  `EngOilPress`               Pressão do óleo
  `ActualEngine_PercTorque`   Percentual de torque/esforço do motor
  `EngineSpeed`               RPM do motor
  `EngFuelRate`               Taxa de consumo de combustível
  `WheelBasedVehicleSpeed`    Velocidade da máquina

O modelo **não analisa essas variáveis apenas de forma isolada**.

Por exemplo, uma temperatura de 80 °C sozinha diz pouco. O modelo
observa o conjunto:

``` text
Temperatura       80 °C
Óleo              91 °C
Pressão           300
Torque            68%
RPM               1800
Combustível       12
Velocidade        6
```

A pergunta é:

> **"Essa combinação se parece com as combinações que aprendemos como
> comportamento normal?"**

------------------------------------------------------------------------

## 5. De onde veio o conhecimento inicial

Como ainda não possuímos meses de telemetria real de máquinas da Sompo,
utilizamos datasets públicos.

A principal base escolhida para o primeiro modelo foi a do **Tümosan
81.110 Powershuttle**, com dados reais de operação agrícola coletados
via CAN/J1939.

Na EDA também foram estudadas bases Fendt e New Holland, mas com papéis
diferentes.

As bases **não foram simplesmente misturadas linha por linha**, porque
máquinas, sensores, frequências e condições de operação podem ser
diferentes.

O Tümosan funciona como a referência operacional inicial do protótipo.

------------------------------------------------------------------------

## 6. Por que usamos Isolation Forest

Nosso problema possui uma dificuldade importante: não temos uma grande
base rotulada assim:

``` text
linha 1 = máquina saudável
linha 2 = falha de bomba
linha 3 = superaquecimento
linha 4 = falha de motor
```

Sem rótulos reais suficientes, seria incorreto treinar um modelo
supervisionado e afirmar que ele identifica falhas específicas.

Por isso utilizamos **Isolation Forest**, um algoritmo de detecção de
anomalias.

De forma simplificada, ele aprende como os dados normalmente aparecem
juntos.

``` text
Padrão aprendido:
████████████████

Nova combinação muito diferente:
                         █
```

Quando uma nova leitura se afasta do comportamento aprendido, ela recebe
maior indicação de anomalia.

Isso **não significa automaticamente defeito**.

Significa:

> **"Esse comportamento está diferente do padrão aprendido e merece
> atenção."**

------------------------------------------------------------------------

## 7. Por que usamos RobustScaler

Antes do Isolation Forest utilizamos `RobustScaler`.

As variáveis possuem escalas muito diferentes:

``` text
Torque       → 65
RPM          → 1800
Velocidade   → 6
Temperatura  → 78
```

Não queremos que uma variável tenha influência inadequada simplesmente
porque seus valores numéricos são maiores.

O `RobustScaler` transforma as variáveis para uma representação mais
adequada e é menos sensível a valores extremos do que métodos baseados
somente em média e desvio padrão.

------------------------------------------------------------------------

## 8. O que existe dentro do arquivo `.pkl`

O modelo treinado é armazenado em:

``` text
ml_assets/
└── modelo_saude_operacional_tumosan_final.pkl
```

O artefato contém:

``` text
versao
perfil_id
tipo
janela_segundos
variaveis
rotulos
scaler
modelo
referencia_anomaly
perfil_robusto
interpretacao
```

Além do Isolation Forest, guardamos tudo que é necessário para
reproduzir e interpretar a inferência.

Dentro de `perfil_robusto`, cada variável possui:

``` text
mediana
escala_robusta
p05
p25
p75
p95
```

Por exemplo, no perfil Tümosan observado durante o desenvolvimento,
`EngCoolantTemp` possuía referência em torno de:

``` text
mediana = 78 °C
p05     = 76 °C
p95     = 80 °C
```

Esses valores são características do dataset/perfil analisado e **não
devem ser tratados como limites universais para qualquer trator**.

------------------------------------------------------------------------

## 9. Como transformamos a anomalia em Score 0--100

O Isolation Forest não entrega naturalmente algo como:

``` text
Saúde = 83%
```

Ele produz um score próprio de anomalia.

Comparamos esse score com a distribuição de scores da referência usada
para calibrar o modelo.

Conceitualmente:

``` text
Comportamento comum
        ↓
    Score alto

Comportamento incomum
        ↓
    Score baixo
```

Apresentamos o resultado como:

``` text
0 ─────────────────────────────── 100
mais distante               mais aderente
ao padrão                    ao padrão
```

Por isso o resultado deve ser interpretado como **Score de Saúde
Operacional / aderência ao padrão**.

Ele **não é** "83% de chance de a máquina estar saudável" e também não é
probabilidade de falha.

------------------------------------------------------------------------

## 10. Como explicamos os desvios

Além do score multivariado, utilizamos o perfil robusto para ajudar na
explicação.

Comparamos:

``` text
Valor atual
    ↓
Mediana histórica
    ↓
Faixa P05–P95
```

Exemplo:

``` text
Temperatura atual: 95 °C

Referência:
mediana = 78 °C
P05 = 76 °C
P95 = 80 °C

Resultado:
valor acima do padrão aprendido
```

Assim o sistema não retorna apenas:

``` text
Score = 42
```

Ele também consegue mostrar quais sinais estão mais distantes da
referência.

Isso melhora a explicabilidade, mas não autoriza diagnósticos
específicos como:

> "A bomba de óleo está quebrada."

O modelo não possui evidência suficiente para esse tipo de conclusão.

------------------------------------------------------------------------

## 11. Aprendizado progressivo por máquina

O Tümosan é nosso **ponto de partida**, não a referência definitiva de
todas as máquinas.

Não podemos assumir:

``` text
John Deere = Tümosan
Fendt = Tümosan
New Holland = Tümosan
```

Por isso criamos a lógica de perfil progressivo:

``` text
INITIAL
   ↓
ADAPTING
   ↓
INDIVIDUAL
```

### INITIAL

A máquina ainda possui pouco histórico.

``` text
Máquina nova
    ↓
Referência inicial
```

O sistema começa a armazenar as leituras.

### ADAPTING

Já existe histórico próprio relevante.

O sistema pode começar a preparar uma referência da própria unidade,
mantendo a referência original como apoio.

### INDIVIDUAL

Quando existir histórico confiável suficiente:

``` text
Máquina 001
     ↓
Histórico da Máquina 001
     ↓
Treinamento
     ↓
INDIVIDUAL_MAQUINA_001
```

A máquina passa a poder possuir seu próprio perfil operacional.

Os números mínimos de janelas usados atualmente são parâmetros de
engenharia do MVP e não limites cientificamente validados.

------------------------------------------------------------------------

## 12. Por que não treinamos com qualquer leitura

Não podemos permitir que toda leitura recebida vire automaticamente um
exemplo de comportamento saudável.

Imagine:

``` text
Dia 1 → máquina começa a degradar
Dia 2 → degrada mais
Dia 3 → degrada mais
...
Dia 30 → modelo aprende a degradação como "normal"
```

Isso criaria um problema de adaptação indevida.

Por isso existe a ideia de:

``` text
approved_for_baseline
```

Nem toda leitura deve alimentar o futuro perfil individual.

No MVP, o `profile_manager.py` utiliza critérios simplificados para
demonstrar esse mecanismo.

Em uma solução real, a aprovação precisaria considerar critérios mais
fortes, como:

-   qualidade da telemetria;
-   inspeções confirmadas;
-   eventos de manutenção;
-   controle de drift;
-   validação temporal;
-   exclusão de períodos suspeitos;
-   versionamento dos perfis.

------------------------------------------------------------------------

## 13. O que faz cada arquivo

A estrutura principal é:

``` text
machine_learning/
│
├── operational_model.py
├── contextual_model.py
├── profile_manager.py
├── scoring_service.py
│
└── config/
    ├── weights.json
    └── operator_feedback.json
```

### `operational_model.py`

É o coração do Machine Learning operacional.

``` text
carrega .pkl
    ↓
recebe dados CAN
    ↓
RobustScaler
    ↓
Isolation Forest
    ↓
calcula aderência
    ↓
Score 0–100
    ↓
identifica principais desvios
```

### `profile_manager.py`

Gerencia o aprendizado progressivo:

``` text
Máquina
   ↓
Histórico
   ↓
Janelas aprovadas
   ↓
INITIAL / ADAPTING / INDIVIDUAL
   ↓
Perfil próprio
```

Atualmente usamos CSV para simular a persistência que futuramente poderá
ser feita no banco.

### `contextual_model.py`

Nem tudo precisa ser Machine Learning.

Ainda não temos dados reais suficientes para aprender cientificamente
pesos de fatores como manutenção, idade, ambiente e feedback.

Por isso essa segunda camada é atualmente um **motor de regras e pesos
explicável**, e não um modelo supervisionado.

Ela considera fatores como:

``` text
Score operacional
Manutenção
Idade
Temperatura ambiente
Umidade
Feedback do operador
Histórico mecânico classificado, quando disponível
```

e produz o **Score Global da Máquina**.

Os pesos atuais são parâmetros de engenharia do MVP e precisam de
calibração futura.

### `scoring_service.py`

É o orquestrador.

``` text
                 scoring_service
                       │
           ┌───────────┼───────────┐
           ▼           ▼           ▼
     Operational    Profile     Contextual
        Model       Manager       Model
           │           │           │
           ▼           ▼           ▼
        Saúde       Histórico     Contexto
     Operacional    individual    global
           └───────────┼───────────┘
                       ▼
                   RESULTADO
```

A ideia é permitir que futuramente a API envie `machine_id`, telemetria
e contexto e receba um resultado padronizado.

------------------------------------------------------------------------

## 14. Feedback do operador

O sistema também considera informações que podem não aparecer
diretamente no CAN.

Exemplos:

-   ruído anormal;
-   fumaça;
-   perda de potência;
-   superaquecimento percebido;
-   vibração;
-   vazamento;
-   dificuldade de movimento;
-   alerta no painel.

Também existe severidade:

``` text
leve
moderado
severo
```

Uma ocorrência severa pode ter impacto maior que uma observação leve.

Essas categorias ficam configuradas em:

``` text
machine_learning/config/operator_feedback.json
```

------------------------------------------------------------------------

## 15. Onde entra o ESP32

Nos testes atuais definimos `telemetry_atual` manualmente porque não
temos uma máquina agrícola real conectada.

Na arquitetura final:

``` text
MÁQUINA
   ↓
Rede CAN
   ↓
J1939
   ↓
Transceiver CAN
   ↓
ESP32
   ↓
Decodificação PGN/SPN
   ↓
JSON padronizado
   ↓
API
   ↓
Banco
   ↓
Machine Learning
```

Quando alteramos manualmente:

``` python
"EngineSpeed": 1800
```

estamos simulando:

> **"O sistema recebeu uma leitura de 1800 RPM da máquina."**

------------------------------------------------------------------------

## 16. Score Contextual / Global

O resultado operacional responde:

> **"Como a máquina está se comportando em relação ao padrão
> aprendido?"**

Mas queremos considerar também o contexto.

Por isso existe uma segunda camada:

``` text
Score Operacional
       +
Manutenção
       +
Idade
       +
Ambiente
       +
Feedback do operador
       +
Histórico mecânico classificado
       ↓
SCORE GLOBAL
```

É importante não contar duas vezes a mesma informação.

Por exemplo:

-   temperatura do líquido de arrefecimento → modelo operacional;
-   temperatura do óleo → modelo operacional;
-   temperatura ambiente → camada contextual.

Assim evitamos penalizar a mesma informação duas vezes.

------------------------------------------------------------------------

## 17. Exemplo de resultado

Conceitualmente, o sistema pode produzir:

``` text
MÁQUINA: Trator 001

Perfil:
INDIVIDUAL

Saúde Operacional:
82 / 100

Status:
ADERENTE

Principais observações:
- temperatura ligeiramente acima da mediana
- pressão do óleo dentro da faixa
- RPM dentro do comportamento aprendido

Contexto:
Manutenção: 80
Idade: 90
Ambiente: 100
Feedback: ruído leve

Saúde Global:
84 / 100
```

O objetivo é entregar algo mais informativo do que uma simples regra:

``` text
Temperatura > X = problema
```

O sistema observa o comportamento conjunto, o histórico e o contexto.

------------------------------------------------------------------------

## 18. O que já está implementado

No protótipo já temos:

-   EDA dos datasets;
-   seleção das variáveis;
-   `RobustScaler`;
-   `IsolationForest`;
-   artefato `.pkl`;
-   perfil robusto;
-   score operacional;
-   explicação dos desvios;
-   armazenamento de histórico;
-   estados `INITIAL`, `ADAPTING` e `INDIVIDUAL`;
-   treinamento de perfil individual candidato;
-   score contextual/global;
-   feedback do operador;
-   teste de máquina sem histórico;
-   teste de máquina com histórico.

------------------------------------------------------------------------

## 19. O que ainda é evolução do produto

Ainda fazem parte da evolução:

-   ESP32/CAN real integrado ponta a ponta;
-   banco real substituindo CSV nos testes;
-   seleção e promoção automática, validada e versionada do perfil
    individual;
-   meses de histórico real por máquina;
-   validação com inspeções e manutenções reais;
-   calibração dos thresholds;
-   calibração dos pesos contextuais;
-   validação com máquinas reais da Sompo;
-   validação do comportamento entre diferentes modelos e fabricantes.

------------------------------------------------------------------------

## 20. Resumo para apresentação

Se alguém perguntar **"o que o Machine Learning de vocês faz?"**, a
resposta curta é:

> A gente criou um modelo de saúde operacional para máquinas agrícolas.
> Primeiro usamos dados CAN/J1939 reais de um Tümosan como referência
> inicial. Selecionamos sete variáveis, como temperatura, pressão do
> óleo, torque, RPM, consumo e velocidade, e usamos Isolation Forest
> para aprender como essas variáveis normalmente se comportam em
> conjunto. Quando chegam novos dados, o modelo mede o quanto aquele
> comportamento está aderente ao padrão e transforma isso em um score de
> 0 a 100. Ele não diz que a máquina vai quebrar; ele identifica desvios
> do comportamento aprendido. Conforme uma máquina específica acumula
> histórico confiável, o sistema pode criar um perfil individual dela,
> reduzindo a dependência da referência inicial. Depois, combinamos esse
> score operacional com manutenção, idade, ambiente e feedback do
> operador para gerar uma visão global da saúde da máquina.

------------------------------------------------------------------------

## 21. Ideia central do projeto

A lógica completa pode ser resumida em:

``` text
                 PRIMEIRO CONTATO
                       │
                       ▼
             Referência Tümosan
                       │
                       ▼
                  INITIAL
                       │
                 dados chegam
                       │
                       ▼
                  ADAPTING
                       │
             histórico confiável
                       │
                       ▼
                 INDIVIDUAL
                       │
                       ▼
          padrão da própria máquina
                       │
                       ▼
             SAÚDE OPERACIONAL
                       │
                       +
        manutenção / idade / ambiente
          / feedback / histórico
                       │
                       ▼
                SAÚDE GLOBAL
```

O objetivo final é que o sistema evolua de uma **referência inicial de
domínio** para uma análise cada vez mais específica do comportamento de
cada máquina, mantendo explicabilidade e evitando afirmar falhas que os
dados ainda não permitem comprovar.
