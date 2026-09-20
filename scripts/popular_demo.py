"""noted by renansouz
Diferente de popular_banco.py (que gera massa de dados sintéticos para
treino/teste do modelo), este script cria um cenário pequeno, realista
e coerente, pensado para ser usado ao vivo numa demonstração ou banca:
2 gestores, 2 propriedades, 3 máquinas, operadores vinculados, um
ticket já escalado como sinistro, e uma manutenção já concluída.

Rodar isso é opcional. Quem não quiser nenhum dado de exemplo no
sistema simplesmente não executa este script - o app começa vazio,
só com o usuário SOMPO inicial (criado automaticamente no primeiro
start, a partir do ADMIN_EMAIL/ADMIN_SENHA do .env).

Uso:
    python -m scripts.popular_demo
"""
from datetime import date, timedelta

from app.core.config_db import configurar_banco
from app.services.user_service import buscar_usuario_por_email, criar_usuario
from app.services.fazenda_service import criar_fazenda, listar_fazendas_do_gestor
from app.services.maquina_service import (
    criar_maquina, buscar_maquina_por_equipamento_id,
    vincular_maquina_fazenda, vincular_operador_maquina
)
from app.services.data_service import salvar_telemetria_db, buscar_ultima_telemetria
from app.services.risco_service import processar_previsao_completa
from app.services.ticket_service import criar_ticket, escalar_ticket_sompo
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


def gerar_telemetria_e_previsao(equipamento_id, cidade, dias_atras, **telemetria_kwargs):
    """Insere uma leitura de telemetria e processa a previsão de risco a partir dela."""
    leitura = {
        "equipamento_id": equipamento_id,
        "cidade": cidade,
        "data_medicao": date.today() - timedelta(days=dias_atras),
        "temperatura": telemetria_kwargs.get("temperatura", 26.0),
        "chuva_mm": telemetria_kwargs.get("chuva_mm", 5.0),
        "umidade_solo": telemetria_kwargs.get("umidade_solo", 40.0),
        "velocidade_kmh": telemetria_kwargs.get("velocidade_kmh", 10.0),
        "proximidade_agua_m": telemetria_kwargs.get("proximidade_agua_m", 400.0),
        "inclinacao_graus": telemetria_kwargs.get("inclinacao_graus", 4.0),
        "tempo_uso_horas": telemetria_kwargs.get("tempo_uso_horas", 4.0),
        "manutencao_dias": telemetria_kwargs.get("manutencao_dias", 10),
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

    print("\n--- Criando propriedades ---")
    santa_rita_id = garantir_fazenda(renan_id, "Fazenda Santa Rita", "Ribeirão Preto", -21.1775, -47.8103, "Zona Rural, Ribeirão Preto - SP")
    boa_esperanca_id = garantir_fazenda(nicole_id, "Fazenda Boa Esperança", "Sorocaba", -23.5015, -47.4526, "Zona Rural, Sorocaba - SP")

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
    # Máquina em condição estável (risco baixo esperado)
    gerar_telemetria_e_previsao("EQP-SP-04", "Ribeirão Preto", dias_atras=0)

    # Máquina com alguns indicadores de atenção (risco médio esperado)
    gerar_telemetria_e_previsao(
        "EQP-SP-07", "Ribeirão Preto", dias_atras=0,
        chuva_mm=35.0, umidade_solo=75.0, manutencao_dias=95
    )

    # Máquina em condição crítica (risco alto esperado) - a que gera o sinistro
    gerar_telemetria_e_previsao(
        "EQP-SP-12", "Sorocaba", dias_atras=0,
        chuva_mm=42.0, umidade_solo=88.0, proximidade_agua_m=60.0,
        inclinacao_graus=18.0, manutencao_dias=120
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
        escalar_ticket_sompo(tickets_marina[0]["id_ticket"], nicole_id)
        print("  Ticket escalado como sinistro para a Sompo.")

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
    print("  Sompo -> use o ADMIN_EMAIL / ADMIN_SENHA configurados no seu .env")

if __name__ == "__main__":
    popular()