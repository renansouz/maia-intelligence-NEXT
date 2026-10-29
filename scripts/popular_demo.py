"""noted by renansouz
Diferente de popular_banco.py (que gera massa de dados sintéticos para
treino/teste do modelo), este script cria um cenário pequeno, realista
e coerente, pensado para ser usado ao vivo numa demonstração ou banca:
2 gestores, 2 propriedades, 3 máquinas, operadores vinculados, um
ticket já escalado como sinistro, e uma manutenção já concluída.

Rodar isso é opcional. Quem não quiser nenhum dado de exemplo no
sistema simplesmente não executa este script - o app começa vazio,
só com o usuário seguradora inicial (criado automaticamente no primeiro
start, a partir do ADMIN_EMAIL/ADMIN_SENHA do .env).

Uso:
    python -m scripts.popular_demo
"""
from datetime import date, timedelta
import json
from app.core.database import db

from app.core.config_db import configurar_banco
from app.services.user_service import buscar_usuario_por_email, criar_usuario
from app.services.fazenda_service import criar_fazenda, listar_fazendas_do_gestor
from app.services.maquina_service import (
    criar_maquina, buscar_maquina_por_equipamento_id,
    vincular_maquina_fazenda, vincular_operador_maquina
)
from app.services.data_service import salvar_telemetria_db, buscar_ultima_telemetria
from app.services.risco_service import processar_previsao_completa
from app.services.ticket_service import criar_ticket, escalar_ticket_seguradora
from app.services.manutencao_service import solicitar_manutencao, concluir_manutencao


def garantir_usuario(nome, email, senha, papel, gestor_id=None, tipo_cobertura=None):
    existente = buscar_usuario_por_email(email)
    if existente:
        print(f"Já existe: {email}")
        return existente["id_usuario"]

    criar_usuario(nome, email, senha, papel, gestor_id=gestor_id, tipo_cobertura=tipo_cobertura)
    return buscar_usuario_por_email(email)["id_usuario"]


def garantir_fazenda(gestor_id, nome, cidade, latitude, longitude, endereco):
    for f in listar_fazendas_do_gestor(gestor_id):
        if f["nome"] == nome:
            print(f"Já existe: fazenda {nome}")
            return f["id_fazenda"]

    criar_fazenda(gestor_id, nome, cidade, latitude, longitude, endereco)
    for f in listar_fazendas_do_gestor(gestor_id):
        if f["nome"] == nome:
            return f["id_fazenda"]


def garantir_maquina(equipamento_id, gestor_id, tipo, modelo, ano, valor_segurado):
    if buscar_maquina_por_equipamento_id(equipamento_id):
        print(f"Já existe: máquina {equipamento_id}")
        return
    criar_maquina(equipamento_id, tipo, modelo, ano, criado_por=None, gestor_id=gestor_id, valor_segurado=valor_segurado)


def gerar_telemetria_e_previsao(equipamento_id, cidade, dias_atras, **can_kwargs):
    """Insere uma leitura de telemetria CAN e processa a previsão de risco a partir dela."""
    leitura = {
        "equipamento_id": equipamento_id,
        "cidade": cidade,
        "data_medicao": date.today() - timedelta(days=dias_atras),
        "temp_coolant": can_kwargs.get("temp_coolant", 78.0),
        "temp_oleo": can_kwargs.get("temp_oleo", 90.0),
        "pressao_oleo": can_kwargs.get("pressao_oleo", 376.0),
        "torque_pct": can_kwargs.get("torque_pct", 69.0),
        "rpm": can_kwargs.get("rpm", 1790.0),
        "combustivel_l_h": can_kwargs.get("combustivel_l_h", 16.0),
        "velocidade_kmh": can_kwargs.get("velocidade_kmh", 7.0),
        "manutencao_dias": can_kwargs.get("manutencao_dias", 30),
    }
    salvar_telemetria_db(leitura)

    dados = buscar_ultima_telemetria(equipamento_id)
    dados["data_medicao"] = dados["data_medicao"].strftime("%Y-%m-%d")
    resultado = processar_previsao_completa(dados)
    print(f"  Previsão gerada para {equipamento_id}: {resultado['classificacao']} ({resultado['score']:.0%})")

