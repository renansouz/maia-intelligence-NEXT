"""noted by renansouz
O operador abre um ticket relatando um problema real na máquina. O
gestor da fazenda correspondente acompanha e resolve. Esse relato
retroalimenta futuramente a explicação do modelo de risco (ver
risco_service.py), mas o CRUD em si é isolado aqui.
"""
from app.core.database import db


def criar_ticket(equipamento_id: str, operador_id: int, categoria: str, observacao: str = None):
    conn = db.get_connection()
    cursor = conn.cursor()
    try:
        cursor.execute("SELECT ID_MAQUINA FROM TB_MAQUINA WHERE EQUIPAMENTO_ID = :eq", eq=equipamento_id)
        row = cursor.fetchone()
        if not row:
            return False
        maquina_id = row[0]

        cursor.execute("""
            INSERT INTO TB_TICKET (MAQUINA_ID, OPERADOR_ID, CATEGORIA, OBSERVACAO)
            VALUES (:maquina_id, :operador_id, :categoria, :observacao)
        """, maquina_id=maquina_id, operador_id=operador_id, categoria=categoria, observacao=observacao)
        conn.commit()
        return True
    except Exception as e:
        conn.rollback()
        raise e
    finally:
        cursor.close()
        db.release_connection(conn)


def listar_tickets_operador(operador_id: int):
    conn = db.get_connection()
    cursor = conn.cursor()
    try:
        cursor.execute("""
            SELECT t.ID_TICKET, m.EQUIPAMENTO_ID, t.CATEGORIA, t.OBSERVACAO,
                   t.STATUS, t.CRIADO_EM, t.RESOLVIDO_EM
            FROM TB_TICKET t
            JOIN TB_MAQUINA m ON t.MAQUINA_ID = m.ID_MAQUINA
            WHERE t.OPERADOR_ID = :operador_id
            ORDER BY t.CRIADO_EM DESC
        """, operador_id=operador_id)
        colunas = [c[0].lower() for c in cursor.description]
        return [dict(zip(colunas, row)) for row in cursor.fetchall()]
    finally:
        cursor.close()
        db.release_connection(conn)


def listar_tickets_gestor(gestor_id: int):
    conn = db.get_connection()
    cursor = conn.cursor()
    try:
        cursor.execute("""
            SELECT t.ID_TICKET, m.EQUIPAMENTO_ID, u.NOME AS OPERADOR_NOME,
                   t.CATEGORIA, t.OBSERVACAO, t.STATUS, t.CRIADO_EM, t.RESOLVIDO_EM
            FROM TB_TICKET t
            JOIN TB_MAQUINA m ON t.MAQUINA_ID = m.ID_MAQUINA
            JOIN TB_FAZENDA f ON m.FAZENDA_ID = f.ID_FAZENDA
            JOIN TB_USUARIO u ON t.OPERADOR_ID = u.ID_USUARIO
            WHERE f.GESTOR_ID = :gestor_id
            ORDER BY t.STATUS ASC, t.CRIADO_EM DESC
        """, gestor_id=gestor_id)
        colunas = [c[0].lower() for c in cursor.description]
        return [dict(zip(colunas, row)) for row in cursor.fetchall()]
    finally:
        cursor.close()
        db.release_connection(conn)

def buscar_detalhe_ticket(ticket_id: int, gestor_id: int):
    """Detalhe completo do ticket, usado no botão "ver mais" da lista do gestor."""
    conn = db.get_connection()
    cursor = conn.cursor()
    try:
        cursor.execute("""
            SELECT t.ID_TICKET, m.EQUIPAMENTO_ID, m.TIPO, m.MODELO,
                   u.NOME AS OPERADOR_NOME, u.EMAIL AS OPERADOR_EMAIL,
                   t.CATEGORIA, t.OBSERVACAO, t.STATUS, t.CRIADO_EM, t.RESOLVIDO_EM
            FROM TB_TICKET t
            JOIN TB_MAQUINA m ON t.MAQUINA_ID = m.ID_MAQUINA
            JOIN TB_USUARIO u ON t.OPERADOR_ID = u.ID_USUARIO
            WHERE t.ID_TICKET = :ticket_id
            AND m.FAZENDA_ID IN (SELECT ID_FAZENDA FROM TB_FAZENDA WHERE GESTOR_ID = :gestor_id)
        """, ticket_id=ticket_id, gestor_id=gestor_id)
        row = cursor.fetchone()
        if not row:
            return None
        colunas = [c[0].lower() for c in cursor.description]
        return dict(zip(colunas, row))
    finally:
        cursor.close()
        db.release_connection(conn)


