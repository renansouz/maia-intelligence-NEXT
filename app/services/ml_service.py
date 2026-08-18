""" noted by renansouz
Módulo de Inteligência Artificial e Explicabilidade (XAI).

Este serviço é responsável por:
1. Carregar o modelo Random Forest e o mapeamento de features.
2. Realizar a predição de probabilidade contínua (0-1).
3. Aplicar a calibração de faixas de risco (Baixo < 30%, Médio 30-70%, Alto > 70%).
4. Gerar laudos técnicos via SHAP (Explainable AI), identificando os fatores de maior influência.

Decisão de Design: Utilizamos SHAP para garantir a transparência exigida em processos
de auditoria de seguros, transformando uma 'caixa-preta' em decisões auditáveis.
"""
import joblib
import pandas as pd
import shap
import os
from app.services.processamento_service import calcular_indicadores

class MLService:
    def __init__(self):
        self.modelo_path = 'ml_assets/modelo_risco.pkl'
        self.features_path = 'ml_assets/features.pkl'
        self.modelo = None
        self.features = None
        self.explainer = None
        self._carregar_arquivos()

    def _carregar_arquivos(self):
        if os.path.exists(self.modelo_path):
            self.modelo = joblib.load(self.modelo_path)
            self.features = joblib.load(self.features_path)
            self.explainer = shap.Explainer(self.modelo)

    def _formatar_explicacao_sompo(self, classe, motivos_shap):
        mapeamento_redundancia = {
            'chuva_mm': 'indicador_chuva_alta',
            'umidade_solo': 'indicador_solo_umido',
            'velocidade_kmh': 'indicador_velocidade_alta',
            'proximidade_agua_m': 'indicador_perto_agua',
            'inclinacao_graus': 'indicador_inclinacao_alta',
            'manutencao_dias': 'indicador_manutencao_atrasada'
        }

        nomes_motivos = [m[0] for m in motivos_shap]
        filtrados = []

        for var, importancia in motivos_shap:
            if var in mapeamento_redundancia and mapeamento_redundancia[var] in nomes_motivos:
                continue
            filtrados.append(var.replace('indicador_', '').replace('_', ' '))

        fatores = filtrados[:3]
        
        if not fatores or classe == "BAIXO":
            resumo = "Equipamento em condicoes estaveis de operacao."
            return f"RESUMO: {resumo}"

        resumo = f"Risco {classe} detectado. Principais fatores: {', '.join(fatores)}."
        tecnico = "Analise baseada na correlacao de fatores ambientais e operacionais via SHAP."
        recs = "Verificar protocolos de seguranca para as condicoes citadas."
        
        return f"RESUMO: {resumo} || FATORES: {', '.join(fatores)} || TECNICO: {tecnico} || RECOMENDACOES: {recs}"

    def prever_score(self, dados_telemetria):
        if not self.modelo: return None
        
        inds = calcular_indicadores(dados_telemetria)
        df_input = pd.DataFrame([{**dados_telemetria, **inds}])
        df_input.columns = [col.lower() for col in df_input.columns]
        X = df_input[self.features]
        
        prob = float(self.modelo.predict_proba(X)[:, 1][0])
        
        if prob > 0.70: classe = "ALTO"
        elif prob >= 0.30: classe = "MEDIO"
        else: classe = "BAIXO"
            
        shap_values = self.explainer(X)
        importancias = dict(zip(self.features, shap_values.values[0, :, 1]))
        
        motivos = sorted(importancias.items(), key=lambda x: x[1], reverse=True)
        motivos_ativos = [m for m in motivos[:6] if m[1] > 0.01]
        
        explicacao_formatada = self._formatar_explicacao_sompo(classe, motivos_ativos)

        return {
            "score": round(prob, 4),
            "classificacao": classe,
            "explicacao_completa": explicacao_formatada
        }

ml_service = MLService()