"""noted by renansouz
Traduz a previsão horária bruta (api_clima.py) em alertas simples pro
Operador: chuva forte ou vento forte nas próximas horas.

Limiares adotados (referência meteorológica geral, não específica do
agro): chuva >= 10mm/h é considerada forte; vento >= 40km/h é
considerado forte o suficiente para afetar operação de máquina agrícola
com segurança. Esses valores podem ser recalibrados com o time depois.
"""
from datetime import datetime, timezone
from app.services.api_clima import buscar_previsao_horaria

LIMIAR_CHUVA_FORTE_MM = 10.0
LIMIAR_VENTO_FORTE_KMH = 40.0


def obter_previsao_com_alerta(latitude, longitude, proximas_horas=12):
    previsao = buscar_previsao_horaria(latitude, longitude)
    if not previsao:
        return None

    agora = datetime.now(timezone.utc).replace(tzinfo=None)
    futuros = [
        p for p in previsao
        if datetime.fromisoformat(p["hora"]) >= agora
    ][:proximas_horas]

    for p in futuros:
        p["alerta_chuva"] = p["chuva_mm"] >= LIMIAR_CHUVA_FORTE_MM
        p["alerta_vento"] = p["vento_kmh"] >= LIMIAR_VENTO_FORTE_KMH

    algum_alerta = any(p["alerta_chuva"] or p["alerta_vento"] for p in futuros)

    return {
        "previsao": futuros,
        "tem_alerta": algum_alerta
    }