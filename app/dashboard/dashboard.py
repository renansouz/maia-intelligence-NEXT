import streamlit as st
import pandas as pd
import requests
import plotly.express as px
import os
import numpy as np
from dotenv import load_dotenv

load_dotenv()
API_URL = "http://127.0.0.1:8000"
API_KEY = os.getenv("API_KEY")
HEADERS = {"X-API-KEY": API_KEY}

st.set_page_config(page_title="SompoRisk AI", page_icon="🌾", layout="wide")

st.markdown("""
<style>
    .main-header { background: linear-gradient(135deg, #0f2027, #203a43, #2c5364); padding: 1.5rem 2rem; border-radius: 12px; margin-bottom: 1.5rem; color: white; }
    .section-title { font-size:1.1rem; font-weight:700; color:#333; border-bottom:2px solid #e0e0e0; padding-bottom:6px; margin:1.5rem 0 0.8rem; }
    /* Ajuste para evitar que o selectbox sobreponha o conteúdo inferior */
    .stSelectbox { margin-bottom: 2rem; }
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

st.markdown('<div class="main-header"><h1>🌾 SompoRisk AI</h1><p>Monitoramento Preditivo e Auditoria de Frotas</p></div>', unsafe_allow_html=True)

df = carregar_dados_api()

if df.empty:
    st.warning("Aguardando dados do backend...")
else:
    aba_op, aba_gest, aba_ia, aba_dados = st.tabs(["🔴 Operacional", "📊 Gestão", "🧠 Investigação IA", "🛡️ Auditoria"])

    with aba_op:
        alto = len(df[df["CLASSIFICACAO"] == "ALTO"])
        medio = len(df[df["CLASSIFICACAO"] == "MEDIO"])
        c1, c2, c3 = st.columns(3)
        c1.metric("Risco ALTO", alto)
        c2.metric("Risco MÉDIO", medio)
        c3.metric("Equipamentos Auditados", df['EQUIPAMENTO_ID'].nunique())

        st.markdown('<div class="section-title">📍 Mapa de Frota Crítica (Risco Alto)</div>', unsafe_allow_html=True)
        
        # Coordenadas Centrais
        coords_base = {
            "São Paulo": [-23.55, -46.63], "Campinas": [-22.90, -47.06], 
            "Ribeirão Preto": [-21.17, -47.81], "Sorocaba": [-23.50, -47.45], 
            "Piracicaba": [-22.73, -47.64]
        }
        
        df_mapa = df[df["CLASSIFICACAO"] == "ALTO"].copy()
        
        if not df_mapa.empty:
            def aplicar_jitter(cidade, eixo):
                base = coords_base.get(cidade, [-23.5, -46.6])[eixo]
                return base + np.random.uniform(-0.02, 0.02)

            df_mapa['lat'] = df_mapa['CIDADE'].apply(lambda x: aplicar_jitter(x, 0))
            df_mapa['lon'] = df_mapa['CIDADE'].apply(lambda x: aplicar_jitter(x, 1))
            st.map(df_mapa[['lat', 'lon']])
        else:
            st.info("Nenhum equipamento em Risco Alto para exibir no mapa.")

    with aba_gest:
        col1, col2 = st.columns(2)
        with col1:
            fig_pie = px.pie(df, names='CLASSIFICACAO', title="Status da Frota",
                             color='CLASSIFICACAO', color_discrete_map={'ALTO':'#d32f2f','MEDIO':'#f9a825','BAIXO':'#388e3c'})
            st.plotly_chart(fig_pie, use_container_width=True)
        with col2:
            ranking = df.groupby("EQUIPAMENTO_ID")["PROBABILIDADE_ALTO"].mean().sort_values(ascending=False).head(10).reset_index()
            fig_rank = px.bar(ranking, x="PROBABILIDADE_ALTO", y="EQUIPAMENTO_ID", orientation='h', title="Top 10 Equipamentos Mais Críticos")
            st.plotly_chart(fig_rank, use_container_width=True)

        st.markdown('<div class="section-title">📈 Evolução Diária do Risco</div>', unsafe_allow_html=True)
        evolucao = df.groupby("DATA_MEDICAO")["PROBABILIDADE_ALTO"].mean().reset_index()
        st.plotly_chart(px.line(evolucao, x="DATA_MEDICAO", y="PROBABILIDADE_ALTO", labels={"PROBABILIDADE_ALTO": "Média de Risco"}), use_container_width=True)

    with aba_ia:
        st.markdown('<div class="section-title">🔍 Laudo Técnico Digital (XAI)</div>', unsafe_allow_html=True)
        
        eq_id = st.selectbox("Selecione um Equipamento:", sorted(df["EQUIPAMENTO_ID"].unique()))
        
        if st.button("Executar Análise de Risco"):
            with st.spinner("IA processando SHAP e Auditoria..."):
                res = obter_previsao_ia(eq_id)
                
                if res:
                    st.divider() 
                    st.subheader(f"Resultado: Risco {res['classificacao']}")
                    
                    blocos = res['explicacao_completa'].split(" || ")
                    for b in blocos:
                        if "RESUMO" in b: st.info(b.replace("RESUMO:", ""))
                        elif "FATORES" in b: st.warning(b.replace("FATORES:", "⚠️ Fatores Detectados:"))
                        else: st.write(b)
                    
                    st.caption("🛡️ Hash de Integridade (Blockchain style):")
                    st.code(res['hash_auditoria'], language="text")
                else:
                    st.error("Erro ao consultar a API de Previsão.")

    with aba_dados:
        st.markdown('<div class="section-title">📋 Registro de Auditoria (Logs Imutáveis)</div>', unsafe_allow_html=True)
        colunas_visiveis = [
            "EQUIPAMENTO_ID", "CIDADE", "DATA_MEDICAO", "CLASSIFICACAO", 
            "PROBABILIDADE_ALTO", "EXPLICACAO", "HASH_INTEGRIDADE"
        ]
        st.dataframe(df[colunas_visiveis].sort_values("DATA_MEDICAO", ascending=False), use_container_width=True)