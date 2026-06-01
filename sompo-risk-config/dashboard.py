import oracledb
import pandas as pd
import plotly.express as px
import streamlit as st

st.set_page_config(
    page_title="SompoRisk AI",
    page_icon="🌾",
    layout="wide"
)


@st.cache_data
def carregar_dados():

    conn = oracledb.connect(
        user="RM572772",
        password="030706",
        host="oracle.fiap.com.br",
        port=1521,
        service_name="ORCL"
    )

    query = """
        SELECT *
        FROM TB_RISCO_AGRICOLA
    """

    df = pd.read_sql(query, conn)

    conn.close()

    return df


df = carregar_dados()

df["DATA_MEDICAO"] = pd.to_datetime(df["DATA_MEDICAO"])

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

alto = len(df[df["RISCO"] == "alto"])
medio = len(df[df["RISCO"] == "medio"])
baixo = len(df[df["RISCO"] == "baixo"])

col1, col2, col3, col4 = st.columns(4)

col1.metric("🔴 Risco Alto", alto)
col2.metric("🟡 Risco Médio", medio)
col3.metric("🟢 Risco Baixo", baixo)
col4.metric("📊 Total", len(df))

if alto > 100:
    st.error("🔴 STATUS OPERACIONAL: CRÍTICO")
elif medio > 100:
    st.warning("🟡 STATUS OPERACIONAL: ATENÇÃO")
else:
    st.success("🟢 STATUS OPERACIONAL: NORMAL")

st.subheader("🚨 Alarmes Críticos")

alarmes = df[df["RISCO"] == "alto"]

if not alarmes.empty:

    st.dataframe(
        alarmes[
            [
                "EQUIPAMENTO_ID",
                "CIDADE",
                "DATA_MEDICAO",
                "TEMPERATURA",
                "CHUVA_MM",
                "UMIDADE_SOLO",
                "RISCO"
            ]
        ],
        use_container_width=True
    )

else:
    st.info("Nenhum alarme crítico encontrado para os filtros selecionados.")

st.subheader("📍 Riscos Altos por Cidade")

ranking = (
    df[df["RISCO"] == "alto"]
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
    "São José dos Campos": (-23.2237, -45.9009),
    "Ribeirão Pires": (-23.7107, -46.4138),
    "Taquaritinga": (-21.4061, -48.5047)
}

mapa_df = (
    df[df["RISCO"] == "alto"]
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

st.subheader("⚠️ Top 20 Equipamentos Mais Críticos")

criticos = (
    df[df["RISCO"] == "alto"]
    .sort_values(
        by=[
            "CHUVA_MM",
            "UMIDADE_SOLO"
        ],
        ascending=False
    )
)

if not criticos.empty:

    st.dataframe(
        criticos.head(20),
        use_container_width=True
    )

else:
    st.info("Nenhum equipamento crítico encontrado.")

st.subheader("📈 Estatísticas Gerais")

col1, col2, col3 = st.columns(3)

col1.metric(
    "🌡️ Temperatura Média",
    f"{df['TEMPERATURA'].mean():.1f} °C"
)

col2.metric(
    "🌧️ Chuva Média",
    f"{df['CHUVA_MM'].mean():.1f} mm"
)

col3.metric(
    "💧 Umidade Média",
    f"{df['UMIDADE_SOLO'].mean():.0f}%"
)

st.markdown("---")

st.caption(
    f"Período selecionado: {periodo} | "
    f"Última atualização dos dados: {ultima_data.strftime('%d/%m/%Y')}"
)
