""" noted by renansouz
Este módulo atua como o 'cérebro' do backend, coordenando a integração:
1. Recebe dados brutos e aciona o ml_service para gerar a inteligência.
2. Solicita ao audit_service a geração do elo da corrente de integridade.
3. Garante a atomicidade da operação (ML + Hash + DB) em uma única transação.
"""
from app.core.database import db
from app.services.ml_service import ml_service
from app.services.audit_service import gerar_hash_integridade
from app.services.ticket_service import buscar_contexto_tickets

def processar_previsao_completa(dados_telemetria):
    resultado_ml = ml_service.prever_score(dados_telemetria)

    tickets = buscar_contexto_tickets(dados_telemetria["equipamento_id"])
    if tickets:
        contexto = ", ".join(f"{categoria}: {qtd}" for categoria, qtd in tickets)
        resultado_ml["explicacao_completa"] += (
            f" || RELATOS PENDENTES: {contexto}. Contexto operacional complementar; "
            "não altera a probabilidade do modelo."
        )
    
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
            INSERT INTO TB_PREVISAO_RISCO (
                EQUIPAMENTO_ID, CIDADE, DATA_MEDICAO, DATA_PREVISAO,
                CLASSIFICACAO, PROBABILIDADE_ALTO,
                MODELO_UTILIZADO, EXPLICACAO, HASH_INTEGRIDADE
            ) VALUES (
                :eq_id, :cid, TO_DATE(:dt_med, 'YYYY-MM-DD'), SYSDATE,
                :classif, :score, 'RandomForest_SHAP', :exp, :h_hash
            )
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


def verificar_integridade_cadeia():
    """
    Percorre TODA a cadeia de previsoes, na ordem em que foram criadas,
    e recalcula cada hash a partir dos dados armazenados + hash anterior.
    Se o hash recalculado nao bater com o hash gravado, a cadeia foi
    rompida a partir daquele ponto (dado alterado ou insercao fora de ordem).

    Retorna um relatorio simples: se a cadeia esta integra, e caso nao
    esteja, em qual ID_PREVISAO a quebra foi detectada.
    """
    import hashlib

    conn = db.get_connection()
    cursor = conn.cursor()

    try:
        cursor.execute("""
            SELECT ID_PREVISAO, EQUIPAMENTO_ID, DATA_MEDICAO, PROBABILIDADE_ALTO, HASH_INTEGRIDADE
            FROM TB_PREVISAO_RISCO
            ORDER BY ID_PREVISAO ASC
        """)
        registros = cursor.fetchall()

        if not registros:
            return {"integra": True, "total_registros": 0, "mensagem": "Nenhum registro para verificar."}

        hash_anterior = "genesis_block_sompo"

        for id_previsao, eq_id, data_medicao, score, hash_gravado in registros:
            data_str = data_medicao.strftime('%Y-%m-%d') if hasattr(data_medicao, 'strftime') else str(data_medicao)
            conteudo = f"{eq_id}{data_str}{score}{hash_anterior}"
            hash_recalculado = hashlib.sha256(conteudo.encode()).hexdigest()

            if hash_recalculado != hash_gravado:
                return {
                    "integra": False,
                    "total_registros": len(registros),
                    "quebra_detectada_em": id_previsao,
                    "mensagem": f"A cadeia foi rompida no registro ID_PREVISAO={id_previsao}. "
                                f"O hash armazenado nao corresponde ao recalculado a partir do historico."
                }

            hash_anterior = hash_gravado

        return {
            "integra": True,
            "total_registros": len(registros),
            "mensagem": "Cadeia de auditoria verificada com sucesso. Nenhuma alteracao detectada."
        }

    finally:
        cursor.close()
        db.release_connection(conn)