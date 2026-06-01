import os
import random

import oracledb
import pandas as pd
from api_clima import buscar_clima_historico_intervalo, buscar_coordenadas
from dotenv import load_dotenv

load_dotenv()


def validar_env():
    variaveis = [
        "ORACLE_USER",
        "ORACLE_PASSWORD",
        "ORACLE_HOST",
        "ORACLE_PORT",
        "ORACLE_SERVICE"
    ]

    for var in variaveis:
        if not os.getenv(var):
            raise ValueError(f"Variável de ambiente não encontrada: {var}")


def conectar_oracle():
    validar_env()

    return oracledb.connect(
        user=os.getenv("ORACLE_USER"),
        password=os.getenv("ORACLE_PASSWORD"),
        host=os.getenv("ORACLE_HOST", "oracle.fiap.com.br"),
        port=int(os.getenv("ORACLE_PORT", 1521)),
        service_name=os.getenv("ORACLE_SERVICE", "ORCL")
    )


def gerar_dataset():
    cidades = [
        "São Paulo",
        "Campinas",
        "Ribeirão Preto",
        "Sorocaba",
        "Piracicaba",
        "Araraquara",
        "São José dos Campos",
        "Ribeirão Pires",
        "Taquaritinga"
    ]

    dados = []
    contador = 1

    print("Baixando históricos climáticos...")

    for cidade in cidades:
        print(f"Buscando dados de {cidade}...")

        coords = buscar_coordenadas(cidade)

        if not coords:
            print(f"Coordenadas não encontradas para {cidade}. Pulando cidade.")
            continue

        historico = buscar_clima_historico_intervalo(
            coords["latitude"],
            coords["longitude"]
        )

        if not historico:
            print(f"Histórico climático não encontrado para {cidade}. Pulando cidade.")
            continue

        for clima in historico:
            temperatura = clima["temperatura"]
            chuva_mm = clima["chuva_mm"]
            data_medicao = clima["data"]

            umidade_solo = random.randint(20, 100)
            velocidade_kmh = round(random.uniform(5, 30), 1)
            proximidade_agua_m = random.randint(20, 1000)
            inclinacao_graus = round(random.uniform(0, 30), 1)
            tempo_uso_horas = random.randint(1, 12)
            manutencao_dias = random.randint(1, 180)

            dados.append({
                "equipamento_id": f"EQUIP{contador:05d}",
                "cidade": cidade,
                "data_medicao": data_medicao,
                "temperatura": temperatura,
                "chuva_mm": chuva_mm,
                "umidade_solo": umidade_solo,
                "velocidade_kmh": velocidade_kmh,
                "proximidade_agua_m": proximidade_agua_m,
                "inclinacao_graus": inclinacao_graus,
                "tempo_uso_horas": tempo_uso_horas,
                "manutencao_dias": manutencao_dias,
                "indicador_chuva_alta": int(chuva_mm > 30),
                "indicador_solo_umido": int(umidade_solo > 70),
                "indicador_velocidade_alta": int(velocidade_kmh > 18),
                "indicador_perto_agua": int(proximidade_agua_m < 100),
                "indicador_inclinacao_alta": int(inclinacao_graus > 15),
                "indicador_manutencao_atrasada": int(manutencao_dias > 90)
            })

            contador += 1

    return pd.DataFrame(dados)


def inserir_no_banco(df):
    conn = conectar_oracle()
    cursor = conn.cursor()

    sql = """
        INSERT INTO TB_RISCO_AGRICOLA (
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
            TO_DATE(:3, 'YYYY-MM-DD'),
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

        print("\nDados inseridos com sucesso no Oracle!")
        print(f"Total de registros inseridos: {len(df)}")

    except Exception as erro:
        conn.rollback()
        print(f"Erro ao inserir dados no banco: {erro}")

    finally:
        cursor.close()
        conn.close()


if __name__ == "__main__":
    try:
        df = gerar_dataset()

        print("\nDataset criado com sucesso!")
        print(f"Total de registros gerados: {len(df)}")
        print("\nPrimeiros registros:")
        print(df.head())

        inserir_no_banco(df)

    except Exception as erro:
        print(f"Erro geral na execução: {erro}")
