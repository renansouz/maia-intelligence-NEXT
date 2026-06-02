# 📚 Documentação Técnica — SompoRisk AI

## Sobre

Esta pasta centraliza toda a documentação técnica e evolutiva do projeto **SompoRisk AI**.

O objetivo é manter histórico técnico, decisões arquiteturais, documentação dos módulos e evolução das funcionalidades ao longo das versões do projeto.

---

# 📂 Estrutura da Documentação

## 🏗 Arquitetura

Documentação da arquitetura geral do sistema:

```txt
docs/arquitetura/
```

Contém:

* definição do problema;
* objetivo da solução;
* escopo do projeto;
* arquitetura macro;
* tecnologias utilizadas;
* integração entre módulos.

---

## 🚜 Projeto

Documentação geral do funcionamento do projeto:

* [Projeto (Documentação)](./project/README-project.md)

```txt
docs/project/
```

Contém:

* visão geral;
* fluxo completo;
* manual de execução;
* regras de negócio;
* integração entre módulos;
* roadmap do projeto.

---

## 📊 Dataset

Documentação da geração e tratamento dos dados:

* [Dataset do Projeto](./dataset/dataset_documentacao.md)

```txt
docs/dataset/
```

Contém:

* origem dos dados;
* integração Open-Meteo;
* geração dos registros;
* indicadores operacionais;
* estrutura do banco;
* estrutura das tabelas;
* preparação dos dados para IA.

---

## ⚙ Backend

Documentação do backend Python:

* [Backend do Projeto](./backend/backend_documentacao.md)

```txt
docs/backend/
```

Contém:

* api_clima.py;
* gerar_dataset.py;
* pre_processamento.py;
* integração Oracle;
* fluxo de execução;
* tratamento de erros;
* persistência dos dados.

---

## 🤖 Machine Learning

Documentação do pipeline de Inteligência Artificial:

* [Machine Learning](./ml/ml_documentacao.md)

```txt
docs/ml/
```

Contém:

* engenharia de features;
* criação da variável alvo;
* preparação dos dados;
* treinamento do modelo;
* árvore de decisão;
* avaliação de métricas;
* persistência do modelo;
* previsão de novos riscos;
* evolução futura do modelo.

---

## 📈 Dashboard

Documentação da futura interface visual:

```txt
docs/dashboard/
```

Contém:

* arquitetura visual;
* indicadores;
* gráficos;
* alertas;
* monitoramento operacional;
* visualização das previsões do modelo.

---

## 🖼 Assets

Arquivos visuais e materiais auxiliares:

```txt
docs/assets/
```

Contém:

* diagramas;
* fluxogramas;
* screenshots;
* imagens;
* apresentações;
* materiais de apoio.

---

# 🔄 Fluxo Geral da Solução

```txt
Open-Meteo API
        ↓
api_clima.py
        ↓
gerar_dataset.py
        ↓
TB_RISCO_AGRICOLA
        ↓
pre_processamento.py
        ↓
TB_RISCO_AGRICOLA_TRATADO
        ↓
preparar_features.py
        ↓
treinar_arvore.py
        ↓
arvore_decisao.pkl
        ↓
prever_risco.py
        ↓
Dashboard
```

---

# 📌 Estado Atual do Projeto

## ✅ Concluído

* arquitetura inicial;
* definição do escopo;
* integração Open-Meteo;
* geração do dataset;
* integração Oracle Database;
* criação de indicadores binários;
* pré-processamento dos dados;
* engenharia de features;
* treinamento da Árvore de Decisão;
* persistência do modelo treinado;
* documentação técnica.

---

## 🔄 Em Desenvolvimento

* integração do modelo ao dashboard;
* visualização das previsões;
* ranking de risco;
* relatórios operacionais;
* monitoramento em tempo real.

---

## 🚀 Próximas Evoluções

### Machine Learning

* validação cruzada;
* ajuste de hiperparâmetros;
* comparação entre modelos;
* utilização de dados reais de sinistros;
* melhoria da variável alvo.

### Banco de Dados

* tabela de previsões;
* histórico de inferências;
* versionamento dos modelos.

### Dashboard

* gráficos interativos;
* indicadores operacionais;
* mapas de risco;
* acompanhamento temporal.

### API

* endpoint de previsão;
* integração externa;
* autenticação.

---

# 🎯 Objetivo Final

Construir uma plataforma inteligente capaz de:

* identificar riscos operacionais;
* prever cenários críticos;
* apoiar decisões preventivas;
* reduzir falhas e perdas operacionais;
* gerar alertas automáticos;
* fornecer análises estratégicas baseadas em dados e Inteligência Artificial.

---

# 📦 Versão Atual

```txt
v2.1.0
```

Principais entregas desta versão:

* Oracle Database integrado;
* Dataset híbrido com Open-Meteo;
* Indicadores binários;
* Pré-processamento estruturado;
* Pipeline de Machine Learning;
* Árvore de Decisão treinável;
* Sistema de previsão de risco;
* Documentação completa.
