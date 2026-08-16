import hashlib

def gerar_hash_integridade(cursor, equipamento_id, data_medicao, score):
    
    sql_ultimo = """
        SELECT hash_integridade FROM TB_PREVISAO_RISCO
        WHERE ROWID = (
            SELECT rid FROM (
                SELECT ROWID as rid FROM TB_PREVISAO_RISCO 
                ORDER BY data_previsao DESC, equipamento_id DESC
            ) WHERE ROWNUM = 1
        )
        FOR UPDATE
    """
    
    cursor.execute(sql_ultimo)
    res = cursor.fetchone()
    
    if res is None:
        ultimo_hash = "genesis_block_sompo"
    else:
        ultimo_hash = res[0]
    
    conteudo = f"{equipamento_id}{data_medicao}{score}{ultimo_hash}"
    return hashlib.sha256(conteudo.encode()).hexdigest()