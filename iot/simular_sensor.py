"""
Simulador de sensor IoT (ESP32 / CAN) para demonstração.
Uso: python3 -m iot.simular_sensor [normal|superaquecido] [EQUIPAMENTO_ID]
"""
import os
import sys
from datetime import date

import requests
from dotenv import load_dotenv

load_dotenv()

BASE_URL = os.getenv("MAIA_URL", "http://127.0.0.1:8000") + "/telemetria"
API_KEY = os.getenv("API_KEY", "senha123")

CENARIOS = {
    "normal": {
        "temp_coolant": 78.0, "temp_oleo": 89.6, "pressao_oleo": 376.0,
        "torque_pct": 69.0, "rpm": 1792.0, "combustivel_l_h": 16.1,
        "velocidade_kmh": 7.0,
    },
    "superaquecido": {
        "temp_coolant": 98.5, "temp_oleo": 112.0, "pressao_oleo": 210.0,
        "torque_pct": 88.0, "rpm": 2200.0, "combustivel_l_h": 19.0,
        "velocidade_kmh": 4.5,
    },
}


def enviar_telemetria(cenario="normal", equipamento="EQP-SP-04"):
    if cenario not in CENARIOS:
        print(f"Cenário desconhecido: {cenario}. Use: {', '.join(CENARIOS)}")
        return
    payload = {
        "equipamento_id": equipamento,
        "cidade": "Ribeirão Preto",
        "data_medicao": date.today().isoformat(),
        **CENARIOS[cenario],
    }
    print(f"[*] Enviando cenário '{cenario}' para {equipamento}...")
    try:
        resp = requests.post(
            BASE_URL, json=payload,
            headers={"Content-Type": "application/json", "X-API-KEY": API_KEY},
        )
        print(f"Status HTTP: {resp.status_code}")
        print(f"Resposta: {resp.json()}")
    except Exception as e:
        print(f"[ERRO] Falha ao conectar com o backend: {e}")


if __name__ == "__main__":
    cenario = sys.argv[1] if len(sys.argv) > 1 else "normal"
    equipamento = sys.argv[2] if len(sys.argv) > 2 else "EQP-SP-04"
    enviar_telemetria(cenario, equipamento)