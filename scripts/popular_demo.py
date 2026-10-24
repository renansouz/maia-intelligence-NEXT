"""
Seed de demonstração do MAIA: cenário pequeno e coerente para uso ao vivo.

  EQP-SP-04  saudável (BAIXO)
  EQP-SP-07  ciclo completo: ALTO -> manutenção -> BAIXO (antes/depois pronto)
  EQP-SP-12  em risco (ALTO), ticket escalado como sinistro

Toda previsão passa por processar_previsao_completa (a cadeia de hash
permanece íntegra). Rodar duas vezes duplicaria o histórico, por isso o
script se recusa a rodar sobre uma base já populada.

Uso:
    python -m scripts.popular_demo
"""
import json
import time
from datetime import date, datetime

from app.core.database import db
from app.core.config_db import configurar_banco
from app.services.user_service import buscar_usuario_por_email, criar_usuario
from app.services.fazenda_service import criar_fazenda, listar_fazendas_do_gestor
from app.services.maquina_service import (
    criar_maquina, buscar_maquina_por_equipamento_id,
    vincular_maquina_fazenda, vincular_operador_maquina,
    buscar_historico_maquina,
)
from app.services.data_service import salvar_telemetria_db, buscar_ultima_telemetria
from app.services.risco_service import (
    processar_previsao_completa, verificar_integridade_cadeia,
)
from app.services.ticket_service import (
    criar_ticket, escalar_ticket_sompo, resolver_ticket, listar_tickets_gestor,
)
from app.services.manutencao_service import solicitar_manutencao, concluir_manutencao

# --- Leituras CAN já validadas no modelo ---------------------------------
NORMAL = dict(temp_coolant=78.0, temp_oleo=89.6, pressao_oleo=376.0,
              torque_pct=69.0, rpm=1792.0, combustivel_l_h=16.1, velocidade_kmh=7.0)
SAUDAVEL_SP04 = dict(temp_coolant=78.0, temp_oleo=90.0, pressao_oleo=376.0,
                     torque_pct=69.0, rpm=1790.0, combustivel_l_h=16.0, velocidade_kmh=7.0)
SUPERAQUECIDO = dict(temp_coolant=98.5, temp_oleo=112.0, pressao_oleo=210.0,
                     torque_pct=88.0, rpm=2200.0, combustivel_l_h=19.0, velocidade_kmh=4.5)
DESVIO_SP12 = dict(temp_coolant=88.0, temp_oleo=108.0, pressao_oleo=290.0,
                   torque_pct=92.0, rpm=2250.0, combustivel_l_h=16.0, velocidade_kmh=7.0)

CATEGORIA_FALHA = "Falha ou Ruído Mecânico"


def garantir_usuario(nome, email, senha, papel, gestor_id=None, tipo_cobertura=None):
    existente = buscar_usuario_por_email(email)
    if existente:
        return existente["id_usuario"]
    criar_usuario(nome, email, senha, papel, gestor_id=gestor_id, tipo_cobertura=tipo_cobertura)
    return buscar_usuario_por_email(email)["id_usuario"]


def garantir_fazenda(gestor_id, nome, cidade, latitude, longitude, endereco):
    for f in listar_fazendas_do_gestor(gestor_id):
        if f["nome"] == nome:
            return f["id_fazenda"]
    criar_fazenda(gestor_id, nome, cidade, latitude, longitude, endereco)
    for f in listar_fazendas_do_gestor(gestor_id):
        if f["nome"] == nome:
            return f["id_fazenda"]


def garantir_maquina(equipamento_id, gestor_id, tipo, modelo, ano, valor_segurado):
    if buscar_maquina_por_equipamento_id(equipamento_id):
        return
    criar_maquina(equipamento_id, tipo, modelo, ano, criado_por=None,
                  gestor_id=gestor_id, valor_segurado=valor_segurado)


def telemetria_e_previsao(equipamento_id, cidade, valores, manutencao_dias=30):
    """Grava uma leitura CAN e gera a previsão correspondente."""
    salvar_telemetria_db({
        "equipamento_id": equipamento_id,
        "cidade": cidade,
        "data_medicao": date.today(),
        **valores,
        "manutencao_dias": manutencao_dias,
    })
    dados = buscar_ultima_telemetria(equipamento_id)
    dados["data_medicao"] = dados["data_medicao"].strftime("%Y-%m-%d")
    r = processar_previsao_completa(dados)
    print(f"  {equipamento_id}: {r['classificacao']} (saúde {r['score'] * 100:.1f})")
    return r


