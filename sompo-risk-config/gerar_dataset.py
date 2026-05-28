import random
from pathlib import Path

import pandas as pd
from api_clima import buscar_clima_historico_intervalo, buscar_coordenadas


def classificar_risco(
    chuva_mm,
    umidade_solo,
    velocidade_kmh,
    proximidade_agua_m,
    inclinacao_graus,
    manutencao_dias
):
    pontos = 0

    if chuva_mm > 30:
        pontos += 2

    if umidade_solo > 70:
        pontos += 2

    if velocidade_kmh > 18:
        pontos += 2

    if proximidade_agua_m < 100:
        pontos += 2

    if inclinacao_graus > 15:
        pontos += 2

    if manutencao_dias > 90:
        pontos += 2

    if pontos >= 8:
        return "alto"
    elif pontos >= 4:
        return "medio"

    return "baixo"


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

            risco = classificar_risco(
                chuva_mm,
                umidade_solo,
                velocidade_kmh,
                proximidade_agua_m,
                inclinacao_graus,
                manutencao_dias
            )

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
                "risco": risco
            })

            contador += 1

    return pd.DataFrame(dados)


if __name__ == "__main__":
    pasta_csv = Path("./csvs")
    pasta_csv.mkdir(exist_ok=True)

    df = gerar_dataset()
    df.to_csv(pasta_csv / "dataset_risco_agricola.csv", index=False)

    print("Dataset criado com sucesso!")
    print(f"Total de registros: {len(df)}")
    print(df.head())

    print("\nDistribuição do risco:")
    print(df["risco"].value_counts())
