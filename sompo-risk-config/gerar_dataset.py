import random
from pathlib import Path
import pandas as pd

from api_clima import buscar_coordenadas, buscar_clima_historico_intervalo


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


def gerar_dataset(qtd=300):
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

    cache_clima = {}

    print("Baixando históricos climáticos...")

    for cidade in cidades:
        coords = buscar_coordenadas(cidade)

        if coords:
            historico = buscar_clima_historico_intervalo(
                coords["latitude"],
                coords["longitude"]
            )
            cache_clima[cidade] = historico or []
        else:
            cache_clima[cidade] = []

    dados = []

    for i in range(1, qtd + 1):
        cidade = random.choice(cidades)

        historico = cache_clima[cidade]

        if historico:
            clima = random.choice(historico)
            temperatura = clima["temperatura"]
            chuva_mm = clima["chuva_mm"]
            data_medicao = clima["data"]
        else:
            temperatura = 25.0
            chuva_mm = random.uniform(0, 80)
            data_medicao = None

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
            "equipamento_id": f"EQUIP{i:03d}",
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

    return pd.DataFrame(dados)


if __name__ == "__main__":
    pasta_csv = Path("./csvs")
    pasta_csv.mkdir(exist_ok=True)

    df = gerar_dataset(300)
    df.to_csv(pasta_csv / "dataset_risco_agricola.csv", index=False)

    print(df.head())