def id_do_unico_ticket(gestor_id):
    tickets = listar_tickets_gestor(gestor_id)
    return tickets[0]["id_ticket"] if tickets else None


def popular():
    print("Sincronizando schema...")
    configurar_banco()

    if buscar_maquina_por_equipamento_id("EQP-SP-04"):
        print("\nA base já tem dados de demonstração (EQP-SP-04 existe).")
        print("Apague as tabelas do app antes de rodar de novo, para não duplicar o histórico.")
        return

    print("\n--- Usuários ---")
    renan_id = garantir_usuario("Renan Souza", "gestor@fazendasantarita.com.br", "demo1234",
                                "GESTOR", tipo_cobertura="BASICA")
    nicole_id = garantir_usuario("Nicole Souza", "gestor@fazendaboaesperanca.com.br", "demo1234",
                                 "GESTOR", tipo_cobertura="BASICA,ADICIONAL")
    kevin_id = garantir_usuario("Kevin Vitor", "operador@fazendasantarita.com.br", "demo1234",
                                "OPERADOR", gestor_id=renan_id)
    thiese_id = garantir_usuario("Thiese Duran", "operador@fazendaboaesperanca.com.br", "demo1234",
                                 "OPERADOR", gestor_id=nicole_id)

    print("\n--- Propriedades ---")
    santa_rita_id = garantir_fazenda(renan_id, "Fazenda Santa Rita", "Ribeirão Preto",
                                     -21.1775, -47.8103, "Zona Rural, Ribeirão Preto - SP")
    boa_esperanca_id = garantir_fazenda(nicole_id, "Fazenda Boa Esperança", "Sorocaba",
                                        -23.5015, -47.4526, "Zona Rural, Sorocaba - SP")

    print("\n--- Dados ambientais base (satélite) ---")
    conn = db.get_connection()
    cursor = conn.cursor()
    try:
        features_exemplo = json.dumps({
            "vv_mean_db": -12.4, "vh_mean_db": -18.2, "ndwi_mean": 0.15, "ndmi_mean": 0.25,
            "soil_moisture_0_7cm_mean_m3_m3": 0.28, "rain_7d_mm": 12.5, "slope_aoi_mean_deg": 3.2
        })
        cursor.execute("""
            MERGE INTO TB_ML_AMBIENTAL t
            USING (SELECT 'EDA_AMBIENTAL' as f, TO_DATE('2026-09-20', 'YYYY-MM-DD') as d,
                          -21.1775 as lat, -47.8103 as lon FROM DUAL) s
            ON (t.FONTE = s.f AND t.LATITUDE = s.lat AND t.LONGITUDE = s.lon)
            WHEN NOT MATCHED THEN
                INSERT (FONTE, DATA_OBSERVACAO, LATITUDE, LONGITUDE, FEATURES_JSON, HASH_REGISTRO)
                VALUES ('EDA_AMBIENTAL', TO_DATE('2026-09-20', 'YYYY-MM-DD'),
                        -21.1775, -47.8103, :feat, 'hash_geo_ribeirao_preto')
        """, feat=features_exemplo)
        conn.commit()
    except Exception as e:
        print(f"Aviso ao injetar base ambiental: {e}")
    finally:
        cursor.close()
        db.release_connection(conn)

    print("\n--- Máquinas e vínculos ---")
    garantir_maquina("EQP-SP-04", renan_id, "Trator", "John Deere 6110J", 2020, 320000.00)
    garantir_maquina("EQP-SP-07", renan_id, "Colheitadeira", "Case IH 2388", 2018, 480000.00)
    garantir_maquina("EQP-SP-12", nicole_id, "Trator", "Massey Ferguson 4707", 2021, 350000.00)
    vincular_maquina_fazenda("EQP-SP-04", santa_rita_id)
    vincular_maquina_fazenda("EQP-SP-07", santa_rita_id)
    vincular_maquina_fazenda("EQP-SP-12", boa_esperanca_id)
    vincular_operador_maquina("EQP-SP-04", kevin_id)
    vincular_operador_maquina("EQP-SP-07", kevin_id)
    vincular_operador_maquina("EQP-SP-12", thiese_id)

    # ------------------------------------------------------------------
    print("\n--- História 1: EQP-SP-04, operação saudável ---")
    telemetria_e_previsao("EQP-SP-04", "Ribeirão Preto", SAUDAVEL_SP04)

    # ------------------------------------------------------------------
    print("\n--- História 2: EQP-SP-07, ciclo completo (alerta -> manutenção -> confirmação) ---")
    criar_ticket(
        "EQP-SP-07", kevin_id, categoria=CATEGORIA_FALHA,
        observacao=("Barulho metálico no motor e cheiro de aquecimento depois de cerca de "
                    "duas horas de colheita. O painel marcou temperatura alta duas vezes."),
    )
    telemetria_e_previsao("EQP-SP-07", "Ribeirão Preto", SUPERAQUECIDO, manutencao_dias=95)

    token = solicitar_manutencao(
        "EQP-SP-07", renan_id,
        descricao=("Inspeção corretiva após alerta do MAIA e relato do operador: "
                   "ruído no motor e temperatura do óleo elevada."),
        tipo="CORRETIVA",
    )
    concluir_manutencao(
        token, date.today().isoformat(), datetime.now().strftime("%H:%M"),
        "Troca do óleo e do filtro, limpeza do radiador e calibração da pressão do óleo. "
        "Motor testado sob carga sem ruído anormal.",
    )
    time.sleep(2)  # garante que a previsão seguinte seja posterior à conclusão
    telemetria_e_previsao("EQP-SP-07", "Ribeirão Preto", NORMAL)

    ticket_id = id_do_unico_ticket(renan_id)
    if ticket_id:
        resolver_ticket(ticket_id, renan_id)
        print("  Ticket do operador marcado como resolvido.")

    # ------------------------------------------------------------------
    print("\n--- História 3: EQP-SP-12, risco alto com sinistro escalado ---")
    criar_ticket(
        "EQP-SP-12", thiese_id, categoria=CATEGORIA_FALHA,
        observacao=("Motor com ruído forte e superaquecimento após duas horas de operação "
                    "contínua. Parei a máquina e aguardo orientação."),
    )
    telemetria_e_previsao("EQP-SP-12", "Sorocaba", DESVIO_SP12, manutencao_dias=150)
    ticket_id = id_do_unico_ticket(nicole_id)
    if ticket_id:
        escalar_ticket_sompo(ticket_id, nicole_id)
        print("  Ticket escalado como sinistro para a Sompo.")

    # ------------------------------------------------------------------
    print("\n--- Verificação ---")
    historico = buscar_historico_maquina("EQP-SP-07")
    ad = next((e["antes_depois"] for e in historico if e.get("antes_depois")), None)
    if ad:
        antes = ad["antes"]["classificacao"] if ad["antes"] else "-"
        depois = ad["depois"]["classificacao"] if ad["depois"] else "-"
        print(f"  EQP-SP-07  antes: {antes} | depois: {depois} | estado: {ad['estado']}")
        if ad["estado"] != "CONFIRMADA":
            print("  ATENÇÃO: o esperado era CONFIRMADA. Me mande esta linha.")
    cadeia = verificar_integridade_cadeia()
    situacao = "íntegra" if cadeia["integra"] else "QUEBRADA"
    print(f"  Cadeia de auditoria: {situacao} ({cadeia['total_registros']} registros)")

    print("\nSeed concluído.")
    print("\nLogins de demonstração (senha: demo1234):")
    print("  Gestor Renan Souza    -> gestor@fazendasantarita.com.br")
    print("  Gestor Nicole Souza   -> gestor@fazendaboaesperanca.com.br")
    print("  Operador Kevin Vitor  -> operador@fazendasantarita.com.br")
    print("  Operador Thiese Duran -> operador@fazendaboaesperanca.com.br")
    print("  Sompo -> ADMIN_EMAIL / ADMIN_SENHA do seu .env")


if __name__ == "__main__":
    popular()