import os

import oracledb
from dotenv import load_dotenv

from prever_risco import (
    buscar_ultimo_registro_cidade,
    prever_risco_por_dados,
    criar_indicadores,
    conectar_oracle,
)

load_dotenv()


# ── Geração de explicações ─────────────────────────────────────────────────────
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


def gerar_resumo_executivo(classificacao, fatores_risco):
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


def montar_texto_explicacao(resultado):
    partes = [f"RESUMO: {resultado['resumo_executivo']}"]

    if resultado["fatores_risco"]:
        partes.append("FATORES: " + " | ".join(resultado["fatores_risco"]))

    if resultado["explicacoes_tecnicas"]:
        partes.append("TECNICO: " + " | ".join(resultado["explicacoes_tecnicas"]))

    if resultado["recomendacoes"]:
        partes.append("RECOMENDACOES: " + " | ".join(resultado["recomendacoes"]))

    return " || ".join(partes)


# ── Persistência ───────────────────────────────────────────────────────────────
def garantir_coluna_explicacao(conn):
    cursor = conn.cursor()
    cursor.execute("""
        SELECT COUNT(*) FROM USER_TAB_COLUMNS
        WHERE TABLE_NAME  = 'TB_PREVISAO_RISCO'
          AND COLUMN_NAME = 'EXPLICACAO'
    """)
    existe = cursor.fetchone()[0]
    cursor.close()

    if not existe:
        c = conn.cursor()
        c.execute(
            "ALTER TABLE TB_PREVISAO_RISCO ADD EXPLICACAO VARCHAR2(4000)"
        )
        conn.commit()
        c.close()


def salvar_explicacao_banco(cidade, data_medicao, texto, conn):
    cursor = conn.cursor()
    cursor.execute("""
        UPDATE TB_PREVISAO_RISCO
        SET    EXPLICACAO   = :explicacao
        WHERE  CIDADE       = :cidade
          AND  DATA_MEDICAO = :data_med
    """, {
        "explicacao": texto[:4000],
        "cidade":     cidade,
        "data_med":   data_medicao,
    })
    conn.commit()
    cursor.close()


# ── Função principal (chamada pelo prever_risco.py) ────────────────────────────
def gerar_explicacao(cidade):
    dados = buscar_ultimo_registro_cidade(cidade)
    dados = criar_indicadores(dados)

    resultado     = prever_risco_por_dados(dados)
    fatores       = gerar_fatores_risco(dados)
    explicacoes   = gerar_explicacoes_tecnicas(dados)
    recomendacoes = gerar_recomendacoes(dados)
    resumo        = gerar_resumo_executivo(resultado["classificacao"], fatores)

    retorno = {
        "cidade":               cidade,
        "classificacao":        resultado["classificacao"],
        "probabilidade_alto":   resultado["probabilidades"].get(1, 0),
        "fatores_risco":        fatores,
        "explicacoes_tecnicas": explicacoes,
        "recomendacoes":        recomendacoes,
        "resumo_executivo":     resumo,
    }

    # Persiste sempre — usa CIDADE + DATA_MEDICAO como chave
    conn = conectar_oracle()
    garantir_coluna_explicacao(conn)
    texto = montar_texto_explicacao(retorno)
    salvar_explicacao_banco(cidade, dados["data_medicao"], texto, conn)
    conn.close()

    return retorno


CIDADES_VALIDAS = [
    "São Paulo",
    "Campinas",
    "Ribeirão Preto",
    "Sorocaba",
    "Piracicaba",
    "Araraquara",
    "São José Dos Campos",
    "Ribeirão Pires",
    "Taquaritinga",
]


if __name__ == "__main__":
    print("\n" + "=" * 60)
    print("GERAÇÃO DE EXPLICAÇÕES — TODAS AS CIDADES")
    print("=" * 60)

    erros = 0

    for cidade in CIDADES_VALIDAS:
        print(f"\n🤖 Processando: {cidade}...")

        try:
            resultado = gerar_explicacao(cidade)

            print(f"   Classificação : {resultado['classificacao'].upper()}")
            print(f"   Risco alto    : {resultado['probabilidade_alto'] * 100:.2f}%")
            print(f"   Resumo        : {resultado['resumo_executivo'][:80]}...")
            print(f"   ✅ Explicação salva no banco.")

        except Exception as e:
            erros += 1
            print(f"   ❌ Erro: {e}")

    print("\n" + "=" * 60)
    print(f"Concluído. Erros: {erros}/{len(CIDADES_VALIDAS)}")
    print("=" * 60 + "\n")
