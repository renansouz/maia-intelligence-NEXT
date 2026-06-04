import oracledb
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
import streamlit as st
import os

from dotenv import load_dotenv

load_dotenv()

st.set_page_config(
    page_title="SompoRisk AI",
    page_icon="🌾",
    layout="wide"
)

# ── CSS customizado ────────────────────────────────────────────────────────────
st.markdown("""
<style>
    /* Cabeçalho principal */
    .main-header {
        background: linear-gradient(135deg, #0f2027, #203a43, #2c5364);
        padding: 1.5rem 2rem;
        border-radius: 12px;
        margin-bottom: 1.5rem;
        color: white;
    }
    .main-header h1 { margin: 0; font-size: 2rem; }
    .main-header p  { margin: 0.2rem 0 0; opacity: 0.75; font-size: 0.9rem; }

    /* Badge de perfil na aba */
    .badge-operacional {
        background:#ff4b4b; color:white;
        padding:2px 10px; border-radius:20px; font-size:0.75rem; font-weight:700;
    }
    .badge-gestao {
        background:#1f77b4; color:white;
        padding:2px 10px; border-radius:20px; font-size:0.75rem; font-weight:700;
    }

    /* Cards de KPI */
    div[data-testid="metric-container"] {
        background: #f8f9fa;
        border: 1px solid #e0e0e0;
        border-radius: 10px;
        padding: 0.8rem 1rem;
    }

    /* Alertas de status */
    .status-critico  { background:#ffe5e5; border-left:4px solid #d32f2f; padding:0.8rem 1rem; border-radius:6px; color:#b71c1c; font-weight:700; }
    .status-atencao  { background:#fff8e1; border-left:4px solid #f9a825; padding:0.8rem 1rem; border-radius:6px; color:#e65100; font-weight:700; }
    .status-normal   { background:#e8f5e9; border-left:4px solid #388e3c; padding:0.8rem 1rem; border-radius:6px; color:#1b5e20; font-weight:700; }

    /* Divisor de seção */
    .section-title {
        font-size:1.1rem; font-weight:700; color:#333;
        border-bottom:2px solid #e0e0e0; padding-bottom:6px; margin:1.5rem 0 0.8rem;
    }
</style>
""", unsafe_allow_html=True)


# ── Carregamento de dados ──────────────────────────────────────────────────────
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
        p.EXPLICACAO,
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
        AND P.DATA_MEDICAO  = T.DATA_MEDICAO
    """

    df = pd.read_sql(query, conn)
    conn.close()
    return df


df_raw = carregar_dados()
df_raw["DATA_MEDICAO"]  = pd.to_datetime(df_raw["DATA_MEDICAO"])
df_raw["DATA_PREVISAO"] = pd.to_datetime(df_raw["DATA_PREVISAO"])

# ── Coordenadas das cidades ────────────────────────────────────────────────────
coordenadas = {
    "São Paulo":          (-23.5505, -46.6333),
    "Campinas":           (-22.9099, -47.0626),
    "Ribeirão Preto":     (-21.1775, -47.8103),
    "Sorocaba":           (-23.5015, -47.4526),
    "Piracicaba":         (-22.7338, -47.6476),
    "Araraquara":         (-21.7944, -48.1756),
    "São José Dos Campos":(-23.2237, -45.9009),
    "Ribeirão Pires":     (-23.7107, -46.4138),
    "Taquaritinga":       (-21.4061, -48.5047),
}

# ── Cabeçalho ─────────────────────────────────────────────────────────────────
st.markdown("""
<div class="main-header">
    <h1>🌾 SompoRisk AI</h1>
    <p>Centro de Monitoramento de Riscos Operacionais e Ambientais</p>
