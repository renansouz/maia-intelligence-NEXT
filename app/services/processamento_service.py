import random

random.seed(42)

def calcular_indicadores(dados):
    d = {k.lower(): v for k, v in dados.items()}
    
    res = {}
    res['indicador_chuva_alta'] = 1 if d.get('chuva_mm', 0) > 30 else 0
    res['indicador_solo_umido'] = 1 if d.get('umidade_solo', 0) > 70 else 0
    res['indicador_velocidade_alta'] = 1 if d.get('velocidade_kmh', 0) > 18 else 0
    res['indicador_perto_agua'] = 1 if d.get('proximidade_agua_m', 0) < 100 else 0
    res['indicador_inclinacao_alta'] = 1 if d.get('inclinacao_graus', 0) > 15 else 0
    res['indicador_manutencao_atrasada'] = 1 if d.get('manutencao_dias', 0) > 90 else 0
    
    return res

def gerar_risco_probabilistico(indicadores):
    qtd_ativos = sum(indicadores.values())
    sorteio = random.random()
    
    if qtd_ativos >= 4:
        return 1 if sorteio <= 0.75 else 0
    elif qtd_ativos >= 2:
        return 1 if sorteio <= 0.35 else 0
    else:
        return 1 if sorteio <= 0.08 else 0