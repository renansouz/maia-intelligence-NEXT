"""noted by renansouz
Responsável por determinar quais equipamentos um usuario tem permissao
de ver/processar, de acordo com a hierarquia:
- seguradora: acesso a todos os equipamentos.
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
    if usuario["papel"] == "seguradora":
        return True
    if usuario["papel"] == "GESTOR":
        return equipamento_id in listar_equipamentos_do_gestor(usuario["id_usuario"])
    if usuario["papel"] == "OPERADOR":
        return equipamento_id in listar_equipamentos_do_operador(usuario["id_usuario"])
    return False


def listar_equipamentos_permitidos(usuario: dict):
    if usuario["papel"] == "seguradora":
        return None
    if usuario["papel"] == "GESTOR":
        return listar_equipamentos_do_gestor(usuario["id_usuario"])
    if usuario["papel"] == "OPERADOR":
        return listar_equipamentos_do_operador(usuario["id_usuario"])
    return []

def criar_maquina(equipamento_id, tipo=None, modelo=None, ano=None, criado_por=None, gestor_id=None, valor_segurado=None):
    conn = db.get_connection()
    cursor = conn.cursor()
    try:
        cursor.execute("""
            INSERT INTO TB_MAQUINA (EQUIPAMENTO_ID, TIPO, MODELO, ANO, CRIADO_POR, GESTOR_ID, VALOR_SEGURADO)
            VALUES (:eq, :tipo, :modelo, :ano, :criado_por, :gestor_id, :valor_segurado)
        """, eq=equipamento_id, tipo=tipo, modelo=modelo, ano=ano, criado_por=criado_por,
             gestor_id=gestor_id, valor_segurado=valor_segurado)
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
            SELECT ID_MAQUINA, EQUIPAMENTO_ID, FAZENDA_ID, TIPO, MODELO, ANO, STATUS, GESTOR_ID
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

def buscar_historico_maquina(equipamento_id: str):
    """
    Agrega tickets e manutenções de uma máquina numa única timeline.

    Correção: em vez de montar um dicionário a partir de cursor.description
    (que pode desalinhar dependendo de como o driver Oracle devolve os
    nomes em consultas com múltiplos JOINs), cada valor é lido pela
    posição da tupla retornada, na ordem exata do SELECT.
    """
    conn = db.get_connection()
    cursor = conn.cursor()
    try:
        cursor.execute("""
            SELECT t.ID_TICKET, t.CATEGORIA, t.OBSERVACAO, t.STATUS,
                   t.CRIADO_EM, t.RESOLVIDO_EM, u.NOME AS OPERADOR_NOME
            FROM TB_TICKET t
            JOIN TB_MAQUINA m ON t.MAQUINA_ID = m.ID_MAQUINA
            JOIN TB_USUARIO u ON t.OPERADOR_ID = u.ID_USUARIO
            WHERE m.EQUIPAMENTO_ID = :eq
        """, eq=equipamento_id)

        eventos = []
        for row in cursor.fetchall():
            id_ticket, categoria, observacao, status, criado_em, resolvido_em, operador_nome = row
            eventos.append({
                "tipo_evento": "TICKET",
                "data": criado_em,
                "titulo": f"Ticket aberto: {categoria}",
                "detalhe": observacao,
                "status": status,
                "responsavel": operador_nome,
                "data_resolucao": resolvido_em
            })

        cursor.execute("""
            SELECT man.ID_MANUTENCAO, man.TIPO, man.DESCRICAO, man.STATUS,
                   man.CRIADO_EM, man.DATA_MANUTENCAO, man.CONCLUIDO_EM
            FROM TB_MANUTENCAO man
            JOIN TB_MAQUINA m ON man.MAQUINA_ID = m.ID_MAQUINA
            WHERE m.EQUIPAMENTO_ID = :eq
        """, eq=equipamento_id)

        for row in cursor.fetchall():
            id_man, tipo, descricao, status, criado_em, data_manutencao, concluido_em = row
            eventos.append({
                "tipo_evento": "MANUTENCAO",
                "data": criado_em,
                "titulo": f"Manutenção solicitada ({tipo})",
                "detalhe": descricao,
                "status": status,
                "responsavel": None,
                "data_resolucao": concluido_em
            })

        eventos.sort(key=lambda e: e["data"], reverse=True)
        return eventos
    finally:
        cursor.close()
        db.release_connection(conn)

def listar_equipamentos_do_gestor_flat(gestor_id: int) -> list[str]:
    """Mesmo resultado de listar_equipamentos_do_gestor, mantido como
    alias semantico para uso especifico da tela de detalhe do gestor."""
    return listar_equipamentos_do_gestor(gestor_id)


def listar_maquinas_com_diagnostico(equipamento_ids=None):
    """
    Lista máquinas com dados de fazenda/gestor e o diagnóstico mais
    recente (score/classificação) de cada uma. Se equipamento_ids for
    None, lista todas (uso exclusivo da seguradora); caso contrário, filtra
    pela lista informada (uso do Gestor, ou de qualquer escopo restrito).

    Nota de performance: para cada máquina é feita uma consulta adicional
    da última previsão. Isso é aceitável para o volume atual do projeto
    (dezenas de equipamentos); numa escala maior valeria a pena reescrever
    como uma única consulta com subquery correlacionada.
    """
    conn = db.get_connection()
    cursor = conn.cursor()
    try:
        cursor.execute("""
            SELECT m.EQUIPAMENTO_ID, m.TIPO, m.MODELO,
                   f.NOME AS FAZENDA_NOME, f.ID_FAZENDA,
                   g.NOME AS GESTOR_NOME, g.ID_USUARIO AS GESTOR_ID
            FROM TB_MAQUINA m
            LEFT JOIN TB_FAZENDA f ON m.FAZENDA_ID = f.ID_FAZENDA
            LEFT JOIN TB_USUARIO g ON f.GESTOR_ID = g.ID_USUARIO
        """)
        colunas = [c[0].lower() for c in cursor.description]
        maquinas = [dict(zip(colunas, row)) for row in cursor.fetchall()]

        if equipamento_ids is not None:
            permitido = set(equipamento_ids)
            maquinas = [m for m in maquinas if m["equipamento_id"] in permitido]

        for m in maquinas:
            cursor.execute("""
                SELECT CLASSIFICACAO, PROBABILIDADE_ALTO
                FROM TB_PREVISAO_RISCO
                WHERE EQUIPAMENTO_ID = :eq
                AND ID_PREVISAO = (SELECT MAX(ID_PREVISAO) FROM TB_PREVISAO_RISCO WHERE EQUIPAMENTO_ID = :eq)
            """, eq=m["equipamento_id"])
            row = cursor.fetchone()
            m["classificacao"] = row[0] if row else None
            m["score"] = row[1] if row else None

        return maquinas
    finally:
        cursor.close()
        db.release_connection(conn)

def listar_maquinas_sem_fazenda_do_gestor(gestor_id: int):
    """
    Lista máquinas que já pertencem ao gestor (atribuídas pela seguradora no
    cadastro), mas ainda não foram vinculadas a nenhuma fazenda dele.
    Usada na tela de vínculo, para o gestor escolher o que ainda falta
    organizar, sem precisar digitar equipamento_id às cegas.
    """
    conn = db.get_connection()
    cursor = conn.cursor()
    try:
        cursor.execute("""
            SELECT EQUIPAMENTO_ID, TIPO, MODELO, ANO
            FROM TB_MAQUINA
            WHERE GESTOR_ID = :gestor_id AND FAZENDA_ID IS NULL
            ORDER BY EQUIPAMENTO_ID
        """, gestor_id=gestor_id)
        colunas = [c[0].lower() for c in cursor.description]
        return [dict(zip(colunas, row)) for row in cursor.fetchall()]
    finally:
        cursor.close()
        db.release_connection(conn)


def listar_operadores_sem_vinculo_na_maquina(maquina_equipamento_id: str, gestor_id: int):
    """
    Lista operadores do gestor que ainda não estão vinculados à máquina
    informada, usada na tela de vínculo operador↔máquina.
    """
    conn = db.get_connection()
    cursor = conn.cursor()
    try:
        cursor.execute("SELECT ID_MAQUINA FROM TB_MAQUINA WHERE EQUIPAMENTO_ID = :eq", eq=maquina_equipamento_id)
        row = cursor.fetchone()
        if not row:
            return []
        maquina_id = row[0]

        cursor.execute("""
            SELECT u.ID_USUARIO, u.NOME, u.EMAIL
            FROM TB_USUARIO u
            WHERE u.GESTOR_ID = :gestor_id AND u.PAPEL = 'OPERADOR'
            AND NOT EXISTS (
                SELECT 1 FROM TB_MAQUINA_OPERADOR mo 
                WHERE mo.MAQUINA_ID = :maquina_id AND mo.OPERADOR_ID = u.ID_USUARIO
            )
            ORDER BY u.NOME
        """, gestor_id=gestor_id, maquina_id=maquina_id)
        colunas = [c[0].lower() for c in cursor.description]
        return [dict(zip(colunas, row)) for row in cursor.fetchall()]
    finally:
        cursor.close()
        db.release_connection(conn)


def calcular_exposicao_financeira_total():
    conn = db.get_connection()
    cursor = conn.cursor()
    try:
        cursor.execute("""
            SELECT m.VALOR_SEGURADO
            FROM TB_MAQUINA m
            WHERE m.EQUIPAMENTO_ID IN (
                SELECT p.EQUIPAMENTO_ID FROM TB_PREVISAO_RISCO p
                WHERE p.CLASSIFICACAO = 'ALTO'
                AND p.ID_PREVISAO = (
                    SELECT MAX(ID_PREVISAO) FROM TB_PREVISAO_RISCO
                    WHERE EQUIPAMENTO_ID = p.EQUIPAMENTO_ID
                )
            )
        """)
        valores = [row[0] for row in cursor.fetchall() if row[0] is not None]
        return sum(valores)
    finally:
        cursor.close()
        db.release_connection(conn)

def buscar_detalhe_completo_maquina(equipamento_id: str):
    conn = db.get_connection()
    cursor = conn.cursor()
    try:
        cursor.execute("""
            SELECT
                m.ID_MAQUINA, m.EQUIPAMENTO_ID, m.TIPO, m.MODELO, m.ANO, m.STATUS,
                m.DATA_ULTIMA_MANUTENCAO,
                f.ID_FAZENDA, f.NOME AS FAZENDA_NOME, f.LATITUDE, f.LONGITUDE, f.ENDERECO,
                g.ID_USUARIO AS GESTOR_ID, g.NOME AS GESTOR_NOME, g.EMAIL AS GESTOR_EMAIL
            FROM TB_MAQUINA m
            LEFT JOIN TB_FAZENDA f ON m.FAZENDA_ID = f.ID_FAZENDA
            LEFT JOIN TB_USUARIO g ON f.GESTOR_ID = g.ID_USUARIO
            WHERE m.EQUIPAMENTO_ID = :eq
        """, eq=equipamento_id)

        row = cursor.fetchone()
        if not row:
            return None

        colunas = [c[0].lower() for c in cursor.description]
        maquina = dict(zip(colunas, row))

        cursor.execute("""
            SELECT u.ID_USUARIO, u.NOME, u.EMAIL
            FROM TB_MAQUINA_OPERADOR mo
            JOIN TB_USUARIO u ON mo.OPERADOR_ID = u.ID_USUARIO
            WHERE mo.MAQUINA_ID = :maquina_id
            ORDER BY u.NOME
        """, maquina_id=maquina["id_maquina"])
        colunas_op = [c[0].lower() for c in cursor.description]
        operadores = [dict(zip(colunas_op, r)) for r in cursor.fetchall()]

        maquina["operadores"] = operadores
        return maquina

    finally:
        cursor.close()
        db.release_connection(conn)