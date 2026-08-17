import streamlit as st
import pandas as pd
import requests
import plotly.express as px
import os
import numpy as np
from PIL import Image
from dotenv import load_dotenv

load_dotenv()
API_URL = "http://127.0.0.1:8000"
API_KEY = os.getenv("API_KEY")
HEADERS = {"X-API-KEY": API_KEY}

LOGO_PATH = os.path.join(os.path.dirname(__file__), "assets", "sompo-logo.webp")

page_icon = "🔴"
if os.path.exists(LOGO_PATH):
    page_icon = Image.open(LOGO_PATH)

st.set_page_config(page_title="MAIA | Sompo Seguros", page_icon=page_icon, layout="wide")

st.markdown(f"""
<style>
    .main-header {{
        background-color: #DF082A;
        padding: 1.5rem 2rem;
        border-radius: 8px;
        margin-top: -3rem;
        margin-bottom: 2rem;
        color: white;
        display: flex;
        align-items: center;
        justify-content: space-between;
    }}
    .header-text h1 {{ margin: 0; font-size: 2.2rem; font-weight: 800; color: white; }}
    .header-text p {{ margin: 0; opacity: 0.9; font-size: 1rem; color: white; }}
    .section-title {{
        color: #101828;
        font-size: 1.1rem;
        font-weight: 700;
        border-left: 4px solid #DF082A;
        padding-left: 12px;
        margin: 1.5rem 0 1rem;
    }}
    /* Forçar tabelas Streamlit a ocuparem largura total */
    .stDataFrame {{ width: 100%; }}
</style>
""", unsafe_allow_html=True)

@st.cache_data(ttl=60)
def carregar_dados_api():
    try:
        res = requests.get(f"{API_URL}/historico", headers=HEADERS)
        if res.status_code == 200:
            df = pd.DataFrame(res.json())
            if not df.empty:
                df['DATA_MEDICAO'] = pd.to_datetime(df['DATA_MEDICAO'])
                df['DATA_PREVISAO'] = pd.to_datetime(df['DATA_PREVISAO'])
            return df
    except: return pd.DataFrame()
    return pd.DataFrame()

def obter_previsao_ia(eq_id):
    try:
        res = requests.get(f"{API_URL}/previsao/{eq_id}", headers=HEADERS)
        return res.json() if res.status_code == 200 else None
    except: return None

with st.container():
    st.markdown(f'''
    <div class="main-header">
        <div class="header-text">
            <h1>MAIA</h1>
            <p>Monitoramento e Análise Inteligente Agrícola · Sompo Seguros</p>
        </div>
    </div>
    ''', unsafe_allow_html=True)

df = carregar_dados_api()

if df.empty:
    st.warning("Conectando ao ecossistema MAIA... Verifique se o backend está ativo.")
else:
    aba_op, aba_gest, aba_ia, aba_audit = st.tabs([
        "📊 Operacional", "📈 Gestão", "🧠 Diagnóstico XAI", "🛡️ Compliance"
    ])

    with aba_op:
        alto = len(df[df["CLASSIFICACAO"] == "ALTO"])
        medio = len(df[df["CLASSIFICACAO"] == "MEDIO"])
        c1, c2, c3 = st.columns(3)
        c1.metric("Risco Crítico (ALTO)", alto, delta_color="inverse")
        c2.metric("Atenção (MÉDIO)", medio)
        c3.metric("Frota Ativa", df['EQUIPAMENTO_ID'].nunique())

        st.markdown('<div class="section-title">Mapa de Calor da Frota (Incidentes ALTO)</div>', unsafe_allow_html=True)
        
        coords_base = {"São Paulo": [-23.55, -46.63], "Campinas": [-22.90, -47.06], "Ribeirão Preto": [-21.17, -47.81], "Sorocaba": [-23.50, -47.45], "Piracicaba": [-22.73, -47.64]}
        df_mapa = df[df["CLASSIFICACAO"] == "ALTO"].copy()
        
        if not df_mapa.empty:
            np.random.seed(42) 
            df_mapa['lat'] = df_mapa['CIDADE'].apply(lambda x: coords_base.get(x, [-23.5, -46.6])[0] + np.random.uniform(-0.015, 0.015))
            df_mapa['lon'] = df_mapa['CIDADE'].apply(lambda x: coords_base.get(x, [-23.5, -46.6])[1] + np.random.uniform(-0.015, 0.015))
            st.map(df_mapa[['lat', 'lon']], color="#DF082A", zoom=6)

    with aba_gest:
        col1, col2 = st.columns(2)
        with col1:
            fig_pie = px.pie(df, names='CLASSIFICACAO', title="Status Geral da Frota",
                             color='CLASSIFICACAO', 
                             color_discrete_map={'ALTO':'#D92D20','MEDIO':'#FDB022','BAIXO':'#12B76A'},
                             template="plotly_white") 
            st.plotly_chart(fig_pie, use_container_width=True)
        with col2:
            ranking = df.groupby("EQUIPAMENTO_ID")["PROBABILIDADE_ALTO"].mean().sort_values(ascending=False).head(10).reset_index()
            fig_rank = px.bar(ranking, x="PROBABILIDADE_ALTO", y="EQUIPAMENTO_ID", orientation='h', 
                              title="Ranking: Score de Risco Médio", template="plotly_white",
                              color_discrete_sequence=['#9E1E24'])
            st.plotly_chart(fig_rank, use_container_width=True)

        st.markdown('<div class="section-title">Evolução Temporal do Risco</div>', unsafe_allow_html=True)
        evolucao = df.groupby("DATA_MEDICAO")["PROBABILIDADE_ALTO"].mean().reset_index()
        fig_evol = px.line(evolucao, x="DATA_MEDICAO", y="PROBABILIDADE_ALTO", 
                           color_discrete_sequence=['#DF082A'], template="plotly_white")
        st.plotly_chart(fig_evol, use_container_width=True)

    with aba_ia:
        st.markdown('<div class="section-title">Diagnóstico Individual XAI</div>', unsafe_allow_html=True)
        eq_id = st.selectbox("Selecione o Equipamento:", sorted(df["EQUIPAMENTO_ID"].unique()), key="sel_ia")
        
        if st.button("GERAR LAUDO TÉCNICO"):
            res = obter_previsao_ia(eq_id)
            if res:
                st.divider()
                color = "#D92D20" if res['classificacao'] == "ALTO" else "#FDB022" if res['classificacao'] == "MEDIO" else "#12B76A"
                st.markdown(f"### Status Atual: <span style='color:{color}'>{res['classificacao']}</span>", unsafe_allow_html=True)
                
                for b in res['explicacao_completa'].split(" || "):
                    if "RESUMO" in b: st.info(b.replace("RESUMO:", ""))
                    elif "FATORES" in b: st.warning(b.replace("FATORES:", "⚠️ Fatores Detectados (SHAP):"))
                    else: st.markdown(f"*{b}*")
                
                st.caption("Autenticação de Auditoria:")
                st.code(res['hash_auditoria'], language="text")

    with aba_audit:
        st.markdown('<div class="section-title">Registro de Auditoria e Conformidade</div>', unsafe_allow_html=True)
        colunas_visiveis = ["DATA_PREVISAO", "EQUIPAMENTO_ID", "CIDADE", "CLASSIFICACAO", "PROBABILIDADE_ALTO", "HASH_INTEGRIDADE"]
        st.dataframe(df[colunas_visiveis].sort_values("DATA_PREVISAO", ascending=False), use_container_width=True)