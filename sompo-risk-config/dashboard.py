import oracledb
import pandas as pd
import plotly.express as px
import streamlit as st
import os

from dotenv import load_dotenv

load_dotenv()

st.set_page_config(
    page_title="SompoRisk AI",
    page_icon="🌾",
    layout="wide"
)


@st.cache_data
def carregar_dados():

    conn = oracledb.connect(
        user=os.getenv("ORACLE_USER"),
        password=os.getenv("ORACLE_PASSWORD"),
        host=os.getenv("ORACLE_HOST", "oracle.fiap.com.br"),
        port=int(os.getenv("ORACLE_PORT", 1521)),
        service_name=os.getenv("ORACLE_SERVICE", "ORCL")
    )

    query = """
    SELECT
    p.EQUIPAMENTO_ID,
    p.CIDADE,
    p.DATA_MEDICAO,
    p.DATA_PREVISAO,
    p.RISCO_PREVISTO,
    p.CLASSIFICACAO,
    p.PROBABILIDADE_BAIXO,
    p.PROBABILIDADE_ALTO,
    p.MODELO_UTILIZADO,

    t.TEMPERATURA,
    t.CHUVA_MM,
    t.UMIDADE_SOLO,
    t.VELOCIDADE_KMH,
    t.PROXIMIDADE_AGUA_M,
    t.INCLINACAO_GRAUS,
    t.TEMPO_USO_HORAS,
    t.MANUTENCAO_DIAS

    FROM TB_PREVISAO_RISCO p

    INNER JOIN TB_RISCO_AGRICOLA_TRATADO t
    ON p.EQUIPAMENTO_ID = t.EQUIPAMENTO_ID
    AND P.DATA_MEDICAO = T.DATA_MEDICAO
    """

    df = pd.read_sql(query, conn)

    conn.close()

    return df


df = carregar_dados()

df["DATA_MEDICAO"] = pd.to_datetime(df["DATA_MEDICAO"])
df["DATA_PREVISAO"] = pd.to_datetime(df["DATA_PREVISAO"])

st.title("🌾 SompoRisk AI")
st.caption("Centro de Monitoramento de Riscos Operacionais e Ambientais")

st.sidebar.header("Filtros")

periodo = st.sidebar.selectbox(
    "Período",
    [
        "Último dia",
        "Últimos 7 dias",
        "Últimos 30 dias",
        "Todo histórico"
    ],
    index=1
)

ultima_data = df["DATA_MEDICAO"].max()

if periodo == "Último dia":

    df = df[
        df["DATA_MEDICAO"] == ultima_data
    ]

elif periodo == "Últimos 7 dias":

    limite = ultima_data - pd.Timedelta(days=7)

    df = df[
        df["DATA_MEDICAO"] >= limite
    ]

elif periodo == "Últimos 30 dias":

    limite = ultima_data - pd.Timedelta(days=30)

    df = df[
        df["DATA_MEDICAO"] >= limite
    ]

cidade = st.sidebar.selectbox(
    "Cidade",
    ["Todas"] + sorted(df["CIDADE"].unique().tolist())
)

if cidade != "Todas":
    df = df[df["CIDADE"] == cidade]

alto = len(df[df["CLASSIFICACAO"] == "alto"])
baixo = len(df[df["CLASSIFICACAO"] == "baixo"])

prob_media = (
    df["PROBABILIDADE_ALTO"].mean() * 100
)

umid_solo = (
    df["UMIDADE_SOLO"].mean()
)

temp = (
    df["TEMPERATURA"].mean()
)

col1, col2, col3, col4, col5, col6 = st.columns(6)

col1.metric("🔴 Risco Alto", alto)
col2.metric("🟢 Risco Baixo", baixo)
col3.metric("🤖 Risco Médio", f"{prob_media:.1f}%")
col4.metric("📊 Total", len(df))
col5.metric("💧 Umidade Média", f"{umid_solo:.1f}%")
col6.metric("🌡️ Temperatura Média", f"{temp:.1f} °C")

if prob_media >= 70:
    st.error("🔴 STATUS OPERACIONAL: CRÍTICO")
elif prob_media >= 40:
    st.warning("🟡 STATUS OPERACIONAL: ATENÇÃO")
else:
    st.success("🟢 STATUS OPERACIONAL: NORMAL")

st.subheader("⚠️ Top 20 Equipamentos Mais Críticos")

criticos = (
    df[df["CLASSIFICACAO"] == "alto"]
    .sort_values(
        by="PROBABILIDADE_ALTO",
        ascending=False
    )
)