</div>
""", unsafe_allow_html=True)

# ── Sidebar — filtros globais ──────────────────────────────────────────────────
st.sidebar.header("🔍 Filtros Globais")

periodo = st.sidebar.selectbox(
    "Período",
    ["Último dia", "Últimos 7 dias", "Últimos 30 dias", "Todo histórico"],
    index=1
)

ultima_data = df_raw["DATA_MEDICAO"].max()

if periodo == "Último dia":
    df = df_raw[df_raw["DATA_MEDICAO"] == ultima_data].copy()
elif periodo == "Últimos 7 dias":
    df = df_raw[df_raw["DATA_MEDICAO"] >= ultima_data - pd.Timedelta(days=7)].copy()
elif periodo == "Últimos 30 dias":
    df = df_raw[df_raw["DATA_MEDICAO"] >= ultima_data - pd.Timedelta(days=30)].copy()
else:
    df = df_raw.copy()

cidade = st.sidebar.selectbox(
    "Cidade",
    ["Todas"] + sorted(df_raw["CIDADE"].unique().tolist())
)
if cidade != "Todas":
    df = df[df["CIDADE"] == cidade]

st.sidebar.markdown("---")
st.sidebar.caption(
    f"📅 Período: **{periodo}**\n\n"
    f"🕒 Última atualização: **{ultima_data.strftime('%d/%m/%Y')}**"
)

# ── Métricas derivadas ─────────────────────────────────────────────────────────
alto        = len(df[df["CLASSIFICACAO"] == "alto"])
baixo       = len(df[df["CLASSIFICACAO"] == "baixo"])
prob_media  = df["PROBABILIDADE_ALTO"].mean() * 100
umid_solo   = df["UMIDADE_SOLO"].mean()
temp_media  = df["TEMPERATURA"].mean()
total       = len(df)
perc_alto   = (alto / total * 100) if total else 0


# ══════════════════════════════════════════════════════════════════════════════
#  ABAS PRINCIPAIS
# ══════════════════════════════════════════════════════════════════════════════
aba_op, aba_gest = st.tabs([
    "🔴  Visão Operacional  (Operador)",
    "📊  Visão de Gestão  (Gestor)",
])


# ══════════════════════════════════════════════════════════════════════════════
#  ABA 1 — OPERACIONAL
# ══════════════════════════════════════════════════════════════════════════════
with aba_op:

    # Status operacional em destaque
    if prob_media >= 70:
        st.markdown('<div class="status-critico">🔴 STATUS OPERACIONAL: CRÍTICO — Intervenção imediata recomendada</div>', unsafe_allow_html=True)
    elif prob_media >= 40:
        st.markdown('<div class="status-atencao">🟡 STATUS OPERACIONAL: ATENÇÃO — Monitoramento intensificado</div>', unsafe_allow_html=True)
    else:
        st.markdown('<div class="status-normal">🟢 STATUS OPERACIONAL: NORMAL — Sistema dentro dos parâmetros</div>', unsafe_allow_html=True)

    st.markdown("<br>", unsafe_allow_html=True)

    # KPIs operacionais
    c1, c2, c3, c4 = st.columns(4)
    c1.metric("🔴 Equipamentos em Risco Alto", alto)
    c2.metric("🟢 Equipamentos em Risco Baixo", baixo)
    c3.metric("⚠️ % em Risco Alto", f"{perc_alto:.1f}%")
    c4.metric("📦 Total Monitorado", total)

    c5, c6, c7 = st.columns(3)
    c5.metric("💧 Umidade Média do Solo", f"{umid_solo:.1f}%")
    c6.metric("🌡️ Temperatura Média", f"{temp_media:.1f} °C")
    c7.metric("🤖 Prob. Média de Risco Alto", f"{prob_media:.1f}%")

    # ── Top 20 equipamentos críticos ──────────────────────────────────────────
    st.markdown('<div class="section-title">⚠️ Top 20 Equipamentos Mais Críticos</div>', unsafe_allow_html=True)

    criticos = df[df["CLASSIFICACAO"] == "alto"].sort_values("PROBABILIDADE_ALTO", ascending=False)

    if not criticos.empty:
        exib = criticos.copy()
        exib["PROBABILIDADE_ALTO"] = (exib["PROBABILIDADE_ALTO"] * 100).round(2).astype(str) + "%"
        exib["PROBABILIDADE_BAIXO"] = (exib["PROBABILIDADE_BAIXO"] * 100).round(2).astype(str) + "%"
        st.dataframe(
            exib[["EQUIPAMENTO_ID","CIDADE","DATA_MEDICAO","CLASSIFICACAO",
                  "PROBABILIDADE_ALTO","PROBABILIDADE_BAIXO",
                  "TEMPERATURA","CHUVA_MM","UMIDADE_SOLO"]].head(20),
            use_container_width=True
        )
    else:
        st.info("Nenhum equipamento crítico encontrado no período.")

    # ── Alarmes detalhados ────────────────────────────────────────────────────
    st.markdown('<div class="section-title">🚨 Todos os Alarmes Críticos</div>', unsafe_allow_html=True)

    alarmes = df[df["CLASSIFICACAO"] == "alto"].copy()

    if not alarmes.empty:
        alarmes["PROBABILIDADE_ALTO"]  = (alarmes["PROBABILIDADE_ALTO"]  * 100).round(2).astype(str) + "%"
        alarmes["PROBABILIDADE_BAIXO"] = (alarmes["PROBABILIDADE_BAIXO"] * 100).round(2).astype(str) + "%"
        st.dataframe(
            alarmes[["EQUIPAMENTO_ID","CIDADE","DATA_MEDICAO","CLASSIFICACAO",
                     "RISCO_PREVISTO","PROBABILIDADE_ALTO","PROBABILIDADE_BAIXO",
                     "MODELO_UTILIZADO","TEMPO_USO_HORAS","MANUTENCAO_DIAS"]],
            use_container_width=True
        )

        # ── Explicações da IA por equipamento crítico ─────────────────────────
        st.markdown('<div class="section-title">🧠 Explicações da IA — Equipamentos Críticos</div>', unsafe_allow_html=True)
        st.caption("Clique em cada equipamento para ver a análise gerada pelo modelo.")

        alarmes_exp = df[df["CLASSIFICACAO"] == "alto"].sort_values("PROBABILIDADE_ALTO", ascending=False)

        for _, row in alarmes_exp.iterrows():
            label = f"🔴 {row['EQUIPAMENTO_ID']} — {row['CIDADE']} ({row['DATA_MEDICAO'].strftime('%d/%m/%Y')})"
            with st.expander(label):
                explicacao = row.get("EXPLICACAO", "")
                if explicacao:
                    for bloco in explicacao.split(" || "):
                        if bloco.startswith("RESUMO:"):
                            st.markdown(f"**📋 Resumo:** {bloco.replace('RESUMO:', '').strip()}")
                        elif bloco.startswith("FATORES:"):
                            st.markdown("**⚠️ Fatores de Risco:**")
                            for f in bloco.replace("FATORES:", "").strip().split(" | "):
                                st.markdown(f"- {f}")
                        elif bloco.startswith("TECNICO:"):
                            st.markdown("**🔬 Análise Técnica:**")
                            for f in bloco.replace("TECNICO:", "").strip().split(" | "):
                                st.markdown(f"- {f}")
                        elif bloco.startswith("RECOMENDACOES:"):
                            st.markdown("**✅ Recomendações:**")
                            for f in bloco.replace("RECOMENDACOES:", "").strip().split(" | "):
                                st.markdown(f"- {f}")
                else:
                    st.info("Explicação não disponível para este registro.")
    else:
        st.info("Nenhum alarme crítico encontrado.")

    # ── Mapa de riscos ────────────────────────────────────────────────────────
    st.markdown('<div class="section-title">🗺️ Mapa de Riscos — Estado de São Paulo</div>', unsafe_allow_html=True)

    mapa_df = (
        df[df["CLASSIFICACAO"] == "alto"]
        .groupby("CIDADE")
        .size()
        .reset_index(name="TOTAL")
    )

    if not mapa_df.empty:
        mapa_df["lat"] = mapa_df["CIDADE"].map(lambda x: coordenadas.get(x, (None, None))[0])
        mapa_df["lon"] = mapa_df["CIDADE"].map(lambda x: coordenadas.get(x, (None, None))[1])
        mapa_df = mapa_df.dropna(subset=["lat", "lon"])
        st.map(mapa_df[["lat", "lon"]])
    else:
        st.info("Nenhum risco alto encontrado para exibir no mapa.")

    # ── Alarmes por cidade (barras) ───────────────────────────────────────────
    st.markdown('<div class="section-title">📍 Riscos Altos por Cidade</div>', unsafe_allow_html=True)

    ranking = (
        df[df["CLASSIFICACAO"] == "alto"]
        .groupby("CIDADE")
        .size()
        .reset_index(name="TOTAL")
        .sort_values("TOTAL", ascending=False)
    )

    if not ranking.empty:
        fig_bar = px.bar(
            ranking, x="CIDADE", y="TOTAL",
            color="TOTAL",
            color_continuous_scale="Reds",
            title="Quantidade de Alarmes Críticos por Cidade",
            labels={"TOTAL": "Alarmes Críticos", "CIDADE": "Cidade"}
        )
        fig_bar.update_layout(showlegend=False, coloraxis_showscale=False)
        st.plotly_chart(fig_bar, use_container_width=True)
    else:
        st.info("Sem riscos altos para exibir.")


# ══════════════════════════════════════════════════════════════════════════════
#  ABA 2 — GESTÃO
# ══════════════════════════════════════════════════════════════════════════════
with aba_gest:

    st.markdown("##### 📊 Painel Executivo — Visão Consolidada de Riscos")
    st.markdown("<br>", unsafe_allow_html=True)

    # KPIs estratégicos
    g1, g2, g3, g4, g5 = st.columns(5)
    g1.metric("📦 Total de Registros",     total)
    g2.metric("🔴 Eventos de Risco Alto",  alto,  delta=f"{perc_alto:.1f}% do total", delta_color="inverse")
    g3.metric("🟢 Eventos de Risco Baixo", baixo)
    g4.metric("🤖 Score Médio de Risco",   f"{prob_media:.1f}%")
    g5.metric("🌡️ Temperatura Média",      f"{temp_media:.1f} °C")

    st.markdown("---")

    # ── Linha 1: Evolução temporal + Distribuição de classificação ────────────
    col_a, col_b = st.columns([2, 1])

    with col_a:
        st.markdown('<div class="section-title">📈 Evolução Diária do Risco Médio</div>', unsafe_allow_html=True)

        evolucao = (
            df.groupby("DATA_MEDICAO")["PROBABILIDADE_ALTO"]
            .mean()
            .reset_index()
        )
        evolucao["PROBABILIDADE_ALTO"] *= 100

        fig_line = px.line(
            evolucao, x="DATA_MEDICAO", y="PROBABILIDADE_ALTO",
            title="Probabilidade Média de Risco Alto (% ao longo do tempo)",
            labels={"DATA_MEDICAO": "Data", "PROBABILIDADE_ALTO": "Risco Médio (%)"},
            markers=True
        )
        fig_line.add_hline(y=70, line_dash="dash", line_color="red",
                           annotation_text="Nível Crítico (70%)")
        fig_line.add_hline(y=40, line_dash="dash", line_color="orange",
                           annotation_text="Nível de Atenção (40%)")
        st.plotly_chart(fig_line, use_container_width=True)

    with col_b:
        st.markdown('<div class="section-title">🥧 Distribuição de Classificação</div>', unsafe_allow_html=True)

        dist = df["CLASSIFICACAO"].value_counts().reset_index()
        dist.columns = ["Classificação", "Quantidade"]
        fig_pie = px.pie(
            dist, values="Quantidade", names="Classificação",
            color="Classificação",
            color_discrete_map={"alto": "#d32f2f", "baixo": "#388e3c"},
            hole=0.45
        )
        fig_pie.update_traces(textinfo="percent+label")
        st.plotly_chart(fig_pie, use_container_width=True)

    # ── Linha 2: Probabilidade por cidade + Correlação ambiental ──────────────
    col_c, col_d = st.columns(2)

    with col_c:
        st.markdown('<div class="section-title">🎯 Score de Risco Médio por Cidade</div>', unsafe_allow_html=True)

        risco_cidade = (
            df.groupby("CIDADE")["PROBABILIDADE_ALTO"]
            .mean()
            .reset_index()
            .sort_values("PROBABILIDADE_ALTO", ascending=True)
        )
        risco_cidade["PROBABILIDADE_ALTO"] *= 100

        fig_hbar = px.bar(
            risco_cidade, x="PROBABILIDADE_ALTO", y="CIDADE",
            orientation="h",
            color="PROBABILIDADE_ALTO",
            color_continuous_scale="RdYlGn_r",
            title="Probabilidade Média de Risco Alto (%)",
            labels={"PROBABILIDADE_ALTO": "Score de Risco (%)", "CIDADE": ""}
        )
        fig_hbar.update_layout(coloraxis_showscale=False)
        st.plotly_chart(fig_hbar, use_container_width=True)

    with col_d:
        st.markdown('<div class="section-title">🌿 Correlação: Variáveis Ambientais vs Risco</div>', unsafe_allow_html=True)

        variaveis = ["TEMPERATURA","CHUVA_MM","UMIDADE_SOLO",
                     "VELOCIDADE_KMH","INCLINACAO_GRAUS",
                     "TEMPO_USO_HORAS","MANUTENCAO_DIAS"]

        corr = (
            df[variaveis + ["PROBABILIDADE_ALTO"]]
            .corr()["PROBABILIDADE_ALTO"]
            .drop("PROBABILIDADE_ALTO")
            .sort_values()
            .reset_index()
        )
        corr.columns = ["Variável", "Correlação"]

        fig_corr = px.bar(
            corr, x="Correlação", y="Variável",
            orientation="h",
            color="Correlação",
            color_continuous_scale="RdBu",
            range_color=[-1, 1],
            title="Correlação com Probabilidade de Risco Alto"
        )
        st.plotly_chart(fig_corr, use_container_width=True)

    # ── Linha 3: Heatmap temporal por cidade ──────────────────────────────────
    st.markdown('<div class="section-title">🗓️ Heatmap de Risco por Cidade ao Longo do Tempo</div>', unsafe_allow_html=True)

    if "DATA_MEDICAO" in df.columns and df["DATA_MEDICAO"].nunique() > 1:
        df["DATA_STR"] = df["DATA_MEDICAO"].dt.strftime("%d/%m")
        heat_data = (
            df.groupby(["CIDADE", "DATA_STR"])["PROBABILIDADE_ALTO"]
            .mean()
            .reset_index()
        )
        heat_pivot = heat_data.pivot(index="CIDADE", columns="DATA_STR", values="PROBABILIDADE_ALTO")

        fig_heat = px.imshow(
            heat_pivot,
            color_continuous_scale="RdYlGn_r",
            title="Risco Médio por Cidade/Dia (0 = baixo, 1 = alto)",
            labels={"color": "Prob. Risco Alto"}
        )
        st.plotly_chart(fig_heat, use_container_width=True)
    else:
        st.info("Dados insuficientes para gerar o heatmap temporal.")

    # ── Linha 4: Boxplot de risco por cidade ──────────────────────────────────
    st.markdown('<div class="section-title">📦 Dispersão do Score de Risco por Cidade</div>', unsafe_allow_html=True)

    fig_box = px.box(
        df, x="CIDADE", y="PROBABILIDADE_ALTO",
        color="CIDADE",
        title="Distribuição do Score de Risco por Cidade",
        labels={"PROBABILIDADE_ALTO": "Probabilidade de Risco Alto", "CIDADE": ""}
    )
    fig_box.update_layout(showlegend=False)
    st.plotly_chart(fig_box, use_container_width=True)

    # ── Explicações da IA por cidade ─────────────────────────────────────────
    st.markdown('<div class="section-title">🧠 Explicações da IA — Resumo por Cidade</div>', unsafe_allow_html=True)
    st.caption("Baseado no último registro de cada cidade. Clique para expandir.")

    cidades_unicas = df.dropna(subset=["EXPLICACAO"]).groupby("CIDADE").last().reset_index()

    for _, row in cidades_unicas.iterrows():
        classificacao = row["CLASSIFICACAO"]
        icone = "🔴" if classificacao == "alto" else "🟢"
        label = f"{icone} {row['CIDADE']} — {classificacao.upper()} RISCO"
        with st.expander(label):
            explicacao = row.get("EXPLICACAO", "")
            if explicacao:
                for bloco in explicacao.split(" || "):
                    if bloco.startswith("RESUMO:"):
                        st.markdown(f"**📋 Resumo:** {bloco.replace('RESUMO:', '').strip()}")
                    elif bloco.startswith("FATORES:"):
                        st.markdown("**⚠️ Fatores de Risco:**")
                        for f in bloco.replace("FATORES:", "").strip().split(" | "):
                            st.markdown(f"- {f}")
                    elif bloco.startswith("TECNICO:"):
                        st.markdown("**🔬 Análise Técnica:**")
                        for f in bloco.replace("TECNICO:", "").strip().split(" | "):
                            st.markdown(f"- {f}")
                    elif bloco.startswith("RECOMENDACOES:"):
                        st.markdown("**✅ Recomendações:**")
                        for f in bloco.replace("RECOMENDACOES:", "").strip().split(" | "):
                            st.markdown(f"- {f}")
            else:
                st.info("Explicação não disponível.")

    # ── Tabela completa ───────────────────────────────────────────────────────
    st.markdown('<div class="section-title">📋 Base Completa de Equipamentos Monitorados</div>', unsafe_allow_html=True)

    mostrar = st.selectbox("Quantidade de registros", [50, 100, 500, "Todos"], key="gest_qtd")

    todos = df.sort_values("PROBABILIDADE_ALTO", ascending=False).copy()
    if mostrar != "Todos":
        todos = todos.head(mostrar)

    todos["PROBABILIDADE_ALTO"]  = (todos["PROBABILIDADE_ALTO"]  * 100).round(2).astype(str) + "%"
    todos["PROBABILIDADE_BAIXO"] = (todos["PROBABILIDADE_BAIXO"] * 100).round(2).astype(str) + "%"

    st.dataframe(todos, use_container_width=True)

# ── Rodapé ────────────────────────────────────────────────────────────────────
st.markdown("---")
st.caption(
    f"SompoRisk AI  ·  Período: {periodo}  ·  "
    f"Cidade: {cidade}  ·  Última atualização: {ultima_data.strftime('%d/%m/%Y')}"
)
