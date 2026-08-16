from app.core.database import db
from app.services.ml_service import ml_service
from app.services.audit_service import gerar_hash_integridade

def processar_previsao_completa(dados_telemetria):
    resultado_ml = ml_service.prever_score(dados_telemetria)
    
    eq_id = dados_telemetria.get('equipamento_id')
    dt_med = dados_telemetria.get('data_medicao')
    cidade = dados_telemetria.get('cidade')
    
    conn = db.get_connection()
    cursor = conn.cursor()
    
    try:
        hash_seguranca = gerar_hash_integridade(
            cursor, 
            eq_id, 
            dt_med, 
            resultado_ml['score']
        )
        
        sql = """
            MERGE INTO TB_PREVISAO_RISCO t
            USING (SELECT :eq_id as eq, TO_DATE(:dt_med, 'YYYY-MM-DD') as dt FROM DUAL) s
            ON (t.EQUIPAMENTO_ID = s.eq AND t.DATA_MEDICAO = s.dt)
            WHEN MATCHED THEN
                UPDATE SET 
                    CLASSIFICACAO = :classif, 
                    PROBABILIDADE_ALTO = :score,
                    EXPLICACAO = :exp,
                    HASH_INTEGRIDADE = :h_hash,
                    DATA_PREVISAO = SYSDATE
            WHEN NOT MATCHED THEN
                INSERT (EQUIPAMENTO_ID, CIDADE, DATA_MEDICAO, DATA_PREVISAO, 
                        CLASSIFICACAO, PROBABILIDADE_ALTO, 
                        MODELO_UTILIZADO, EXPLICACAO, HASH_INTEGRIDADE)
                VALUES (:eq_id, :cid, TO_DATE(:dt_med, 'YYYY-MM-DD'), SYSDATE, 
                        :classif, :score, 'RandomForest_SHAP', :exp, :h_hash)
        """
        
        params = {
            "eq_id": eq_id,
            "dt_med": dt_med,
            "classif": resultado_ml['classificacao'],
            "score": resultado_ml['score'],
            "exp": resultado_ml['explicacao_completa'],
            "h_hash": hash_seguranca,
            "cid": cidade
        }
        
        cursor.execute(sql, params)
        conn.commit()
        
        return {
            **resultado_ml,
            "hash_auditoria": hash_seguranca,
            "status": "sucesso"
        }

    except Exception as e:
        conn.rollback()
        raise e 
    finally:
        cursor.close()
        db.release_connection(conn)