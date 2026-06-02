import os
import random

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


def carregar_dataset_tratado():
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
        FROM TB_RISCO_AGRICOLA_TRATADO
    """

    df = pd.read_sql(query, conn)
    conn.close()

    df.columns = df.columns.str.lower()

    return df


def criar_variavel_alvo(df):
    df = df.copy()

    indicadores = [
        "indicador_chuva_alta",
        "indicador_solo_umido",
        "indicador_velocidade_alta",
        "indicador_perto_agua",
        "indicador_inclinacao_alta",
        "indicador_manutencao_atrasada"
    ]

    df["total_indicadores"] = df[indicadores].sum(axis=1)

    def gerar_ocorrencia(row):
        total = row["total_indicadores"]

        if total >= 4:
            probabilidade = 0.75
        elif total >= 2:
            probabilidade = 0.35
        else:
            probabilidade = 0.08

        return int(random.random() < probabilidade)

    df["ocorrencia_risco"] = df.apply(gerar_ocorrencia, axis=1)

    return df


def preparar_features():
    df = carregar_dataset_tratado()

    df["data_medicao"] = pd.to_datetime(df["data_medicao"], errors="coerce")

    df["ano"] = df["data_medicao"].dt.year
    df["mes"] = df["data_medicao"].dt.month
    df["dia"] = df["data_medicao"].dt.day
    df["dia_semana"] = df["data_medicao"].dt.dayofweek

    df = criar_variavel_alvo(df)

    features = [
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
        "indicador_manutencao_atrasada",
        "ano",
        "mes",
        "dia",
        "dia_semana"
    ]

    X = df[features]
    y = df["ocorrencia_risco"]

    return X, y, features, df


if __name__ == "__main__":
    X, y, features, df = preparar_features()

    print("Features preparadas com sucesso!")
    print(X.head())
    print("\nDistribuição do alvo:")
    print(y.value_counts())
