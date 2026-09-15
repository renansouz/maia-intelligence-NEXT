from app.core.database import db

def criar_fazenda(gestor_id, nome, latitude, longitude, endereco=None):
    conn = db.get_connection()
    cursor = conn.cursor()
    try:
        cursor.execute("""
            INSERT INTO TB_FAZENDA (GESTOR_ID, NOME, LATITUDE, LONGITUDE, ENDERECO)
            VALUES (:gestor_id, :nome, :lat, :lon, :end)
        """, gestor_id=gestor_id, nome=nome, lat=latitude, lon=longitude, end=endereco)
        conn.commit()
        return True
    except Exception as e:
        conn.rollback()
        raise e
    finally:
        cursor.close()
        db.release_connection(conn)


def listar_fazendas_do_gestor(gestor_id):
    conn = db.get_connection()
    cursor = conn.cursor()
    try:
        cursor.execute("""
            SELECT ID_FAZENDA, NOME, LATITUDE, LONGITUDE, ENDERECO
            FROM TB_FAZENDA WHERE GESTOR_ID = :gestor_id ORDER BY NOME
        """, gestor_id=gestor_id)
        colunas = [c[0].lower() for c in cursor.description]
        return [dict(zip(colunas, row)) for row in cursor.fetchall()]
    finally:
        cursor.close()
        db.release_connection(conn)


def buscar_fazenda_por_id(fazenda_id):
    conn = db.get_connection()
    cursor = conn.cursor()
    try:
        cursor.execute("SELECT ID_FAZENDA, GESTOR_ID, NOME FROM TB_FAZENDA WHERE ID_FAZENDA = :id", id=fazenda_id)
        row = cursor.fetchone()
        if not row:
            return None
        colunas = [c[0].lower() for c in cursor.description]
        return dict(zip(colunas, row))
    finally:
        cursor.close()
        db.release_connection(conn)