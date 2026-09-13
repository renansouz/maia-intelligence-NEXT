"""noted by renansouz
Responsável pela interface direta com o Oracle Database para:
1. Ingestão de telemetria via INSERT (cada leitura é um evento novo).
2. Recuperação de registros históricos e métricas para o frontend.
3. Abstração das queries SQL para manter o restante do sistema independente do banco.

Centraliza o acesso ao dado para garantir que todas as 
operações utilizem o Oracle Session Pool de forma eficiente.
"""
from app.core.database import db
import oracledb

def salvar_telemetria_db(dados_dict):
    conn = db.get_connection()
    cursor = conn.cursor()
    
    dt_str = dados_dict['data_medicao'].isoformat()
    
    sql = """
    INSERT INTO TB_RISCO_AGRICOLA_TRATADO (
        EQUIPAMENTO_ID, CIDADE, DATA_MEDICAO, TEMPERATURA, CHUVA_MM,
        UMIDADE_SOLO, VELOCIDADE_KMH, PROXIMIDADE_AGUA_M, INCLINACAO_GRAUS,
        TEMPO_USO_HORAS, MANUTENCAO_DIAS
    ) VALUES (
        :eq_id, :cid, TO_DATE(:dt_med, 'YYYY-MM-DD'), :temp, :chuva,
        :umid, :vel, :prox, :incl, :t_uso, :manut
    )
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
    conn = db.get_connection()
    cursor = conn.cursor()
    
    sql = """
        SELECT * FROM TB_RISCO_AGRICOLA_TRATADO
        WHERE EQUIPAMENTO_ID = :eq_id
        AND ID_TELEMETRIA = (
            SELECT MAX(ID_TELEMETRIA) FROM TB_RISCO_AGRICOLA_TRATADO
            WHERE EQUIPAMENTO_ID = :eq_id
        )
    """
    
    try:
        cursor.execute(sql, eq_id=eq_id)
        colunas = [col[0].lower() for col in cursor.description]
        row = cursor.fetchone()
        if not row:
            return None
        return dict(zip(colunas, row))
    finally:
        cursor.close()
        db.release_connection(conn)

def buscar_ultima_previsao(equipamento_id):
    """
    Busca a PREVISAO mais recente ja processada para um equipamento,
    sem disparar novo processamento de ML. Usada pela rota de leitura
    (GET), que deve ser segura/idempotente por definicao REST.
    """
    conn = db.get_connection()
    cursor = conn.cursor()

    sql = """
        SELECT * FROM TB_PREVISAO_RISCO
        WHERE EQUIPAMENTO_ID = :eq_id
        AND ID_PREVISAO = (
            SELECT MAX(ID_PREVISAO) FROM TB_PREVISAO_RISCO
            WHERE EQUIPAMENTO_ID = :eq_id
        )
    """

    try:
        cursor.execute(sql, eq_id=equipamento_id)
        colunas = [col[0].lower() for col in cursor.description]
        row = cursor.fetchone()
        if not row:
            return None
        return dict(zip(colunas, row))
    finally:
        cursor.close()
        db.release_connection(conn)