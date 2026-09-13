""" noted by renansouz
Este serviço garante a integridade imutável das decisões da IA:
1. Implementa uma estrutura de 'ledger' onde cada hash depende do registro anterior.
2. Utiliza SHA-256 para gerar assinaturas digitais únicas por predição.
3. Gerencia concorrência via lock transacional (FOR UPDATE) para garantir unicidade da cadeia.

Decisão de Design: O uso de Hash Chain provê segurança jurídica à Sompo, 
permitindo provar que um registro histórico não foi adulterado após sua criação.
"""
import hashlib

def gerar_hash_integridade(cursor, equipamento_id, data_medicao, score):
    
    sql_ultimo = """
        SELECT HASH_INTEGRIDADE
        FROM TB_PREVISAO_RISCO
        WHERE ID_PREVISAO = (SELECT MAX(ID_PREVISAO) FROM TB_PREVISAO_RISCO)
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