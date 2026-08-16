from app.core.database import db
import oracledb

def salvar_telemetria_db(dados_dict):
    """
    insere ou atualiza telemetria na tabela tratado via MERGE
    """
    conn = db.get_connection()
    cursor = conn.cursor()
    
    # extraindo e convertendo a data para string iso
    dt_str = dados_dict['data_medicao'].isoformat()
    
    sql = """
    MERGE INTO TB_RISCO_AGRICOLA_TRATADO t
    USING (SELECT :eq_id as eq, TO_DATE(:dt_med, 'YYYY-MM-DD') as dt FROM DUAL) s
    ON (t.EQUIPAMENTO_ID = s.eq AND t.DATA_MEDICAO = s.dt)
    WHEN MATCHED THEN
        UPDATE SET TEMPERATURA = :temp, CHUVA_MM = :chuva, UMIDADE_SOLO = :umid
    WHEN NOT MATCHED THEN
        INSERT (EQUIPAMENTO_ID, CIDADE, DATA_MEDICAO, TEMPERATURA, CHUVA_MM, 
                UMIDADE_SOLO, VELOCIDADE_KMH, PROXIMIDADE_AGUA_M, INCLINACAO_GRAUS, 
                TEMPO_USO_HORAS, MANUTENCAO_DIAS)
        VALUES (:eq_id, :cid, TO_DATE(:dt_med, 'YYYY-MM-DD'), :temp, :chuva, 
                :umid, :vel, :prox, :incl, :t_uso, :manut)
    """
    
    params = {
        "eq_id": dados_dict['equipamento_id'],
        "dt_med": dt_str,
        "temp": dados_dict['temperatura'],
        "chuva": dados_dict['chuva_mm'],
        "umid": dados_dict['umidade_solo'],
        "cid": dados_dict['cidade'],
        "vel": dados_dict['velocidade_kmh'],
        "prox": dados_dict['proximidade_agua_m'],
        "incl": dados_dict['inclinacao_graus'],
        "t_uso": dados_dict['tempo_uso_horas'],
        "manut": dados_dict['manutencao_dias']
    }
    
    try:
        cursor.execute(sql, params)
        conn.commit()
        return True
    except Exception as e:
        conn.rollback()
        raise e
    finally:
        cursor.close()
        db.release_connection(conn)

def buscar_ultima_telemetria(eq_id):
    """
    busca o registro mais recente de um equipamento para processar o risco
    """
    conn = db.get_connection()
    cursor = conn.cursor()
    
    sql = """
        SELECT * FROM (
            SELECT * FROM TB_RISCO_AGRICOLA_TRATADO 
            WHERE EQUIPAMENTO_ID = :eq_id 
            ORDER BY DATA_MEDICAO DESC
        ) WHERE ROWNUM = 1
    """
    
    try:
        cursor.execute(sql, eq_id=eq_id)
        # transforma o resultado em dicionario para o ml_service
        colunas = [col[0].lower() for col in cursor.description]
        row = cursor.fetchone()
        if not row:
            return None
        return dict(zip(colunas, row))
    finally:
        cursor.close()
        db.release_connection(conn)