def resolver_ticket(ticket_id: int, gestor_id: int) -> bool:
    conn = db.get_connection()
    cursor = conn.cursor()
    try:
        cursor.execute("""
            UPDATE TB_TICKET
            SET STATUS = 'RESOLVIDO', RESOLVIDO_EM = SYSDATE
            WHERE ID_TICKET = :ticket_id
            AND MAQUINA_ID IN (
                SELECT m.ID_MAQUINA FROM TB_MAQUINA m
                JOIN TB_FAZENDA f ON m.FAZENDA_ID = f.ID_FAZENDA
                WHERE f.GESTOR_ID = :gestor_id
            )
        """, ticket_id=ticket_id, gestor_id=gestor_id)
        conn.commit()
        return cursor.rowcount > 0
    except Exception as e:
        conn.rollback()
        raise e
    finally:
        cursor.close()
        db.release_connection(conn)

def buscar_contexto_tickets(equipamento_id: str):
    conn = db.get_connection()
    cursor = conn.cursor()
    try:
        cursor.execute("""
            SELECT CATEGORIA, COUNT(*) FROM TB_TICKET t
            JOIN TB_MAQUINA m ON t.MAQUINA_ID = m.ID_MAQUINA
            WHERE m.EQUIPAMENTO_ID = :eq AND t.STATUS = 'ABERTO'
            GROUP BY CATEGORIA ORDER BY CATEGORIA
        """, eq=equipamento_id)
        return cursor.fetchall()
    finally:
        cursor.close()
        db.release_connection(conn)

def escalar_ticket_sompo(ticket_id: int, gestor_id: int) -> bool:
    conn = db.get_connection()
    cursor = conn.cursor()
    try:
        cursor.execute("""
            UPDATE TB_TICKET
            SET STATUS = 'ESCALADO_SOMPO', ESCALADO_EM = SYSTIMESTAMP
            WHERE ID_TICKET = :ticket_id
            AND MAQUINA_ID IN (
                SELECT m.ID_MAQUINA FROM TB_MAQUINA m
                JOIN TB_FAZENDA f ON m.FAZENDA_ID = f.ID_FAZENDA
                WHERE f.GESTOR_ID = :gestor_id
            )
        """, ticket_id=ticket_id, gestor_id=gestor_id)
        conn.commit()
        return cursor.rowcount > 0
    except Exception as e:
        conn.rollback()
        raise e
    finally:
        cursor.close()
        db.release_connection(conn)


def listar_sinistros_sompo():
    """Lista todos os tickets escalados como sinistro, de todos os gestores, usada pela Sompo."""
    conn = db.get_connection()
    cursor = conn.cursor()
    try:
        cursor.execute("""
            SELECT t.ID_TICKET, m.EQUIPAMENTO_ID, g.NOME AS GESTOR_NOME,
                   u.NOME AS OPERADOR_NOME, t.CATEGORIA, t.OBSERVACAO,
                   t.CRIADO_EM, t.ESCALADO_EM
            FROM TB_TICKET t
            JOIN TB_MAQUINA m ON t.MAQUINA_ID = m.ID_MAQUINA
            JOIN TB_FAZENDA f ON m.FAZENDA_ID = f.ID_FAZENDA
            JOIN TB_USUARIO g ON f.GESTOR_ID = g.ID_USUARIO
            JOIN TB_USUARIO u ON t.OPERADOR_ID = u.ID_USUARIO
            WHERE t.STATUS = 'ESCALADO_SOMPO'
            ORDER BY t.ESCALADO_EM DESC
        """)
        colunas = [c[0].lower() for c in cursor.description]
        return [dict(zip(colunas, row)) for row in cursor.fetchall()]
    finally:
        cursor.close()
        db.release_connection(conn)