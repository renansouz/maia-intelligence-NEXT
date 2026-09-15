"""noted by renansouz
Responsável por determinar quais equipamentos um usuario tem permissao
de ver/processar, de acordo com a hierarquia:
- SOMPO: acesso a todos os equipamentos.
- GESTOR: acesso aos equipamentos vinculados as fazendas dele.
- OPERADOR: acesso aos equipamentos vinculados a ele em TB_MAQUINA_OPERADOR.
"""
from app.core.database import db


def listar_equipamentos_do_gestor(gestor_id: int) -> list[str]:
    conn = db.get_connection()
    cursor = conn.cursor()
    try:
        cursor.execute("""
            SELECT M.EQUIPAMENTO_ID
            FROM TB_MAQUINA M
            JOIN TB_FAZENDA F ON M.FAZENDA_ID = F.ID_FAZENDA
            WHERE F.GESTOR_ID = :gestor_id
        """, gestor_id=gestor_id)
        return [row[0] for row in cursor.fetchall()]
    finally:
        cursor.close()
        db.release_connection(conn)


def listar_equipamentos_do_operador(operador_id: int) -> list[str]:
    conn = db.get_connection()
    cursor = conn.cursor()
    try:
        cursor.execute("""
            SELECT M.EQUIPAMENTO_ID
            FROM TB_MAQUINA M
            JOIN TB_MAQUINA_OPERADOR MO ON M.ID_MAQUINA = MO.MAQUINA_ID
            WHERE MO.OPERADOR_ID = :operador_id
        """, operador_id=operador_id)
        return [row[0] for row in cursor.fetchall()]
    finally:
        cursor.close()
        db.release_connection(conn)


def usuario_tem_acesso_equipamento(usuario: dict, equipamento_id: str) -> bool:
    if usuario["papel"] == "SOMPO":
        return True
    if usuario["papel"] == "GESTOR":
        return equipamento_id in listar_equipamentos_do_gestor(usuario["id_usuario"])
    if usuario["papel"] == "OPERADOR":
        return equipamento_id in listar_equipamentos_do_operador(usuario["id_usuario"])
    return False


def listar_equipamentos_permitidos(usuario: dict):
    if usuario["papel"] == "SOMPO":
        return None
    if usuario["papel"] == "GESTOR":
        return listar_equipamentos_do_gestor(usuario["id_usuario"])
    if usuario["papel"] == "OPERADOR":
        return listar_equipamentos_do_operador(usuario["id_usuario"])
    return []

def criar_maquina(equipamento_id, tipo=None, modelo=None, ano=None, criado_por=None):
    conn = db.get_connection()
    cursor = conn.cursor()
    try:
        cursor.execute("""
            INSERT INTO TB_MAQUINA (EQUIPAMENTO_ID, TIPO, MODELO, ANO, CRIADO_POR)
            VALUES (:eq, :tipo, :modelo, :ano, :criado_por)
        """, eq=equipamento_id, tipo=tipo, modelo=modelo, ano=ano, criado_por=criado_por)
        conn.commit()
        return True
    except Exception as e:
        conn.rollback()
        raise e
    finally:
        cursor.close()
        db.release_connection(conn)


def buscar_maquina_por_equipamento_id(equipamento_id):
    conn = db.get_connection()
    cursor = conn.cursor()
    try:
        cursor.execute("""
            SELECT ID_MAQUINA, EQUIPAMENTO_ID, FAZENDA_ID, TIPO, MODELO, ANO, STATUS
            FROM TB_MAQUINA WHERE EQUIPAMENTO_ID = :eq
        """, eq=equipamento_id)
        row = cursor.fetchone()
        if not row:
            return None
        colunas = [c[0].lower() for c in cursor.description]
        return dict(zip(colunas, row))
    finally:
        cursor.close()
        db.release_connection(conn)


def vincular_maquina_fazenda(equipamento_id, fazenda_id):
    conn = db.get_connection()
    cursor = conn.cursor()
    try:
        cursor.execute("""
            UPDATE TB_MAQUINA SET FAZENDA_ID = :fazenda_id WHERE EQUIPAMENTO_ID = :eq
        """, fazenda_id=fazenda_id, eq=equipamento_id)
        conn.commit()
        return cursor.rowcount > 0
    except Exception as e:
        conn.rollback()
        raise e
    finally:
        cursor.close()
        db.release_connection(conn)


def vincular_operador_maquina(equipamento_id, operador_id):
    conn = db.get_connection()
    cursor = conn.cursor()
    try:
        cursor.execute("SELECT ID_MAQUINA FROM TB_MAQUINA WHERE EQUIPAMENTO_ID = :eq", eq=equipamento_id)
        row = cursor.fetchone()
        if not row:
            return False
        maquina_id = row[0]

        cursor.execute("""
            MERGE INTO TB_MAQUINA_OPERADOR t
            USING (SELECT :maquina_id as m, :operador_id as o FROM DUAL) s
            ON (t.MAQUINA_ID = s.m AND t.OPERADOR_ID = s.o)
            WHEN NOT MATCHED THEN
                INSERT (MAQUINA_ID, OPERADOR_ID) VALUES (:maquina_id, :operador_id)
        """, maquina_id=maquina_id, operador_id=operador_id)
        conn.commit()
        return True
    except Exception as e:
        conn.rollback()
        raise e
    finally:
        cursor.close()
        db.release_connection(conn)