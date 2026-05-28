from pathlib import Path

import pandas as pd

CAMINHO_ENTRADA = Path("./csvs/dataset_risco_agricola.csv")
CAMINHO_SAIDA = Path("./csvs/dataset_tratado.csv")


def calcular_score_risco(row):
    score = 0

    if row["chuva_mm"] > 30:
        score += 20

    if row["umidade_solo"] > 70:
        score += 20

    if row["velocidade_kmh"] > 18:
        score += 20

    if row["proximidade_agua_m"] < 100:
        score += 20

    if row["inclinacao_graus"] > 15:
        score += 10

    if row["manutencao_dias"] > 90:
        score += 10

    return min(score, 100)


def classificar_por_score(score):
    if score >= 70:
        return "alto"
    elif score >= 40:
        return "medio"
    else:
        return "baixo"


def carregar_dataset():
    if not CAMINHO_ENTRADA.exists():
        raise FileNotFoundError(f"Arquivo não encontrado: {CAMINHO_ENTRADA}")

    return pd.read_csv(CAMINHO_ENTRADA)


def limpar_dados(df):
    df = df.copy()
    df = df.drop_duplicates()

    df["cidade"] = df["cidade"].astype(str).str.strip().str.title()
    df["risco"] = df["risco"].astype(str).str.strip().str.lower()

    df["data_medicao"] = pd.to_datetime(df["data_medicao"], errors="coerce")

    colunas_numericas = [
        "temperatura",
        "chuva_mm",
        "umidade_solo",
        "velocidade_kmh",
        "proximidade_agua_m",
        "inclinacao_graus",
        "tempo_uso_horas",
        "manutencao_dias"
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


def preparar_dataset():
    df = carregar_dataset()
    df = limpar_dados(df)

    df["score_risco"] = df.apply(calcular_score_risco, axis=1)
    df["classificacao_risco"] = df["score_risco"].apply(classificar_por_score)

    CAMINHO_SAIDA.parent.mkdir(exist_ok=True)
    df.to_csv(CAMINHO_SAIDA, index=False)

    return df


if __name__ == "__main__":
    df_tratado = preparar_dataset()

    print("Dataset tratado criado com sucesso!")
    print(df_tratado.head())
    print("\nDistribuição da classificação:")
    print(df_tratado["classificacao_risco"].value_counts())
