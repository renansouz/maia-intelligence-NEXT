"""
Simulador de Sensor IoT (ESP32 / CAN) para demonstração da banca.
Envia um payload de telemetria para a API do MAIA.
"""
import requests
import json
import os
from dotenv import load_dotenv

load_dotenv()

BASE_URL = "http://127.0.0.1:8000/telemetria"
API_KEY = os.getenv("API_KEY", "senha123")

def enviar_telemetria(cenario="normal"):
    # Cenários para demonstração na banca
    if cenario == "superaquecido":
        payload = {
            "equipamento_id": "EQP-SP-04",
            "cidade": "Ribeirão Preto",
            "data_medicao": "2026-09-22",
            "temp_coolant": 98.5,  # Crítico (> 95°C)
            "temp_oleo": 112.0,    # Crítico (> 105°C)
            "pressao_oleo": 210.0, # Baixa pressão sob alta temperatura
            "torque_pct": 88.0,
            "rpm": 2200.0,
            "combustivel_l_h": 19.0,
            "velocidade_kmh": 4.5,
            "manutencao_dias": 95
        }
        print("[!]. Simulando cenário crítico de SUPERAQUECIMENTO (Risco de Incêndio)...")
    else:
        payload = {
            "equipamento_id": "EQP-SP-04",
            "cidade": "Ribeirão Preto",
            "data_medicao": "2026-09-22",
            "temp_coolant": 78.0,  # Normal
            "temp_oleo": 89.0,     # Normal
            "pressao_oleo": 375.0, # Normal
            "torque_pct": 65.0,
            "rpm": 1800.0,
            "combustivel_l_h": 12.0,
            "velocidade_kmh": 8.0,
            "manutencao_dias": 10
        }
        print("[*]. Simulando cenário normal de operação...")

    headers = {
        "Content-Type": "application/json",
        "X-API-KEY": API_KEY
    }

    try:
        response = requests.post(BASE_URL, json=payload, headers=headers)
        print(f"Status HTTP: {response.status_code}")
        print(f"Resposta: {response.json()}")
    except Exception as e:
        print(f"[ERRO] Falha ao conectar com o backend: {e}")

if __name__ == "__main__":
    import sys
    cenario_escolhido = sys.argv[1] if len(sys.argv) > 1 else "normal"
    enviar_telemetria(cenario_escolhido)