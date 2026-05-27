# 📚 Documentação Técnica — SompoRisk AI

## Sobre

Esta pasta centraliza toda a documentação técnica e evolutiva do projeto **SompoRisk AI**.

O objetivo é manter histórico técnico, decisões arquiteturais e explicações detalhadas sobre cada módulo.

---

# Estrutura da documentação

## Arquitetura

Documentação da arquitetura geral do sistema:

```txt
docs/arquitetura/
```

Contém:

- definição do problema;
- escopo;
- arquitetura macro;
- tecnologias;

---

## Dataset

Documentação sobre geração e tratamento de dados:

- [Dataset do projeto (Documentação)](./docs/dataset/dataset_documentacao.md)

```txt
docs/dataset/
```

Contém:

- origem dos dados;
- API Open-Meteo;
- dataset híbrido;
- regras de classificação inicial;
- estrutura do CSV.

---

## Backend

Documentação do backend Python:

- [Backend do projeto (Documentação)](./docs/backend/backend_documentacao.md)

```txt
docs/backend/
```

Contém:

- api_clima.py
- gerar_dataset.py
- pre_processamento.py
- fluxo de execução
- tratamento de erros

---

## Machine Learning

Documentação do pipeline de IA:

```txt
docs/machine-learning/
```

Contém:

- preparação dos dados;
- split treino/teste;
- encoding;
- normalização;
- modelos;
- métricas;
- resultados.

---

## Dashboard

Documentação da interface visual:

```txt
docs/dashboard/
```

Contém:

- arquitetura visual;
- dashboards;
- indicadores;
- gráficos;
- alertas.

---

## Assets

Arquivos visuais:

```txt
docs/assets/
```

Contém:

- diagramas;
- prints;
- screenshots;
- imagens auxiliares.

---

# Estado atual

## Concluído

✅ arquitetura inicial  
✅ dataset híbrido  
✅ integração Open-Meteo  
✅ geração de dataset  
✅ pré-processamento  

---

## Em andamento

🔄 Machine Learning  
🔄 Dashboard  

---

# Objetivo final

Construir uma plataforma inteligente para previsão de riscos agrícolas com:

- IA;
- dados reais;
- score de risco;
- alertas preventivos;
- dashboard visual.
