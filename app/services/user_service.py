"""noted by renansouz
Responsável por:
1. CRUD basico de TB_USUARIO.
2. Bootstrap do primeiro usuario SOMPO (admin), necessario porque so um
   usuario SOMPO pode criar outros usuarios - sem isso, ninguem conseguiria
   fazer login pela primeira vez no sistema.
"""
import os
from app.core.database import db
from app.services.auth_service import hash_senha


def buscar_usuario_por_email(email: str):
    conn = db.get_connection()
    cursor = conn.cursor()
    try:
        cursor.execute("""
            SELECT ID_USUARIO, NOME, EMAIL, SENHA_HASH, PAPEL, GESTOR_ID, ATIVO
            FROM TB_USUARIO WHERE EMAIL = :email
        """, email=email)
        row = cursor.fetchone()
        if not row:
            return None
        colunas = [c[0].lower() for c in cursor.description]
        return dict(zip(colunas, row))
    finally:
        cursor.close()
        db.release_connection(conn)


def criar_usuario(nome, email, senha_plana, papel, gestor_id=None, tipo_cobertura=None):
    conn = db.get_connection()
    cursor = conn.cursor()
    try:
        senha_hash = hash_senha(senha_plana)
        cursor.execute("""
            INSERT INTO TB_USUARIO (NOME, EMAIL, SENHA_HASH, PAPEL, GESTOR_ID, TIPO_COBERTURA)
            VALUES (:nome, :email, :senha_hash, :papel, :gestor_id, :tipo_cobertura)
        """, nome=nome, email=email, senha_hash=senha_hash, papel=papel,
             gestor_id=gestor_id, tipo_cobertura=tipo_cobertura)
        conn.commit()
        return True
    except Exception as e:
        conn.rollback()
        raise e
    finally:
        cursor.close()
        db.release_connection(conn)


def garantir_usuario_sompo_inicial():
    conn = db.get_connection()
    cursor = conn.cursor()
    try:
        cursor.execute("SELECT COUNT(*) FROM TB_USUARIO WHERE PAPEL = 'SOMPO'")
        total = cursor.fetchone()[0]
        if total > 0:
            return

        admin_email = os.getenv("ADMIN_EMAIL")
        admin_senha = os.getenv("ADMIN_SENHA")

        if not admin_email or not admin_senha:
            print("AVISO: nenhum usuario SOMPO existe e ADMIN_EMAIL/ADMIN_SENHA "
                  "nao estao configurados no .env. Usuario administrador inicial "
                  "nao foi criado.")
            return

        senha_hash = hash_senha(admin_senha)
        cursor.execute("""
            INSERT INTO TB_USUARIO (NOME, EMAIL, SENHA_HASH, PAPEL)
            VALUES ('Sompo Seguros', :email, :senha_hash, 'SOMPO')
        """, email=admin_email, senha_hash=senha_hash)
        conn.commit()
        print(f"Usuario SOMPO inicial criado: {admin_email}")
    finally:
        cursor.close()
        db.release_connection(conn)

def listar_operadores_do_gestor(gestor_id: int):
    conn = db.get_connection()
    cursor = conn.cursor()
    try:
        cursor.execute("""
            SELECT ID_USUARIO, NOME, EMAIL, ATIVO
            FROM TB_USUARIO WHERE GESTOR_ID = :gestor_id AND PAPEL = 'OPERADOR'
            ORDER BY NOME
        """, gestor_id=gestor_id)
        colunas = [c[0].lower() for c in cursor.description]
        return [dict(zip(colunas, row)) for row in cursor.fetchall()]
    finally:
        cursor.close()
        db.release_connection(conn)

def buscar_usuario_por_id(id_usuario: int):
    conn = db.get_connection()
    cursor = conn.cursor()
    try:
        cursor.execute("""
            SELECT ID_USUARIO, NOME, EMAIL, PAPEL, GESTOR_ID, TIPO_COBERTURA, ATIVO
            FROM TB_USUARIO WHERE ID_USUARIO = :id
        """, id=id_usuario)
        row = cursor.fetchone()
        if not row:
            return None
        colunas = [c[0].lower() for c in cursor.description]
        return dict(zip(colunas, row))
    finally:
        cursor.close()
        db.release_connection(conn)


def listar_gestores_com_estatisticas():
    """
    Lista todos os gestores com contadores de fazenda e máquina, usada
    pela tela da Sompo ao clicar em "Gestores Ativos".
    """
    conn = db.get_connection()
    cursor = conn.cursor()
    try:
        cursor.execute("""
            SELECT ID_USUARIO, NOME, EMAIL, TIPO_COBERTURA, ATIVO
            FROM TB_USUARIO WHERE PAPEL = 'GESTOR' ORDER BY NOME
        """)
        colunas = [c[0].lower() for c in cursor.description]
        gestores = [dict(zip(colunas, row)) for row in cursor.fetchall()]

        for g in gestores:
            cursor.execute("SELECT COUNT(*) FROM TB_FAZENDA WHERE GESTOR_ID = :id", id=g["id_usuario"])
            g["total_fazendas"] = cursor.fetchone()[0]

            cursor.execute("""
                SELECT COUNT(*) FROM TB_MAQUINA m
                JOIN TB_FAZENDA f ON m.FAZENDA_ID = f.ID_FAZENDA
                WHERE f.GESTOR_ID = :id
            """, id=g["id_usuario"])
            g["total_maquinas"] = cursor.fetchone()[0]

        return gestores
    finally:
        cursor.close()
        db.release_connection(conn)