if not criticos.empty:

    criticos_exibir = criticos.copy()

    criticos_exibir["PROBABILIDADE_ALTO"] = (
    criticos_exibir["PROBABILIDADE_ALTO"] * 100
    ).round(2).astype(str) + "%"

    criticos_exibir["PROBABILIDADE_BAIXO"] = (
    criticos_exibir["PROBABILIDADE_BAIXO"] * 100
    ).round(2).astype(str) + "%"

    st.dataframe(
    criticos_exibir[
        [
            "EQUIPAMENTO_ID",
            "CIDADE",
            "DATA_MEDICAO",
            "CLASSIFICACAO",
            "PROBABILIDADE_ALTO",
            "PROBABILIDADE_BAIXO"
        ]
    ].head(20),
    use_container_width=True
    )

else:
    st.info("Nenhum equipamento crítico encontrado.")

st.subheader("📍 Riscos Altos por Cidade")

ranking = (
    df[df["CLASSIFICACAO"] == "alto"]
    .groupby("CIDADE")
    .size()
    .reset_index(name="TOTAL")
)

if not ranking.empty:

    fig = px.bar(
        ranking,
        x="CIDADE",
        y="TOTAL",
        title="Quantidade de Alarmes Críticos"
    )

    st.plotly_chart(
        fig,
        use_container_width=True
    )

else:
    st.info("Não há riscos altos para exibir no gráfico.")

st.subheader("🗺️ Mapa de Riscos - Estado de São Paulo")

coordenadas = {
    "São Paulo": (-23.5505, -46.6333),
    "Campinas": (-22.9099, -47.0626),
    "Ribeirão Preto": (-21.1775, -47.8103),
    "Sorocaba": (-23.5015, -47.4526),
    "Piracicaba": (-22.7338, -47.6476),
    "Araraquara": (-21.7944, -48.1756),
    "São José Dos Campos": (-23.2237, -45.9009),
    "Ribeirão Pires": (-23.7107, -46.4138),
    "Taquaritinga": (-21.4061, -48.5047)
}

mapa_df = (
    df[df["CLASSIFICACAO"] == "alto"]
    .groupby("CIDADE")
    .size()
    .reset_index(name="TOTAL")
)

if not mapa_df.empty:

    mapa_df["lat"] = mapa_df["CIDADE"].map(
        lambda x: coordenadas[x][0]
    )

    mapa_df["lon"] = mapa_df["CIDADE"].map(
        lambda x: coordenadas[x][1]
    )

    st.map(
        mapa_df[["lat", "lon"]]
    )

else:
    st.info("Nenhum risco alto encontrado para exibir no mapa.")

st.subheader("🚨 Alarmes Críticos")

alarmes = df[df["CLASSIFICACAO"] == "alto"]

if not alarmes.empty:

    alarmes_exibir = alarmes.copy()

    alarmes_exibir["PROBABILIDADE_ALTO"] = (
        alarmes_exibir["PROBABILIDADE_ALTO"] * 100
    ).round(2).astype(str) + "%"

    alarmes_exibir["PROBABILIDADE_BAIXO"] = (
        alarmes_exibir["PROBABILIDADE_BAIXO"] * 100
    ).round(2).astype(str) + "%"

    st.dataframe(
        alarmes_exibir[
            [
                "EQUIPAMENTO_ID",
                "CIDADE",
                "DATA_MEDICAO",
                "CLASSIFICACAO",
                "RISCO_PREVISTO",
                "PROBABILIDADE_ALTO",
                "PROBABILIDADE_BAIXO",
                "MODELO_UTILIZADO"
            ]
        ],
        use_container_width=True
    )

else:
    st.info("Nenhum alarme crítico encontrado.")
    

st.subheader("🎯 Probabilidade Média de Risco por Cidade")

risco_cidade = (
    df.groupby("CIDADE")["PROBABILIDADE_ALTO"]
    .mean()
    .reset_index()
)

fig = px.bar(
    risco_cidade,
    x="CIDADE",
    y="PROBABILIDADE_ALTO",
    title="Probabilidade Média de Risco"
)

st.plotly_chart(
    fig,
    use_container_width=True
)


st.subheader("📋 Todos os Equipamentos Monitorados")

mostrar = st.selectbox(
    "Quantidade de registros",
    [50, 100, 500, "Todos"]
)

todos_equipamentos = (
    df.sort_values(
        by="PROBABILIDADE_ALTO",
        ascending=False
    )
)

if mostrar != "Todos":
    todos_equipamentos = todos_equipamentos.head(mostrar)

todos_exibir = todos_equipamentos.copy()

todos_exibir["PROBABILIDADE_ALTO"] = (
    todos_exibir["PROBABILIDADE_ALTO"] * 100
).round(2).astype(str) + "%"

todos_exibir["PROBABILIDADE_BAIXO"] = (
    todos_exibir["PROBABILIDADE_BAIXO"] * 100
).round(2).astype(str) + "%"

st.dataframe(
    todos_exibir,
    use_container_width=True
)
st.markdown("---")

st.caption(
    f"Período selecionado: {periodo} | "
    f"Última atualização: {ultima_data.strftime('%d/%m/%Y')}"
)
