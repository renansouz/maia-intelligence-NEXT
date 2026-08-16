from app.services.risco_service import processar_previsao_completa

exemplo = {
    "equipamento_id": "TESTE-001",
    "cidade": "Sao Paulo",
    "data_medicao": "2024-05-15",
    "temperatura": 28,
    "chuva_mm": 60,
    "umidade_solo": 90,
    "velocidade_kmh": 22,
    "proximidade_agua_m": 30,
    "inclinacao_graus": 18,
    "tempo_uso_horas": 10,
    "manutencao_dias": 5
}

print("Iniciando processamento completo...")
res = processar_previsao_completa(exemplo)
print("Resultado final:")
print(res)