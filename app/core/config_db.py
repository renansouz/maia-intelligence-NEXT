from app.core.database import db
import oracledb

def coluna_existe(cursor, tabela, coluna):
    query = """
        SELECT COUNT(*) FROM user_tab_columns 
        WHERE table_name = :tname AND column_name = :cname
    """
    cursor.execute(query, tname=tabela.upper(), cname=coluna.upper())
    return cursor.fetchone()[0] > 0

def pk_correta(cursor, tabela):
    query = """
        SELECT COUNT(*) FROM user_cons_columns ucc
        JOIN user_constraints uc ON ucc.constraint_name = uc.constraint_name
        WHERE uc.table_name = :tname AND uc.constraint_type = 'P'
    """
    cursor.execute(query, tname=tabela.upper())
    return cursor.fetchone()[0] == 2

def configurar_banco():
    conn = db.get_connection()
    cursor = conn.cursor()
    
    try:
        tabelas = {
            "TB_RISCO_AGRICOLA": "EQUIPAMENTO_ID VARCHAR2(20), CIDADE VARCHAR2(100), DATA_MEDICAO DATE",
            "TB_RISCO_AGRICOLA_TRATADO": "EQUIPAMENTO_ID VARCHAR2(20), CIDADE VARCHAR2(100), DATA_MEDICAO DATE",
            "TB_PREVISAO_RISCO": "EQUIPAMENTO_ID VARCHAR2(20), CIDADE VARCHAR2(100), DATA_MEDICAO DATE",
            "TB_LOG_ACESSO": "ID_LOG NUMBER GENERATED ALWAYS AS IDENTITY, METODO VARCHAR2(10)"
        }

        for nome, campos in tabelas.items():
            try:
                cursor.execute(f"CREATE TABLE {nome} ({campos})")
                print(f"Infra: {nome} verificada.")
            except oracledb.DatabaseError as e:
                if "ORA-00955" not in str(e): raise e

        colunas_novas = [
            ("TB_LOG_ACESSO", "ROTA", "VARCHAR2(255)"),
            ("TB_LOG_ACESSO", "STATUS_CODE", "NUMBER(3)"),
            ("TB_LOG_ACESSO", "IP_ORIGEM", "VARCHAR2(50)"),
            ("TB_LOG_ACESSO", "TEMPO_MS", "NUMBER"),
            ("TB_LOG_ACESSO", "TIMESTAMP_LOG", "TIMESTAMP DEFAULT CURRENT_TIMESTAMP"),
            
            ("TB_RISCO_AGRICOLA_TRATADO", "RISCO_OPERACIONAL", "NUMBER(1)"),
            ("TB_RISCO_AGRICOLA_TRATADO", "TEMPERATURA", "NUMBER"),
            ("TB_RISCO_AGRICOLA_TRATADO", "CHUVA_MM", "NUMBER"),
            ("TB_RISCO_AGRICOLA_TRATADO", "UMIDADE_SOLO", "NUMBER"),
            ("TB_RISCO_AGRICOLA_TRATADO", "VELOCIDADE_KMH", "NUMBER"),
            ("TB_RISCO_AGRICOLA_TRATADO", "PROXIMIDADE_AGUA_M", "NUMBER"),
            ("TB_RISCO_AGRICOLA_TRATADO", "INCLINACAO_GRAUS", "NUMBER"),
            ("TB_RISCO_AGRICOLA_TRATADO", "TEMPO_USO_HORAS", "NUMBER"),
            ("TB_RISCO_AGRICOLA_TRATADO", "MANUTENCAO_DIAS", "NUMBER"),
            ("TB_RISCO_AGRICOLA_TRATADO", "INDICADOR_CHUVA_ALTA", "NUMBER(1)"),
            ("TB_RISCO_AGRICOLA_TRATADO", "INDICADOR_SOLO_UMIDO", "NUMBER(1)"),
            ("TB_RISCO_AGRICOLA_TRATADO", "INDICADOR_VELOCIDADE_ALTA", "NUMBER(1)"),
            ("TB_RISCO_AGRICOLA_TRATADO", "INDICADOR_PERTO_AGUA", "NUMBER(1)"),
            ("TB_RISCO_AGRICOLA_TRATADO", "INDICADOR_INCLINACAO_ALTA", "NUMBER(1)"),
            ("TB_RISCO_AGRICOLA_TRATADO", "INDICADOR_MANUTENCAO_ATRASADA", "NUMBER(1)"),
            
            ("TB_PREVISAO_RISCO", "HASH_INTEGRIDADE", "VARCHAR2(64)"),
            ("TB_PREVISAO_RISCO", "DATA_PREVISAO", "DATE"),
            ("TB_PREVISAO_RISCO", "CLASSIFICACAO", "VARCHAR2(20)"),
            ("TB_PREVISAO_RISCO", "PROBABILIDADE_ALTO", "NUMBER"),
            ("TB_PREVISAO_RISCO", "MODELO_UTILIZADO", "VARCHAR2(50)"),
            ("TB_PREVISAO_RISCO", "EXPLICACAO", "VARCHAR2(4000)")
        ]

        for tab, col, tipo in colunas_novas:
            if not coluna_existe(cursor, tab, col):
                print(f"Migração: Adicionando {col} em {tab}...")
                cursor.execute(f"ALTER TABLE {tab} ADD {col} {tipo}")

        for tab in ["TB_RISCO_AGRICOLA", "TB_RISCO_AGRICOLA_TRATADO", "TB_PREVISAO_RISCO"]:
            if not pk_correta(cursor, tab):
                try: cursor.execute(f"ALTER TABLE {tab} DROP PRIMARY KEY")
                except: pass
                cursor.execute(f"ALTER TABLE {tab} ADD PRIMARY KEY (EQUIPAMENTO_ID, DATA_MEDICAO)")

        conn.commit()
        print("Infraestrutura de dados: Sincronizada.")

    except Exception as e:
        conn.rollback()
        print(f"Falha na sincronização de infraestrutura: {e}")
    finally:
        cursor.close()
        db.release_connection(conn)

if __name__ == "__main__":
    configurar_banco()