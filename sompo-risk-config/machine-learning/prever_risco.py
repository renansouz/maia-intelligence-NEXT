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
    "equipamento_id": dados.get("equipamento_id"),
    "cidade": dados.get("cidade"),
    "data_medicao": dados.get("data_medicao"),
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

def buscar_todos_registros():
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
            MANUTENCAO_DIAS
        FROM TB_RISCO_AGRICOLA_TRATADO
    """

    df = pd.read_sql(query, conn)

    conn.close()

    return df


def salvar_previsao(resultado):
    conn = conectar_oracle()
    cursor = conn.cursor()

    cursor.execute(
        """
        INSERT INTO TB_PREVISAO_RISCO (
            EQUIPAMENTO_ID,
            CIDADE,
            DATA_MEDICAO,
            DATA_PREVISAO,
            RISCO_PREVISTO,
            CLASSIFICACAO,
            PROBABILIDADE_BAIXO,
            PROBABILIDADE_ALTO,
            MODELO_UTILIZADO
        )
        VALUES (
            :1,
            :2,
            :3,
            SYSDATE,
            :4,
            :5,
            :6,
            :7,
            'DecisionTreeClassifier'
        )
        """,
        (
            resultado["equipamento_id"],
            resultado["cidade"],
            resultado["data_medicao"],
            resultado["risco_previsto"],
            resultado["classificacao"],
            resultado["probabilidades"].get(0, 0),
            resultado["probabilidades"].get(1, 0)
        )
    )

    conn.commit()

    cursor.close()
    conn.close()

if __name__ == "__main__":

    modelo, features = carregar_modelo()

    conn = conectar_oracle()
    cursor = conn.cursor()

    print("Limpando tabela de previsões...")

    cursor.execute("DELETE FROM TB_PREVISAO_RISCO")
    conn.commit()

    print("Buscando registros...")

    df = buscar_todos_registros()

    print(f"Total de registros encontrados: {len(df)}")

    inserts = []

    for i, (_, row) in enumerate(df.iterrows(), start=1):

        if i % 100 == 0:
            print(f"Processados {i} registros")

        dados = {
            "equipamento_id": row["EQUIPAMENTO_ID"],
            "cidade": row["CIDADE"],
            "data_medicao": pd.to_datetime(row["DATA_MEDICAO"]),
            "temperatura": row["TEMPERATURA"],
            "chuva_mm": row["CHUVA_MM"],
            "umidade_solo": row["UMIDADE_SOLO"],
            "velocidade_kmh": row["VELOCIDADE_KMH"],
            "proximidade_agua_m": row["PROXIMIDADE_AGUA_M"],
            "inclinacao_graus": row["INCLINACAO_GRAUS"],
            "tempo_uso_horas": row["TEMPO_USO_HORAS"],
            "manutencao_dias": row["MANUTENCAO_DIAS"]
        }

        dados["ano"] = dados["data_medicao"].year
        dados["mes"] = dados["data_medicao"].month
        dados["dia"] = dados["data_medicao"].day
        dados["dia_semana"] = dados["data_medicao"].dayofweek

        dados = criar_indicadores(dados)

        df_pred = pd.DataFrame([dados])

        for feature in features:
            if feature not in df_pred.columns:
                df_pred[feature] = 0

        X = df_pred[features]

        risco_numerico = int(modelo.predict(X)[0])

        classificacao = (
            "alto"
            if risco_numerico == 1
            else "baixo"
        )

        probabilidades = modelo.predict_proba(X)[0]
        classes = modelo.classes_

        prob_dict = {
            int(classe): float(prob)
            for classe, prob in zip(classes, probabilidades)
        }

        inserts.append(
            (
                dados["equipamento_id"],
                dados["cidade"],
                dados["data_medicao"],
                risco_numerico,
                classificacao,
                prob_dict.get(0, 0),
                prob_dict.get(1, 0)
            )
        )

    print("Gravando previsões no Oracle...")

    cursor.executemany(
        """
        INSERT INTO TB_PREVISAO_RISCO (
            EQUIPAMENTO_ID,
            CIDADE,
            DATA_MEDICAO,
            DATA_PREVISAO,
            RISCO_PREVISTO,
            CLASSIFICACAO,
            PROBABILIDADE_BAIXO,
            PROBABILIDADE_ALTO,
            MODELO_UTILIZADO
        )
        VALUES (
            :1,
            :2,
            :3,
            SYSDATE,
            :4,
            :5,
            :6,
            :7,
            'DecisionTreeClassifier'
        )
        """,
        inserts
    )

    conn.commit()

    cursor.close()
    conn.close()

    print(f"Finalizado. {len(inserts)} previsões gravadas.")
