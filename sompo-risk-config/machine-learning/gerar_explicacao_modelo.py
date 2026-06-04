from prever_risco import (
    buscar_ultimo_registro_cidade,
    prever_risco_por_dados,
    criar_indicadores
)


def gerar_explicacoes_tecnicas(dados):
    explicacoes = []

    if (
        dados["indicador_chuva_alta"]
        and dados["indicador_solo_umido"]
    ):
        explicacoes.append(
            "A combinação de chuva elevada e solo úmido "
            "aumenta o risco de atolamento, reduz a tração "
            "do equipamento e dificulta a operação em campo."
        )

    if (
        dados["indicador_chuva_alta"]
        and dados["indicador_perto_agua"]
    ):
        explicacoes.append(
            "A proximidade de corpos d'água associada à "
            "alta precipitação aumenta a probabilidade "
            "de encharcamento do terreno."
        )

    if dados["indicador_manutencao_atrasada"]:
        explicacoes.append(
            "A manutenção atrasada aumenta o risco de "
            "falhas mecânicas, desgaste excessivo e "
            "interrupções não planejadas."
        )

    if dados["indicador_inclinacao_alta"]:
        explicacoes.append(
            "Terrenos com elevada inclinação aumentam "
            "o risco de instabilidade operacional e "
            "dificultam a movimentação segura do equipamento."
        )

    if dados["indicador_velocidade_alta"]:
        explicacoes.append(
            "Velocidades elevadas reduzem o tempo de reação "
            "do operador diante de situações críticas."
        )

    return explicacoes


def gerar_recomendacoes(dados):
    recomendacoes = []

    if dados["indicador_chuva_alta"]:
        recomendacoes.append(
            "Monitorar as condições climáticas antes da operação."
        )

    if dados["indicador_solo_umido"]:
        recomendacoes.append(
            "Evitar operações em áreas com excesso de umidade."
        )

    if dados["indicador_perto_agua"]:
        recomendacoes.append(
            "Redobrar a atenção em regiões próximas a corpos d'água."
        )

    if dados["indicador_manutencao_atrasada"]:
        recomendacoes.append(
            "Realizar manutenção preventiva antes da operação."
        )

    if dados["indicador_inclinacao_alta"]:
        recomendacoes.append(
            "Reduzir velocidade em áreas com grande inclinação."
        )

    return recomendacoes


def gerar_fatores_risco(dados):
    fatores = []

    if dados["indicador_chuva_alta"]:
        fatores.append(
            f"Chuva elevada ({dados['chuva_mm']} mm)"
        )

    if dados["indicador_solo_umido"]:
        fatores.append(
            f"Solo muito úmido ({dados['umidade_solo']}%)"
        )

    if dados["indicador_velocidade_alta"]:
        fatores.append(
            f"Velocidade elevada ({dados['velocidade_kmh']} km/h)"
        )

    if dados["indicador_perto_agua"]:
        fatores.append(
            f"Próximo de corpos d'água ({dados['proximidade_agua_m']} m)"
        )

    if dados["indicador_inclinacao_alta"]:
        fatores.append(
            f"Inclinação elevada ({dados['inclinacao_graus']}°)"
        )

    if dados["indicador_manutencao_atrasada"]:
        fatores.append(
            f"Manutenção atrasada ({dados['manutencao_dias']} dias)"
        )

    return fatores


def gerar_resumo_executivo(
    classificacao,
    fatores_risco
):
    if not fatores_risco:
        return (
            "O equipamento apresentou condições "
            "operacionais estáveis e baixo risco "
            "de ocorrência de incidentes."
        )

    texto = (
        f"O equipamento foi classificado como "
        f"{classificacao.upper()} RISCO devido à presença de "
    )

    texto += ", ".join(fatores_risco[:-1])

    if len(fatores_risco) > 1:
        texto += f" e {fatores_risco[-1]}."
    else:
        texto += fatores_risco[0] + "."

    return texto


def gerar_explicacao(cidade):
    dados = buscar_ultimo_registro_cidade(cidade)

    dados = criar_indicadores(dados)

    resultado = prever_risco_por_dados(dados)

    fatores_risco = gerar_fatores_risco(dados)

    explicacoes_tecnicas = gerar_explicacoes_tecnicas(dados)

    recomendacoes = gerar_recomendacoes(dados)

    resumo = gerar_resumo_executivo(
        resultado["classificacao"],
        fatores_risco
    )

    return {
        "cidade": cidade,
        "classificacao": resultado["classificacao"],
        "probabilidade_alto":
            resultado["probabilidades"].get(1, 0),
        "fatores_risco": fatores_risco,
        "explicacoes_tecnicas": explicacoes_tecnicas,
        "recomendacoes": recomendacoes,
        "resumo_executivo": resumo
    }


if __name__ == "__main__":
    cidade = "Araraquara"

    resultado = gerar_explicacao(cidade)

    print("\n" + "=" * 60)
    print("EXPLICAÇÃO DA IA")
    print("=" * 60)

    print(f"\nCidade: {resultado['cidade']}")

    print(
        f"Classificação: "
        f"{resultado['classificacao'].upper()}"
    )

    print(
        f"Probabilidade de risco alto: "
        f"{resultado['probabilidade_alto'] * 100:.2f}%"
    )

    print("\nRESUMO EXECUTIVO")
    print("-" * 60)
    print(resultado["resumo_executivo"])

    print("\nFATORES DE RISCO")
    print("-" * 60)

    for fator in resultado["fatores_risco"]:
        print(f"• {fator}")

    print("\nEXPLICAÇÃO TÉCNICA")
    print("-" * 60)

    for explicacao in resultado["explicacoes_tecnicas"]:
        print(f"• {explicacao}")

    print("\nRECOMENDAÇÕES")
    print("-" * 60)

    for recomendacao in resultado["recomendacoes"]:
        print(f"• {recomendacao}")

    print("\n")