def popular():
    print("Sincronizando schema...")
    configurar_banco()

    print("\n--- Criando gestores ---")
    renan_id = garantir_usuario("Renan Souza", "gestor@fazendasantarita.com.br", "demo1234", "GESTOR", tipo_cobertura="BASICA")
    nicole_id = garantir_usuario("Nicole Souza", "gestor@fazendaboaesperanca.com.br", "demo1234", "GESTOR", tipo_cobertura="BASICA,ADICIONAL")

    print("\n--- Criando operadores ---")
    kevin_id = garantir_usuario("Kevin Vitor", "operador@fazendasantarita.com.br", "demo1234", "OPERADOR", gestor_id=renan_id)
    thiese_id = garantir_usuario("Thiese Duran", "operador@fazendaboaesperanca.com.br", "demo1234", "OPERADOR", gestor_id=nicole_id)

    print("\n--- Criando propriedades com coordenadas reais ---")
    santa_rita_id = garantir_fazenda(renan_id, "Fazenda Santa Rita", "Ribeirão Preto", -21.1775, -47.8103, "Zona Rural, Ribeirão Preto - SP")
    boa_esperanca_id = garantir_fazenda(nicole_id, "Fazenda Boa Esperança", "Sorocaba", -23.5015, -47.4526, "Zona Rural, Sorocaba - SP")

    print("\n--- Injetando dados ambientais base (PCA / Satélite) ---")
    conn = db.get_connection()
    cursor = conn.cursor()
    try:
        # Insere um registro mockado/real na TB_ML_AMBIENTAL para as coordenadas de Ribeirão Preto e Sorocaba
        features_exemplo = json.dumps({
            "vv_mean_db": -12.4, "vh_mean_db": -18.2, "ndwi_mean": 0.15, "ndmi_mean": 0.25,
            "soil_moisture_0_7cm_mean_m3_m3": 0.28, "rain_7d_mm": 12.5, "slope_aoi_mean_deg": 3.2
        })
        cursor.execute("""
            MERGE INTO TB_ML_AMBIENTAL t
            USING (SELECT 'EDA_AMBIENTAL' as f, TO_DATE('2026-09-20', 'YYYY-MM-DD') as d, -21.1775 as lat, -47.8103 as lon FROM DUAL) s
            ON (t.FONTE = s.f AND t.LATITUDE = s.lat AND t.LONGITUDE = s.lon)
            WHEN NOT MATCHED THEN
                INSERT (FONTE, DATA_OBSERVACAO, LATITUDE, LONGITUDE, FEATURES_JSON, HASH_REGISTRO)
                VALUES ('EDA_AMBIENTAL', TO_DATE('2026-09-20', 'YYYY-MM-DD'), -21.1775, -47.8103, :feat, 'hash_geo_ribeirao_preto')
        """, feat=features_exemplo)
        conn.commit()
    except Exception as e:
        print(f"Aviso ao injetar base ambiental: {e}")
    finally:
        cursor.close()
        db.release_connection(conn)


    print("\n--- Cadastrando máquinas ---")
    garantir_maquina("EQP-SP-04", renan_id, "Trator", "John Deere 6110J", 2020, 320000.00)
    garantir_maquina("EQP-SP-07", renan_id, "Colheitadeira", "Case IH 2388", 2018, 480000.00)
    garantir_maquina("EQP-SP-12", nicole_id, "Trator", "Massey Ferguson 4707", 2021, 350000.00)

    print("\n--- Vinculando máquinas às propriedades ---")
    vincular_maquina_fazenda("EQP-SP-04", santa_rita_id)
    vincular_maquina_fazenda("EQP-SP-07", santa_rita_id)
    vincular_maquina_fazenda("EQP-SP-12", boa_esperanca_id)

    print("\n--- Vinculando operadores às máquinas ---")
    vincular_operador_maquina("EQP-SP-04", kevin_id)
    vincular_operador_maquina("EQP-SP-07", kevin_id)
    vincular_operador_maquina("EQP-SP-12", thiese_id)

    print("\n--- Gerando telemetria e previsão de risco ---")
    # Máquina em condição aderente ao padrão (risco baixo esperado)
    gerar_telemetria_e_previsao("EQP-SP-04", "Ribeirão Preto", dias_atras=0)

    # Máquina com desvio moderado (risco médio esperado)
    gerar_telemetria_e_previsao(
        "EQP-SP-07", "Ribeirão Preto", dias_atras=0,
        temp_oleo=98.0, pressao_oleo=340.0, manutencao_dias=95
    )

    # Máquina com desvio forte (risco alto esperado) - a que gera o sinistro
    gerar_telemetria_e_previsao(
        "EQP-SP-12", "Sorocaba", dias_atras=0,
        temp_coolant=88.0, temp_oleo=108.0, pressao_oleo=290.0,
        torque_pct=92.0, rpm=2250.0, manutencao_dias=150
    )

    print("\n--- Criando ticket e escalando como sinistro ---")
    criar_ticket(
        "EQP-SP-12", thiese_id,
        categoria="Falha ou Ruído Mecânico",
        observacao="Motor apresentando ruído forte e superaquecimento após duas horas de operação contínua."
    )
    from app.services.ticket_service import listar_tickets_gestor
    tickets_marina = listar_tickets_gestor(nicole_id)
    if tickets_marina:
        escalar_ticket_seguradora(tickets_marina[0]["id_ticket"], nicole_id)
        print("  Ticket escalado como sinistro para a seguradora.")

    print("\n--- Registrando manutenção já concluída (histórico) ---")
    token = solicitar_manutencao("EQP-SP-04", renan_id, descricao="Revisão preventiva de rotina.", tipo="PREVENTIVA")
    if token:
        data_passada = (date.today() - timedelta(days=15)).isoformat()
        concluir_manutencao(token, data_passada, "09:30", "Troca de filtro de óleo e verificação geral do motor.")
        print("  Manutenção registrada e concluída no histórico.")

    print("\n✅ Cenário de demonstração populado com sucesso.")
    print("\nLogins de demonstração:")
    print("  Gestor Renan Souza    -> gestor@fazendasantarita.com.br / demo1234")
    print("  Gestor Nicole Souza   -> gestor@fazendaboaesperanca.com.br / demo1234")
    print("  Operador Kevin Vitor  -> operador@fazendasantarita.com.br / demo1234")
    print("  Operador Thiese Duran -> operador@fazendaboaesperanca.com.br / demo1234")
    print("  seguradora -> use o ADMIN_EMAIL / ADMIN_SENHA configurados no seu .env")

if __name__ == "__main__":
    popular()