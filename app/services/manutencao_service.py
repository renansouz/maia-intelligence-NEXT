"""noted by renansouz
O gestor solicita manutenção de uma máquina e recebe um link único
(token) para enviar ao técnico. O técnico, sem login, acessa esse link,
registra o que foi feito, e isso reprocessa o score da máquina.


o token expira em 7 dias e é de uso único, depois de concluído, não pode ser
reaberto. Se o recálculo do score falhar por qualquer motivo, o registro
de manutenção permanece salvo (não é desfeito), porque a manutenção
física já aconteceu de verdade; o gestor pode gerar uma nova análise
depois manualmente.
"""
import secrets
from app.core.database import db
from app.services.data_service import buscar_ultima_telemetria
from app.services.risco_service import processar_previsao_completa


def solicitar_manutencao(equipamento_id: str, gestor_id: int, descricao: str = None, tipo: str = "PREVENTIVA") -> str:
    conn = db.get_connection()
    cursor = conn.cursor()
    try:
        cursor.execute("SELECT ID_MAQUINA FROM TB_MAQUINA WHERE EQUIPAMENTO_ID = :eq", eq=equipamento_id)
        row = cursor.fetchone()
        if not row:
            return None
        maquina_id = row[0]

        token = secrets.token_hex(32)

        cursor.execute("""
            INSERT INTO TB_MANUTENCAO (MAQUINA_ID, SOLICITADO_POR, DESCRICAO, TIPO, TOKEN_LINK, TOKEN_EXPIRA_EM, STATUS)
            VALUES (:maquina_id, :gestor_id, :descricao, :tipo, :token, SYSTIMESTAMP + INTERVAL '7' DAY, 'SOLICITADA')
        """, maquina_id=maquina_id, gestor_id=gestor_id, descricao=descricao, tipo=tipo, token=token)
        conn.commit()
        return token
    except Exception as e:
        conn.rollback()
        raise e
    finally:
        cursor.close()
        db.release_connection(conn)


def buscar_manutencao_por_token(token: str):
    """
    Usado pela página externa do técnico ao abrir o link. Só retorna
    dado se o token existir, ainda estiver com status SOLICITADA e não
    tiver expirado.
    """
    conn = db.get_connection()
    cursor = conn.cursor()
    try:
        cursor.execute("""
            SELECT man.ID_MANUTENCAO, maq.EQUIPAMENTO_ID, maq.TIPO, maq.MODELO,
                   man.DESCRICAO, man.TIPO AS TIPO_MANUTENCAO, man.CRIADO_EM
            FROM TB_MANUTENCAO man
            JOIN TB_MAQUINA maq ON man.MAQUINA_ID = maq.ID_MAQUINA
            WHERE man.TOKEN_LINK = :token
            AND man.STATUS = 'SOLICITADA'
            AND man.TOKEN_EXPIRA_EM > SYSTIMESTAMP
        """, token=token)
        row = cursor.fetchone()
        if not row:
            return None
        colunas = [c[0].lower() for c in cursor.description]
        return dict(zip(colunas, row))
    finally:
        cursor.close()
        db.release_connection(conn)


def concluir_manutencao(token: str, data_realizada: str, hora_realizada: str, descricao: str):
    """
    Registra a conclusão e tenta reprocessar o score da máquina. A
    conexão de banco é liberada ANTES de chamar o motor de ML (que abre
    sua própria conexão), evitando prender duas conexões do pool na
    mesma requisição.
    """
    conn = db.get_connection()
    cursor = conn.cursor()
    equipamento_id = None

    try:
        cursor.execute("""
            SELECT man.ID_MANUTENCAO, man.MAQUINA_ID, maq.EQUIPAMENTO_ID
            FROM TB_MANUTENCAO man
            JOIN TB_MAQUINA maq ON man.MAQUINA_ID = maq.ID_MAQUINA
            WHERE man.TOKEN_LINK = :token
            AND man.STATUS = 'SOLICITADA'
            AND man.TOKEN_EXPIRA_EM > SYSTIMESTAMP
        """, token=token)
        row = cursor.fetchone()
        if not row:
            return None

        id_manutencao, maquina_id, equipamento_id = row
        data_hora_str = f"{data_realizada} {hora_realizada}"

        cursor.execute("""
            UPDATE TB_MANUTENCAO
            SET STATUS = 'CONCLUIDA',
                DATA_MANUTENCAO = TO_DATE(:data_hora, 'YYYY-MM-DD HH24:MI'),
                DESCRICAO = :descricao,
                CONCLUIDO_EM = SYSTIMESTAMP
            WHERE ID_MANUTENCAO = :id_manutencao
        """, data_hora=data_hora_str, descricao=descricao, id_manutencao=id_manutencao)

        cursor.execute("""
            UPDATE TB_MAQUINA SET DATA_ULTIMA_MANUTENCAO = TO_DATE(:data_realizada, 'YYYY-MM-DD')
            WHERE ID_MAQUINA = :maquina_id
        """, data_realizada=data_realizada, maquina_id=maquina_id)

        conn.commit()

    except Exception as e:
        conn.rollback()
        raise e
    finally:
        cursor.close()
        db.release_connection(conn)

    # Recálculo do score, fora do bloco de conexão acima de propósito.
    # Se falhar, a manutenção já está salva e não é desfeita.
    try:
        dados_telemetria = buscar_ultima_telemetria(equipamento_id)
        if dados_telemetria:
            if not isinstance(dados_telemetria['data_medicao'], str):
                dados_telemetria['data_medicao'] = dados_telemetria['data_medicao'].strftime('%Y-%m-%d')
            processar_previsao_completa(dados_telemetria)
    except Exception as e:
        print(f"Aviso: manutenção registrada, mas falhou o recálculo automático do score: {e}")

    return equipamento_id