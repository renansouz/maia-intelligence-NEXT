import json
import os
from pathlib import Path
from typing import Any, Dict, Optional
import pandas as pd
import numpy as np

from app.core.database import db
from machine_learning import EnvironmentalPCAModel

# Configura o path para importar o EnvironmentalPCAModel criado pelo Kevin
BASE_DIR = Path(__file__).resolve().parents[2]
import sys
ML_DIR = BASE_DIR / "machine_learning"
if str(ML_DIR) not in sys.path:
    sys.path.insert(0, str(ML_DIR))

try:
    from machine_learning import EnvironmentalPCAModel  # type: ignore
except ImportError:
    EnvironmentalPCAModel = None

class EnvironmentalService:
    def __init__(self):
        self.model_class = EnvironmentalPCAModel

    def avaliar_condicao_ambiental(self, latitude: Optional[float], longitude: Optional[float]) -> Dict[str, Any]:
        """
        Consulta o histórico de 2 meses na TB_ML_AMBIENTAL para a coordenada,
        ajusta o PCA dinamicamente com o histórico e prediz a condição mais recente.
        """
        fallback_padrao = {
            "score_ambiental": 85.0,
            "indice_atipicidade_pct": 15.0,
            "faixa_condicao": "proxima_do_padrao",
            "pca_distance": 0.42
        }

        if not self.model_class:
            return fallback_padrao

        lat = latitude if latitude is not None else -21.1775
        lon = longitude if longitude is not None else -47.8103

        conn = db.get_connection()
        cursor = conn.cursor()
        try:
            # Busca o histórico dos últimos 2 meses (60 dias) para a região
            cursor.execute("""
                SELECT DATA_OBSERVACAO, LATITUDE, LONGITUDE, FEATURES_JSON
                FROM TB_ML_AMBIENTAL
                WHERE LATITUDE BETWEEN (:lat - 0.2) AND (:lat + 0.2)
                  AND LONGITUDE BETWEEN (:lon - 0.2) AND (:lon + 0.2)
                  AND DATA_OBSERVACAO >= SYSDATE - 60
                ORDER BY DATA_OBSERVACAO ASC
            """, lat=lat, lon=lon)
            
            rows = cursor.fetchall()
            
            # Fallback global caso a coordenada específica não tenha 3+ pontos na janela
            if len(rows) < 3:
                cursor.execute("""
                    SELECT DATA_OBSERVACAO, LATITUDE, LONGITUDE, FEATURES_JSON
                    FROM TB_ML_AMBIENTAL
                    ORDER BY DATA_OBSERVACAO ASC
                    FETCH FIRST 30 ROWS ONLY
                """)
                rows = cursor.fetchall()

            if len(rows) < 3:
                return fallback_padrao

            registros = []
            for data_obs, r_lat, r_lon, features_json in rows:
                if hasattr(features_json, "read"):
                    features_json = features_json.read()
                
                dados = json.loads(features_json)
                dados["date"] = pd.to_datetime(data_obs)
                dados["latitude"] = r_lat
                dados["longitude"] = r_lon
                registros.append(dados)

            df_historico = pd.DataFrame(registros)

            if len(df_historico) < 3:
                return fallback_padrao

            # Separa o histórico de treino e a observação mais recente para teste
            observacao_atual = df_historico.iloc[-1].to_dict()
            historico = df_historico.iloc[:-1].copy()

            if len(historico) < 2:
                return fallback_padrao

            # Instancia e ajusta o PCA dinamicamente com o histórico recuperado
            modelo = self.model_class(explained_variance_target=0.90, min_components=2)
            modelo.fit(historico)
            
            resultado = modelo.predict_one(observacao_atual)

            return {
                "score_ambiental": round(float(resultado.get("score_condicao_ambiental", 85.0)), 2),
                "indice_atipicidade_pct": round(float(resultado.get("indice_atipicidade_pct", 15.0)), 2),
                "faixa_condicao": str(resultado.get("faixa_condicao", "proxima_do_padrao")),
                "pca_distance": round(float(resultado.get("pca_distance", 0.42)), 4)
            }

        except Exception as e:
            print(f"[ERRO] Falha ao processar PCA ambiental dinâmico: {e}")
            return fallback_padrao
        finally:
            cursor.close()
            db.release_connection(conn)

environmental_service = EnvironmentalService()