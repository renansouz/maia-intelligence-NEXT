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

def garantir_fk_maquina_gestor(cursor):
    cursor.execute("""
        SELECT COUNT(*) FROM user_constraints
        WHERE table_name = 'TB_MAQUINA' AND constraint_name = 'FK_MAQUINA_GESTOR'
    """)
    if cursor.fetchone()[0] == 0:
        print("Migração: Adicionando FK_MAQUINA_GESTOR...")
        cursor.execute("""
            ALTER TABLE TB_MAQUINA
            ADD CONSTRAINT FK_MAQUINA_GESTOR FOREIGN KEY (GESTOR_ID) REFERENCES TB_USUARIO(ID_USUARIO)
        """)
    

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
                PAPEL VARCHAR2(20) NOT NULL CHECK (PAPEL IN ('seguradora','GESTOR','OPERADOR')),
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
            """,

            "TB_ML_DATASET": """
                ID_DATASET NUMBER GENERATED ALWAYS AS IDENTITY PRIMARY KEY,
                CODIGO VARCHAR2(50) NOT NULL UNIQUE,
                NOME VARCHAR2(200) NOT NULL,
                FONTE VARCHAR2(500),
                FREQUENCIA_HZ NUMBER,
                TIPO_DADO VARCHAR2(30) NOT NULL,
                CRIADO_EM TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            """,

            "TB_ML_SESSAO": """
                ID_SESSAO NUMBER GENERATED ALWAYS AS IDENTITY PRIMARY KEY,
                DATASET_ID NUMBER NOT NULL,
                IDENTIFICADOR VARCHAR2(120) NOT NULL,
                OPERACAO VARCHAR2(100),
                IMPLEMENTO VARCHAR2(150),
                ARQUIVO_ORIGEM VARCHAR2(500) NOT NULL,
                HASH_ARQUIVO VARCHAR2(64),
                TOTAL_LINHAS NUMBER,
                CRIADO_EM TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                CONSTRAINT FK_ML_SESSAO_DATASET FOREIGN KEY (DATASET_ID) REFERENCES TB_ML_DATASET(ID_DATASET),
                CONSTRAINT UK_ML_SESSAO UNIQUE (DATASET_ID, IDENTIFICADOR)
            """,

            "TB_ML_TELEMETRIA": """
                ID_AMOSTRA NUMBER GENERATED ALWAYS AS IDENTITY PRIMARY KEY,
                SESSAO_ID NUMBER NOT NULL,
                LINHA_ORIGEM NUMBER NOT NULL,
                TIMESTAMP_ORIGEM TIMESTAMP,
                TEMPO_MS NUMBER,
                TEMP_COOLANT_C NUMBER,
                TEMP_OLEO_C NUMBER,
                TEMP_AMBIENTE_C NUMBER,
                TEMP_ADMISSAO_C NUMBER,
                PRESSAO_OLEO_KPA NUMBER,
                TORQUE_PCT NUMBER,
                CARGA_MOTOR_PCT NUMBER,
                RPM NUMBER,
                COMBUSTIVEL_L_H NUMBER,
                VELOCIDADE_KMH NUMBER,
                VENTOINHA_PCT NUMBER,
                POSICAO_ENGATE_PCT NUMBER,
                DRAFT1_PCT NUMBER,
                DRAFT2_PCT NUMBER,
                TRACAO_4X4 NUMBER(1),
                PTO_STATUS NUMBER(1),
                IMPLEMENTO_CODIGO VARCHAR2(30),
                ESTADO_OPERACIONAL VARCHAR2(30),
                ANOMALIA_SINTETICA VARCHAR2(80),
                RISCO_SCORE NUMBER,
                CLASSIFICACAO_RISCO VARCHAR2(20),
                MOTIVOS_RISCO VARCHAR2(1000),
                CRIADO_EM TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                CONSTRAINT FK_ML_TELEMETRIA_SESSAO FOREIGN KEY (SESSAO_ID) REFERENCES TB_ML_SESSAO(ID_SESSAO),
                CONSTRAINT UK_ML_TELEMETRIA_LINHA UNIQUE (SESSAO_ID, LINHA_ORIGEM)
            """,

            "TB_ML_AMBIENTAL": """
                ID_AMBIENTAL NUMBER GENERATED ALWAYS AS IDENTITY PRIMARY KEY,
                FONTE VARCHAR2(30) NOT NULL,
                DATA_OBSERVACAO DATE NOT NULL,
                LATITUDE NUMBER,
                LONGITUDE NUMBER,
                FEATURES_JSON CLOB NOT NULL,
                HASH_REGISTRO VARCHAR2(64) NOT NULL UNIQUE,
                CRIADO_EM TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            """
        }

        for nome, campos in tabelas.items():
            try:
                cursor.execute(f"CREATE TABLE {nome} ({campos})")
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
            ("TB_RISCO_AGRICOLA", "ID_REGISTRO", "NUMBER GENERATED ALWAYS AS IDENTITY"),
            ("TB_MAQUINA", "GESTOR_ID", "NUMBER"),
            ("TB_MAQUINA", "VALOR_SEGURADO", "NUMBER(12,2)"),
            ("TB_FAZENDA", "CIDADE", "VARCHAR2(100)"),
            ("TB_TICKET", "ESCALADO_EM", "TIMESTAMP"),

            ("TB_RISCO_AGRICOLA_TRATADO", "TEMP_COOLANT", "NUMBER"),
            ("TB_RISCO_AGRICOLA_TRATADO", "TEMP_OLEO", "NUMBER"),
            ("TB_RISCO_AGRICOLA_TRATADO", "PRESSAO_OLEO", "NUMBER"),
            ("TB_RISCO_AGRICOLA_TRATADO", "TORQUE_PCT", "NUMBER"),
            ("TB_RISCO_AGRICOLA_TRATADO", "RPM", "NUMBER"),
            ("TB_RISCO_AGRICOLA_TRATADO", "COMBUSTIVEL_L_H", "NUMBER"),
        ]

        colunas_ml_contexto = [
            ("TB_ML_TELEMETRIA", "POSICAO_ENGATE_PCT", "NUMBER"),
            ("TB_ML_TELEMETRIA", "DRAFT1_PCT", "NUMBER"),
            ("TB_ML_TELEMETRIA", "DRAFT2_PCT", "NUMBER"),
            ("TB_ML_TELEMETRIA", "TRACAO_4X4", "NUMBER(1)"),
            ("TB_ML_TELEMETRIA", "PTO_STATUS", "NUMBER(1)"),
            ("TB_ML_TELEMETRIA", "IMPLEMENTO_CODIGO", "VARCHAR2(30)"),
            ("TB_ML_TELEMETRIA", "RISCO_SCORE", "NUMBER"),
            ("TB_ML_TELEMETRIA", "CLASSIFICACAO_RISCO", "VARCHAR2(20)"),
            ("TB_ML_TELEMETRIA", "MOTIVOS_RISCO", "VARCHAR2(1000)"),
        ]
        colunas_novas.extend(colunas_ml_contexto)

        for tab, col, tipo in colunas_novas:
            if not coluna_existe(cursor, tab, col):
                print(f"Migração: Adicionando {col} em {tab}...")
                cursor.execute(f"ALTER TABLE {tab} ADD {col} {tipo}")

        garantir_fk_maquina_gestor(cursor)
        garantir_status_ticket_atualizado(cursor)


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

        indices = [
            ("IX_ML_SESSAO_DATASET", "TB_ML_SESSAO(DATASET_ID)"),
            ("IX_ML_TELEMETRIA_SESSAO", "TB_ML_TELEMETRIA(SESSAO_ID)"),
            ("IX_ML_TELEMETRIA_TEMPO", "TB_ML_TELEMETRIA(TIMESTAMP_ORIGEM)"),
            ("IX_ML_TELEMETRIA_COOLANT", "TB_ML_TELEMETRIA(TEMP_COOLANT_C)"),
            ("IX_ML_TELEMETRIA_RISCO", "TB_ML_TELEMETRIA(CLASSIFICACAO_RISCO)"),
            ("IX_ML_AMBIENTAL_DATA", "TB_ML_AMBIENTAL(DATA_OBSERVACAO)"),
        ]

        for nome_indice, alvo in indices:
            try:
                cursor.execute(f"CREATE INDEX {nome_indice} ON {alvo}")
            except oracledb.DatabaseError as e:
                if "ORA-00955" not in str(e) and "ORA-01408" not in str(e):
                    raise

        views = {
            "VW_ML_TELEMETRIA_ALINHADA": """
                SELECT
                    d.CODIGO AS DATASET,
                    d.NOME AS DATASET_NOME,
                    s.IDENTIFICADOR AS SESSAO,
                    s.OPERACAO,
                    s.IMPLEMENTO,
                    s.ARQUIVO_ORIGEM,
                    t.ID_AMOSTRA,
                    t.LINHA_ORIGEM,
                    t.TIMESTAMP_ORIGEM,
                    t.TEMPO_MS,
                    t.TEMP_COOLANT_C,
                    t.TEMP_OLEO_C,
                    t.TEMP_AMBIENTE_C,
                    t.TEMP_ADMISSAO_C,
                    t.PRESSAO_OLEO_KPA,
                    t.TORQUE_PCT,
                    t.CARGA_MOTOR_PCT,
                    t.RPM,
                    t.COMBUSTIVEL_L_H,
                    t.VELOCIDADE_KMH,
                    t.VENTOINHA_PCT,
                    t.POSICAO_ENGATE_PCT,
                    t.DRAFT1_PCT,
                    t.DRAFT2_PCT,
                    t.TRACAO_4X4,
                    t.PTO_STATUS,
                    t.IMPLEMENTO_CODIGO,
                    t.ESTADO_OPERACIONAL,
                    t.ANOMALIA_SINTETICA,
                    t.RISCO_SCORE,
                    t.CLASSIFICACAO_RISCO,
                    t.MOTIVOS_RISCO
                FROM TB_ML_TELEMETRIA t
                JOIN TB_ML_SESSAO s ON s.ID_SESSAO = t.SESSAO_ID
                JOIN TB_ML_DATASET d ON d.ID_DATASET = s.DATASET_ID
            """,
            "VW_ML_RESUMO_SESSAO": """
                SELECT
                    d.CODIGO AS DATASET,
                    s.IDENTIFICADOR AS SESSAO,
                    s.OPERACAO,
                    s.IMPLEMENTO,
                    s.ARQUIVO_ORIGEM,
                    COUNT(t.ID_AMOSTRA) AS AMOSTRAS,
                    MIN(t.TIMESTAMP_ORIGEM) AS PRIMEIRO_TIMESTAMP,
                    MAX(t.TIMESTAMP_ORIGEM) AS ULTIMO_TIMESTAMP,
                    MIN(t.TEMP_COOLANT_C) AS COOLANT_MIN_C,
                    MAX(t.TEMP_COOLANT_C) AS COOLANT_MAX_C,
                    AVG(t.TEMP_COOLANT_C) AS COOLANT_MEDIA_C,
                    AVG(t.TORQUE_PCT) AS TORQUE_MEDIO_PCT,
                    AVG(t.RPM) AS RPM_MEDIO
                FROM TB_ML_TELEMETRIA t
                JOIN TB_ML_SESSAO s ON s.ID_SESSAO = t.SESSAO_ID
                JOIN TB_ML_DATASET d ON d.ID_DATASET = s.DATASET_ID
                GROUP BY d.CODIGO, s.IDENTIFICADOR, s.OPERACAO,
                    s.IMPLEMENTO, s.ARQUIVO_ORIGEM
            """
        }

        for nome_view, consulta in views.items():
            try:
                cursor.execute(f"CREATE OR REPLACE VIEW {nome_view} AS {consulta}")
            except oracledb.DatabaseError as e:
                if "ORA-00955" not in str(e):
                    raise

        conn.commit()
        print("Infraestrutura de dados: Sincronizada.")

    except Exception as e:
        conn.rollback()
        print(f"Falha na sincronização de infraestrutura: {e}")
    finally:
        cursor.close()
        db.release_connection(conn)

def garantir_status_ticket_atualizado(cursor):
    cursor.execute("""
        SELECT COUNT(*) FROM user_constraints
        WHERE table_name = 'TB_TICKET' AND constraint_name = 'CK_TICKET_STATUS'
    """)
    if cursor.fetchone()[0] > 0:
        return

    cursor.execute("""
        SELECT constraint_name, search_condition FROM user_constraints
        WHERE table_name = 'TB_TICKET' AND constraint_type = 'C'
    """)
    for nome, condicao in cursor.fetchall():
        if condicao and 'STATUS' in condicao.upper() and 'ABERTO' in condicao.upper():
            print(f"Migração: removendo constraint antiga de status ({nome})...")
            cursor.execute(f"ALTER TABLE TB_TICKET DROP CONSTRAINT {nome}")

    print("Migração: adicionando ESCALADO_seguradora como status válido de ticket...")
    cursor.execute("""
        ALTER TABLE TB_TICKET
        ADD CONSTRAINT CK_TICKET_STATUS CHECK (STATUS IN ('ABERTO','RESOLVIDO','ESCALADO_seguradora'))
    """)

if __name__ == "__main__":
    configurar_banco()