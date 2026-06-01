import os

import oracledb
import pandas as pd
from dotenv import load_dotenv

load_dotenv()


def conectar_oracle():
    return oracledb.connect(
        user=os.getenv("ORACLE_USER"),
        password=os.getenv("ORACLE_PASSWORD"),
        host=os.getenv("ORACLE_HOST", "oracle.fiap.com.br"),
        port=int(os.getenv("ORACLE_PORT", 1521)),
        service_name=os.getenv("ORACLE_SERVICE", "ORCL")
    )


def carregar_dataset_banco():
    conn = conectar_oracle()

    query = """
        SELECT
            EQUIPAMENTO_ID,
            CIDADE,
            DATA_MEDICAO,
            TEMPERATURA,
            CHUVA_MM,
            UMIDADE_SOLO,
            VELOCIDADE_KMH,
            PROXIMIDADE_AGUA_M,
            INCLINACAO_GRAUS,
            TEMPO_USO_HORAS,
            MANUTENCAO_DIAS,
            INDICADOR_CHUVA_ALTA,
            INDICADOR_SOLO_UMIDO,
            INDICADOR_VELOCIDADE_ALTA,
            INDICADOR_PERTO_AGUA,
            INDICADOR_INCLINACAO_ALTA,
            INDICADOR_MANUTENCAO_ATRASADA
        FROM TB_RISCO_AGRICOLA
    """

    df = pd.read_sql(query, conn)
    conn.close()

    return df


def limpar_dados(df):
    df = df.copy()
    df = df.drop_duplicates()

    df.columns = df.columns.str.lower()

    df["cidade"] = df["cidade"].astype(str).str.strip().str.title()
    df["data_medicao"] = pd.to_datetime(df["data_medicao"], errors="coerce")

    colunas_numericas = [
        "temperatura",
        "chuva_mm",
        "umidade_solo",
        "velocidade_kmh",
        "proximidade_agua_m",
        "inclinacao_graus",
        "tempo_uso_horas",
        "manutencao_dias",
        "indicador_chuva_alta",
        "indicador_solo_umido",
        "indicador_velocidade_alta",
        "indicador_perto_agua",
        "indicador_inclinacao_alta",
        "indicador_manutencao_atrasada"
    ]

    for coluna in colunas_numericas:
        df[coluna] = pd.to_numeric(df[coluna], errors="coerce")

    df = df.dropna(subset=colunas_numericas + ["data_medicao"])

    df = df[df["temperatura"].between(-10, 60)]
    df = df[df["chuva_mm"].between(0, 300)]
    df = df[df["umidade_solo"].between(0, 100)]
    df = df[df["velocidade_kmh"].between(0, 100)]
    df = df[df["proximidade_agua_m"].between(0, 5000)]
    df = df[df["inclinacao_graus"].between(0, 90)]
    df = df[df["tempo_uso_horas"].between(0, 24)]
    df = df[df["manutencao_dias"].between(0, 365)]

    return df


def salvar_dataset_tratado_banco(df):
    conn = conectar_oracle()
    cursor = conn.cursor()

    cursor.execute("DELETE FROM TB_RISCO_AGRICOLA_TRATADO")

    sql = """
        INSERT INTO TB_RISCO_AGRICOLA_TRATADO (
            EQUIPAMENTO_ID,
            CIDADE,
            DATA_MEDICAO,
            TEMPERATURA,
            CHUVA_MM,
            UMIDADE_SOLO,
            VELOCIDADE_KMH,
            PROXIMIDADE_AGUA_M,
            INCLINACAO_GRAUS,
            TEMPO_USO_HORAS,
            MANUTENCAO_DIAS,
            INDICADOR_CHUVA_ALTA,
            INDICADOR_SOLO_UMIDO,
            INDICADOR_VELOCIDADE_ALTA,
            INDICADOR_PERTO_AGUA,
            INDICADOR_INCLINACAO_ALTA,
            INDICADOR_MANUTENCAO_ATRASADA
        )
        VALUES (
            :1,
            :2,
            :3,
            :4,
            :5,
            :6,
            :7,
            :8,
            :9,
            :10,
            :11,
            :12,
            :13,
            :14,
            :15,
            :16,
            :17
        )
    """

    dados_insert = [
        (
            row["equipamento_id"],
            row["cidade"],
            row["data_medicao"],
            row["temperatura"],
            row["chuva_mm"],
            row["umidade_solo"],
            row["velocidade_kmh"],
            row["proximidade_agua_m"],
            row["inclinacao_graus"],
            row["tempo_uso_horas"],
            row["manutencao_dias"],
            row["indicador_chuva_alta"],
            row["indicador_solo_umido"],
            row["indicador_velocidade_alta"],
            row["indicador_perto_agua"],
            row["indicador_inclinacao_alta"],
            row["indicador_manutencao_atrasada"]
        )
        for _, row in df.iterrows()
    ]

    try:
        cursor.executemany(sql, dados_insert)
        conn.commit()
        print("Dataset tratado salvo no banco com sucesso!")
        print(f"Total de registros tratados: {len(df)}")

    except Exception as erro:
        conn.rollback()
        print(f"Erro ao salvar dataset tratado: {erro}")

    finally:
        cursor.close()
        conn.close()


def preparar_dataset():
    df = carregar_dataset_banco()
    df_tratado = limpar_dados(df)
    salvar_dataset_tratado_banco(df_tratado)

    return df_tratado


if __name__ == "__main__":
    df_tratado = preparar_dataset()

    print("\nPrimeiros registros tratados:")
    print(df_tratado.head())
