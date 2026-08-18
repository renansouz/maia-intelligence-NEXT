import requests
from datetime import date

def buscar_coordenadas(cidade):
    url = "https://geocoding-api.open-meteo.com/v1/search"
    params = {
        "name": cidade,
        "count": 1,
        "language": "pt",
        "format": "json"
    }

    try:
        resposta = requests.get(url, params=params, timeout=10)
        resposta.raise_for_status()
        dados = resposta.json()
    except requests.exceptions.RequestException as e:
        print(f"Erro na API de Geocoding ({cidade}): {e}")
        return None

    resultados = dados.get("results")
    if not resultados:
        return None

    local = resultados[0]
    return {
        "latitude": local["latitude"],
        "longitude": local["longitude"]
    }

def buscar_clima_historico_intervalo(latitude, longitude):
    hoje = date.today().isoformat()
    url = "https://archive-api.open-meteo.com/v1/archive"

    params = {
        "latitude": latitude,
        "longitude": longitude,
        "start_date": "2024-01-01",
        "end_date": hoje,
        "daily": "temperature_2m_mean,precipitation_sum",
        "timezone": "America/Sao_Paulo"
    }

    try:
        resposta = requests.get(url, params=params, timeout=30)
        resposta.raise_for_status()
        dados = resposta.json()
    except requests.exceptions.RequestException as e:
        print(f"Erro na API de Clima Historico: {e}")
        if hasattr(e.response, 'text'):
            print(f"Detalhe do erro: {e.response.text}")
        return None

    daily = dados.get("daily")
    if not daily:
        return None

    registros = []
    for data, temp, chuva in zip(
        daily["time"],
        daily["temperature_2m_mean"],
        daily["precipitation_sum"]
    ):
        registros.append({
            "data": data,
            "temperatura": temp,
            "chuva_mm": chuva
        })

    return registros