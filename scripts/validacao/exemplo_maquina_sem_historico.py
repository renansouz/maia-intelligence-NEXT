"""
EXEMPLO — Máquina nova, sem histórico próprio

Objetivo:
Simular o momento em que uma máquina acabou de entrar no sistema.

Como ela ainda NÃO possui histórico individual:
1. os dados atuais da máquina são recebidos;
2. o modelo operacional usa o baseline Tümosan;
3. o modelo contextual acrescenta cadastro/ambiente/feedback;
4. a leitura pode ser armazenada como início do histórico da unidade;
5. o resultado NÃO afirma que já existe um perfil individual da máquina.

Coloque este arquivo, por exemplo, em:
    scripts/validacao/exemplo_maquina_sem_historico.py

Execute a partir da raiz do projeto:
    python scripts/validacao/exemplo_maquina_sem_historico.py
"""

from pathlib import Path
import sys
import json


# ============================================================
# 1. LOCALIZA A RAIZ DO PROJETO
# ============================================================

ROOT = Path(__file__).resolve()

for p in [ROOT.parent, *ROOT.parents]:
    if (p / "machine_learning").exists() and (p / "ml_assets").exists():
        ROOT = p
        break
else:
    raise RuntimeError("Não foi possível localizar a raiz do projeto.")


if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))


# ============================================================
# 2. IMPORTA OS MÓDULOS
# ============================================================

from machine_learning.operational_model import OperationalHealthModel
from machine_learning.contextual_model import ContextualHealthModel
from machine_learning.profile_manager import MachineProfileManager
from machine_learning.scoring_service import HealthScoringService


# ============================================================
# 3. CARREGA O BASELINE INICIAL
# ============================================================

MODEL_PATH = (
    ROOT
    / "ml_assets"
    / "modelo_saude_operacional_tumosan_final.pkl"
)

WEIGHTS_PATH = (
    ROOT
    / "machine_learning"
    / "config"
    / "weights.json"
)

FEEDBACK_PATH = (
    ROOT
    / "machine_learning"
    / "config"
    / "operator_feedback.json"
)

HISTORY_DIR = (
    ROOT
    / "data"
    / "machine_history"
)


operational_model = OperationalHealthModel.load(MODEL_PATH)

contextual_model = ContextualHealthModel(
    WEIGHTS_PATH,
    FEEDBACK_PATH,
)

profile_manager = MachineProfileManager(
    HISTORY_DIR,
)

service = HealthScoringService(
    operational_model,
    contextual_model,
    profile_manager,
)


# ============================================================
# 4. SIMULA UMA MÁQUINA QUE ACABOU DE SER CADASTRADA
# ============================================================

MACHINE_ID = "TRATOR-DEMO-001"

# Neste momento ela possui ZERO histórico próprio.
print("\nESTADO ANTES DA PRIMEIRA LEITURA")
print(profile_manager.stage(MACHINE_ID))


# ============================================================
# 5. DADOS ATUAIS RECEBIDOS DA MÁQUINA
# ============================================================
#
# Pense neste dicionário como o resultado da janela recente
# enviada pelo ESP32/CAN.
#
# IMPORTANTE:
# EngOilPress = pressão do óleo, não nível do óleo.
#
# Esses valores são apenas um cenário de demonstração.
# ============================================================

telemetry = {
    "EngCoolantTemp": 78.0,             # °C
    "EngOilTemp1": 91.0,                # °C
    "EngOilPress": 300.0,               # unidade da base CAN
    "ActualEngine_PercTorque": 68.0,     # %
    "EngineSpeed": 1800.0,               # RPM
    "EngFuelRate": 12.0,                 # unidade da base CAN
    "WheelBasedVehicleSpeed": 6.0,       # unidade da base CAN
}


# ============================================================
# 6. DADOS DE CONTEXTO
# ============================================================
#
# Estes dados futuramente podem vir do cadastro/banco/API.
# Aqui estão escritos manualmente apenas para simulação.
#
# O modelo da máquina NÃO recebe penalização por ser de
# determinada marca/modelo. Ele identifica qual perfil deverá
# ser usado.
# ============================================================

context = {
    "machine_model": "TUMOSAN 81.110",

    # Cadastro
    "machine_age_years": 2,

    # Manutenção
    "days_since_maintenance": 60,
    "recommended_maintenance_days": 180,

    # Ambiente externo
    "ambient_temp_c": 29.0,
    "recent_humidity_pct": 65.0,

    # Sem feedback neste primeiro exemplo
    "operator_feedback": None,

    # Sem histórico de sinistro mecânico
    "mechanical_claim_severity": 0.0,
}


# ============================================================
# 7. GERA O PRIMEIRO SCORE
# ============================================================
#
# Como não existe perfil individual:
#
#     TRATOR-DEMO-001
#            ↓
#     sem histórico próprio
#            ↓
#     baseline Tümosan
#            ↓
#     score operacional
#            ↓
#     score contextual/global
#
# persist_history=True simula o INSERT dessa primeira janela
# no histórico da máquina.
# ============================================================

resultado = service.generate_score(
    machine_id=MACHINE_ID,
    telemetry=telemetry,
    context=context,
    timestamp="2026-09-19T22:30:00-03:00",
    persist_history=True,
)


# ============================================================
# 8. EXIBE O RESULTADO
# ============================================================

print("\n" + "=" * 70)
print("PRIMEIRO SCORE DA MÁQUINA")
print("=" * 70)

print(
    json.dumps(
        resultado,
        indent=2,
        ensure_ascii=False,
        default=str,
    )
)


# ============================================================
# 9. CONFIRMA O INÍCIO DO HISTÓRICO
# ============================================================

estado_depois = profile_manager.stage(MACHINE_ID)

print("\n" + "=" * 70)
print("ESTADO DO PERFIL APÓS A PRIMEIRA LEITURA")
print("=" * 70)

print(estado_depois)


if estado_depois["stage"] == "INITIAL":
    print(
        "\nA máquina continua no estágio INITIAL."
        "\nO Tümosan continua sendo sua referência operacional principal."
        "\nAs próximas leituras formarão progressivamente o histórico da unidade."
    )


# ============================================================
# 10. VISÃO SIMPLIFICADA PARA O FUTURO BACKEND
# ============================================================

operacional = resultado["operational_health"]
global_health = resultado["contextual_global_health"]

print("\n" + "=" * 70)
print("RESUMO")
print("=" * 70)

print(f"Máquina: {MACHINE_ID}")
print("Perfil utilizado: baseline Tümosan")
print(f"Score operacional: {operacional['score']}/100")
print(f"Status operacional: {operacional['status']}")
print(f"Score global: {global_health['global_score']}/100")

print("\nPrincipais fatores operacionais:")
if operacional["top_factors"]:
    for fator in operacional["top_factors"]:
        print(
            f"- {fator['label']}: "
            f"valor={fator['value']:.2f}, "
            f"referência={fator['reference_median']:.2f}"
        )
else:
    print("- Nenhum desvio operacional relevante identificado.")

print("\nFim da simulação.")
