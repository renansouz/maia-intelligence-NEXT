from app.core.database import db
import oracledb

def coluna_existe(cursor, tabela, coluna):
    query = """
        SELECT COUNT(*) FROM user_tab_columns 
        WHERE table_name = :tname AND column_name = :cname
    """
    cursor.execute(query, tname=tabela.upper(), cname=coluna.upper())
    return cursor.fetchone()[0] > 0

def obter_colunas_pk(cursor, tabela):
    query = """
        SELECT ucc.column_name
        FROM user_cons_columns ucc
        JOIN user_constraints uc ON ucc.constraint_name = uc.constraint_name
        WHERE uc.table_name = :tname AND uc.constraint_type = 'P'
        ORDER BY ucc.position
    """
    cursor.execute(query, tname=tabela.upper())
    return [row[0] for row in cursor.fetchall()]

def configurar_banco():
    conn = db.get_connection()
    cursor = conn.cursor()
    
    try:
        tabelas = {
            "TB_RISCO_AGRICOLA": "EQUIPAMENTO_ID VARCHAR2(20), CIDADE VARCHAR2(100), DATA_MEDICAO DATE",
            "TB_RISCO_AGRICOLA_TRATADO": "EQUIPAMENTO_ID VARCHAR2(20), CIDADE VARCHAR2(100), DATA_MEDICAO DATE",
            "TB_PREVISAO_RISCO": "EQUIPAMENTO_ID VARCHAR2(20), CIDADE VARCHAR2(100), DATA_MEDICAO DATE",
            "TB_LOG_ACESSO": "ID_LOG NUMBER GENERATED ALWAYS AS IDENTITY, METODO VARCHAR2(10)",

            "TB_USUARIO": """
                ID_USUARIO NUMBER GENERATED ALWAYS AS IDENTITY PRIMARY KEY,
                NOME VARCHAR2(150) NOT NULL,
                EMAIL VARCHAR2(150) NOT NULL UNIQUE,
                SENHA_HASH VARCHAR2(255) NOT NULL,
                PAPEL VARCHAR2(20) NOT NULL CHECK (PAPEL IN ('SOMPO','GESTOR','OPERADOR')),
                GESTOR_ID NUMBER,
                TIPO_COBERTURA VARCHAR2(20),
                ATIVO NUMBER(1) DEFAULT 1 NOT NULL,
                CRIADO_EM TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                CONSTRAINT FK_USUARIO_GESTOR FOREIGN KEY (GESTOR_ID) REFERENCES TB_USUARIO(ID_USUARIO)
            """,

            "TB_FAZENDA": """
                ID_FAZENDA NUMBER GENERATED ALWAYS AS IDENTITY PRIMARY KEY,
                GESTOR_ID NUMBER NOT NULL,
                NOME VARCHAR2(150) NOT NULL,
                LATITUDE NUMBER,
                LONGITUDE NUMBER,
                ENDERECO VARCHAR2(255),
                CRIADO_EM TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                CONSTRAINT FK_FAZENDA_GESTOR FOREIGN KEY (GESTOR_ID) REFERENCES TB_USUARIO(ID_USUARIO)
            """,

            "TB_MAQUINA": """
                ID_MAQUINA NUMBER GENERATED ALWAYS AS IDENTITY PRIMARY KEY,
                EQUIPAMENTO_ID VARCHAR2(20) NOT NULL UNIQUE,
                FAZENDA_ID NUMBER,
                TIPO VARCHAR2(50),
                MODELO VARCHAR2(100),
                ANO NUMBER(4),
                STATUS VARCHAR2(20) DEFAULT 'ATIVA' NOT NULL CHECK (STATUS IN ('ATIVA','INATIVA')),
                CRIADO_POR NUMBER,
                LATITUDE NUMBER,
                LONGITUDE NUMBER,
                DATA_ULTIMA_MANUTENCAO DATE,
                CRIADO_EM TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                CONSTRAINT FK_MAQUINA_FAZENDA FOREIGN KEY (FAZENDA_ID) REFERENCES TB_FAZENDA(ID_FAZENDA),
                CONSTRAINT FK_MAQUINA_CRIADOR FOREIGN KEY (CRIADO_POR) REFERENCES TB_USUARIO(ID_USUARIO)
            """,

            "TB_MAQUINA_OPERADOR": """
                MAQUINA_ID NUMBER NOT NULL,
                OPERADOR_ID NUMBER NOT NULL,
                CRIADO_EM TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                CONSTRAINT PK_MAQUINA_OPERADOR PRIMARY KEY (MAQUINA_ID, OPERADOR_ID),
                CONSTRAINT FK_MO_MAQUINA FOREIGN KEY (MAQUINA_ID) REFERENCES TB_MAQUINA(ID_MAQUINA),
                CONSTRAINT FK_MO_OPERADOR FOREIGN KEY (OPERADOR_ID) REFERENCES TB_USUARIO(ID_USUARIO)
            """,

            "TB_MANUTENCAO": """
                ID_MANUTENCAO NUMBER GENERATED ALWAYS AS IDENTITY PRIMARY KEY,
                MAQUINA_ID NUMBER NOT NULL,
                SOLICITADO_POR NUMBER,
                DATA_MANUTENCAO DATE,
                DESCRICAO VARCHAR2(2000),
                TIPO VARCHAR2(20) CHECK (TIPO IN ('PREVENTIVA','CORRETIVA')),
                TOKEN_LINK VARCHAR2(64) UNIQUE,
                TOKEN_EXPIRA_EM TIMESTAMP,
                STATUS VARCHAR2(20) DEFAULT 'SOLICITADA' NOT NULL CHECK (STATUS IN ('SOLICITADA','CONCLUIDA')),
                CRIADO_EM TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                CONCLUIDO_EM TIMESTAMP,
                CONSTRAINT FK_MANUT_MAQUINA FOREIGN KEY (MAQUINA_ID) REFERENCES TB_MAQUINA(ID_MAQUINA),
                CONSTRAINT FK_MANUT_SOLICITANTE FOREIGN KEY (SOLICITADO_POR) REFERENCES TB_USUARIO(ID_USUARIO)
            """,

            "TB_TICKET": """
                ID_TICKET NUMBER GENERATED ALWAYS AS IDENTITY PRIMARY KEY,
                MAQUINA_ID NUMBER NOT NULL,
                OPERADOR_ID NUMBER NOT NULL,
                CATEGORIA VARCHAR2(50),
                OBSERVACAO VARCHAR2(2000),
                STATUS VARCHAR2(20) DEFAULT 'ABERTO' NOT NULL CHECK (STATUS IN ('ABERTO','RESOLVIDO')),
                CRIADO_EM TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                RESOLVIDO_EM TIMESTAMP,
                CONSTRAINT FK_TICKET_MAQUINA FOREIGN KEY (MAQUINA_ID) REFERENCES TB_MAQUINA(ID_MAQUINA),
                CONSTRAINT FK_TICKET_OPERADOR FOREIGN KEY (OPERADOR_ID) REFERENCES TB_USUARIO(ID_USUARIO)
            """
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
            ("TB_PREVISAO_RISCO", "EXPLICACAO", "VARCHAR2(4000)"),
            ("TB_PREVISAO_RISCO", "ID_PREVISAO", "NUMBER GENERATED ALWAYS AS IDENTITY"),
            ("TB_RISCO_AGRICOLA_TRATADO", "ID_TELEMETRIA", "NUMBER GENERATED ALWAYS AS IDENTITY"),
            ("TB_RISCO_AGRICOLA", "ID_REGISTRO", "NUMBER GENERATED ALWAYS AS IDENTITY")
        ]

        for tab, col, tipo in colunas_novas:
            if not coluna_existe(cursor, tab, col):
                print(f"Migração: Adicionando {col} em {tab}...")
                cursor.execute(f"ALTER TABLE {tab} ADD {col} {tipo}")

        pk_alvo = {
            "TB_PREVISAO_RISCO": "ID_PREVISAO",
            "TB_RISCO_AGRICOLA_TRATADO": "ID_TELEMETRIA",
            "TB_RISCO_AGRICOLA": "ID_REGISTRO"
        }

        for tab, id_col in pk_alvo.items():
            pk_atual = obter_colunas_pk(cursor, tab)
            if pk_atual != [id_col]:
                print(f"Migração de chave primária: {tab} -> {id_col}")
                try:
                    cursor.execute(f"ALTER TABLE {tab} DROP PRIMARY KEY")
                except oracledb.DatabaseError:
                    pass
                cursor.execute(f"ALTER TABLE {tab} ADD PRIMARY KEY ({id_col})")

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