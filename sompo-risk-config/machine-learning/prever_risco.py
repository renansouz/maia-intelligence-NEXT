import os
from pathlib import Path

import joblib
import oracledb
import pandas as pd
from dotenv import load_dotenv

load_dotenv()

CAMINHO_MODELO = Path("./models/arvore_decisao.pkl")
CAMINHO_FEATURES = Path("./models/features.pkl")

CIDADES_VALIDAS = [
    "São Paulo",
    "Campinas",
    "Ribeirão Preto",
    "Sorocaba",
    "Piracicaba",
    "Araraquara",
    "São José Dos Campos",
    "Ribeirão Pires",
    "Taquaritinga"
]


def conectar_oracle():
    return oracledb.connect(
        user=os.getenv("ORACLE_USER"),
        password=os.getenv("ORACLE_PASSWORD"),
        host=os.getenv("ORACLE_HOST", "oracle.fiap.com.br"),
        port=int(os.getenv("ORACLE_PORT", 1521)),
        service_name=os.getenv("ORACLE_SERVICE", "ORCL")
    )


def carregar_modelo():
    if not CAMINHO_MODELO.exists():
        raise FileNotFoundError(
            "Modelo não encontrado. Execute treinar_arvore.py primeiro."
        )

    if not CAMINHO_FEATURES.exists():
        raise FileNotFoundError(
            "Arquivo de features não encontrado. Execute treinar_arvore.py primeiro."
        )

    modelo = joblib.load(CAMINHO_MODELO)
    features = joblib.load(CAMINHO_FEATURES)

    return modelo, features


def validar_cidade(cidade):
    cidade_formatada = cidade.strip().title()

    if cidade_formatada not in CIDADES_VALIDAS:
        raise ValueError(
            f"Cidade inválida: {cidade}. "
            f"Cidades disponíveis: {', '.join(CIDADES_VALIDAS)}"
        )

    return cidade_formatada


def buscar_ultimo_registro_cidade(cidade):
    cidade = validar_cidade(cidade)

    conn = conectar_oracle()
    cursor = conn.cursor()

    query = """
        SELECT
            CIDADE,
            DATA_MEDICAO,
            TEMPERATURA,
            CHUVA_MM,
            UMIDADE_SOLO,
            VELOCIDADE_KMH,
            PROXIMIDADE_AGUA_M,
            INCLINACAO_GRAUS,
            TEMPO_USO_HORAS,
            MANUTENCAO_DIAS
        FROM TB_RISCO_AGRICOLA_TRATADO
        WHERE CIDADE = :cidade
        ORDER BY DATA_MEDICAO DESC
        FETCH FIRST 1 ROW ONLY
    """

    cursor.execute(query, cidade=cidade)
    resultado = cursor.fetchone()

    cursor.close()
    conn.close()

    if not resultado:
        raise ValueError(f"Nenhum registro encontrado para a cidade: {cidade}")

    colunas = [
        "cidade",
        "data_medicao",
        "temperatura",
        "chuva_mm",
        "umidade_solo",
        "velocidade_kmh",
        "proximidade_agua_m",
        "inclinacao_graus",
        "tempo_uso_horas",
        "manutencao_dias"
    ]

    dados = dict(zip(colunas, resultado))
    dados["data_medicao"] = pd.to_datetime(dados["data_medicao"])

    dados["ano"] = dados["data_medicao"].year
    dados["mes"] = dados["data_medicao"].month
    dados["dia"] = dados["data_medicao"].day
    dados["dia_semana"] = dados["data_medicao"].dayofweek

    return dados


def criar_indicadores(dados):
    dados["indicador_chuva_alta"] = int(dados["chuva_mm"] > 30)
    dados["indicador_solo_umido"] = int(dados["umidade_solo"] > 70)
    dados["indicador_velocidade_alta"] = int(dados["velocidade_kmh"] > 18)
    dados["indicador_perto_agua"] = int(dados["proximidade_agua_m"] < 100)
    dados["indicador_inclinacao_alta"] = int(dados["inclinacao_graus"] > 15)
    dados["indicador_manutencao_atrasada"] = int(dados["manutencao_dias"] > 90)

    return dados


def traduzir_classificacao(risco):
    if risco == 1:
        return "alto"

    return "baixo"


def prever_risco_por_dados(dados_entrada):
    modelo, features = carregar_modelo()

    dados = criar_indicadores(dados_entrada.copy())

    df = pd.DataFrame([dados])

    for feature in features:
        if feature not in df.columns:
            df[feature] = 0

    X = df[features]

    risco_numerico = int(modelo.predict(X)[0])
    classificacao = traduzir_classificacao(risco_numerico)

    probabilidades = modelo.predict_proba(X)[0]
    classes = modelo.classes_

    probabilidades_dict = {
        int(classe): round(float(prob), 4)
        for classe, prob in zip(classes, probabilidades)
    }

    return {
        "cidade": dados.get("cidade"),
        "data_medicao": str(dados.get("data_medicao")),
        "risco_previsto": risco_numerico,
        "classificacao": classificacao,
        "probabilidades": probabilidades_dict,
        "interpretacao": {
            "0": "baixo",
            "1": "alto"
        }
    }


def prever_risco_por_cidade(cidade):
    dados = buscar_ultimo_registro_cidade(cidade)
    return prever_risco_por_dados(dados)


if __name__ == "__main__":
    cidade = "Araraquara"

    resultado = prever_risco_por_cidade(cidade)

    print("Resultado da previsão:")
    print(resultado)
