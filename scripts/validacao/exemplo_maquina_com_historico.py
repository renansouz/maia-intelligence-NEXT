"""
EXEMPLO — Máquina com histórico próprio (validação da arquitetura)

Coloque em:
    scripts/validacao/exemplo_maquina_com_historico.py

Execute pela raiz:
    python scripts/validacao/exemplo_maquina_com_historico.py

IMPORTANTE:
O histórico abaixo é SINTÉTICO e já é marcado como aprovado para baseline.
Isso é intencional: este script testa o cenário "máquina que já acumulou
histórico confiável". A aprovação real ocorrerá durante a ingestão real.
"""

from pathlib import Path
import sys
import json
import random
import pandas as pd

ROOT = Path(__file__).resolve()
for p in [ROOT.parent, *ROOT.parents]:
    if (p / "machine_learning").exists() and (p / "ml_assets").exists():
        ROOT = p
        break
else:
    raise RuntimeError("Não foi possível localizar a raiz do projeto.")

if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from machine_learning import (
    OperationalHealthModel,
    ContextualHealthModel,
    MachineProfileManager,
    HealthScoringService,
    VARIABLES,
)

MODEL_PATH = ROOT / "ml_assets" / "modelo_saude_operacional_tumosan_final.pkl"
WEIGHTS_PATH = ROOT / "machine_learning" / "config" / "weights.json"
FEEDBACK_PATH = ROOT / "machine_learning" / "config" / "operator_feedback.json"
HISTORY_DIR = ROOT / "data" / "machine_history"

baseline_tumosan = OperationalHealthModel.load(MODEL_PATH)
contextual = ContextualHealthModel(WEIGHTS_PATH, FEEDBACK_PATH)

# Limites reduzidos SOMENTE para demonstração.
profiles = MachineProfileManager(
    HISTORY_DIR,
    min_adapt=30,
    min_mature=60,
    candidate_min_score=50,
)

MACHINE_ID = "TRATOR-DEMO-COM-HISTORICO"
history_path = HISTORY_DIR / f"{MACHINE_ID}.csv"
HISTORY_DIR.mkdir(parents=True, exist_ok=True)

if history_path.exists():
    history_path.unlink()

print("\n1) ESTADO INICIAL")
print(profiles.stage(MACHINE_ID))

# ------------------------------------------------------------------
# HISTÓRICO SINTÉTICO JÁ VALIDADO
# ------------------------------------------------------------------
# O teste anterior tentava passar dados artificiais pelo gate do modelo
# Tümosan. Como combinações artificiais podem ser anômalas multivariadas,
# nenhuma janela era aprovada.
#
# Aqui o objetivo é outro: simular uma máquina que JÁ POSSUI histórico
# confiável. Por isso criamos as janelas em torno do perfil robusto do
# artefato e as marcamos explicitamente como approved_for_baseline=True.
# ------------------------------------------------------------------

random.seed(42)
rows = []

for i in range(70):
    row = {
        "machine_id": MACHINE_ID,
        "timestamp": f"HISTORICO-SINTETICO-{i:03d}",
        "score_at_ingestion": 90.0,
        "quality_ok": True,
        "approved_for_baseline": True,
        "source_profile_id": baseline_tumosan.perfil_id,
        "source_model_version": baseline_tumosan.versao,
    }

    for variable in VARIABLES:
        p = baseline_tumosan.profile[variable]
        mediana = float(p["mediana"])
        p25 = float(p["p25"])
        p75 = float(p["p75"])

        # Pequena variação ao redor da mediana, limitada ao intervalo
        # interquartil do perfil original.
        amplitude = max((p75 - p25) * 0.35, abs(mediana) * 0.005, 0.01)
        valor = random.gauss(mediana, amplitude)

        limite_min = min(p25, p75)
        limite_max = max(p25, p75)
        valor = max(limite_min, min(limite_max, valor))

        row[variable] = valor

    rows.append(row)

pd.DataFrame(rows).to_csv(history_path, index=False)

estado = profiles.stage(MACHINE_ID)

print("\n2) DEPOIS DO HISTÓRICO")
print(estado)

if estado["approved_windows"] < profiles.min_adapt:
    raise RuntimeError(
        "Histórico aprovado insuficiente para criar perfil individual."
    )

# ------------------------------------------------------------------
# TREINA PERFIL INDIVIDUAL
# ------------------------------------------------------------------

perfil_individual = profiles.train_individual_candidate(MACHINE_ID)

print("\n3) PERFIL INDIVIDUAL CRIADO")
print("Perfil:", perfil_individual.perfil_id)
print("Tipo:", perfil_individual.tipo)
print("Janelas usadas:", estado["approved_windows"])

# Usa uma leitura baseada nas medianas do próprio perfil recém-criado.
telemetry_atual = {
    "EngCoolantTemp": 78.0,             # Temperatura arrefecimento °C
    "EngOilTemp1": 90.0,                # Temperatura óleo °C
    "EngOilPress": 300.0,               # Pressão óleo
    "ActualEngine_PercTorque": 65.0,     # Torque %
    "EngineSpeed": 1800.0,               # RPM
    "EngFuelRate": 12.0,                 # Consumo/taxa combustível
    "WheelBasedVehicleSpeed": 6.0,       # Velocidade
}

contexto_atual = {
    "machine_model": "TUMOSAN 81.110",
    "machine_age_years": 5,
    "days_since_maintenance": 120,
    "recommended_maintenance_days": 180,
    "ambient_temp_c": 31.0,
    "recent_humidity_pct": 70.0,
    "operator_feedback": [
        {"category": "noise", "severity": "mild"}
    ],
    "mechanical_claim_severity": 0.0,
}

resultado_tumosan = baseline_tumosan.predict(telemetry_atual)
resultado_individual = perfil_individual.predict(telemetry_atual)

print("\n4) COMPARAÇÃO")
print(f"Baseline Tümosan: {resultado_tumosan['score']}/100")
print(f"Perfil individual: {resultado_individual['score']}/100")

service = HealthScoringService(
    operational_model=perfil_individual,
    contextual_model=contextual,
    profile_manager=profiles,
)

resultado_final = service.generate_score(
    machine_id=MACHINE_ID,
    telemetry=telemetry_atual,
    context=contexto_atual,
    timestamp="ATUAL",
    persist_history=True,
)

print("\n5) RESULTADO FINAL")
print(json.dumps(resultado_final, indent=2, ensure_ascii=False, default=str))

print("\n" + "=" * 70)
print("RESUMO")
print("=" * 70)
print("Máquina:", MACHINE_ID)
print("Estágio:", profiles.stage(MACHINE_ID)["stage"])
print("Referência operacional usada: PERFIL INDIVIDUAL")
print("Score operacional:", resultado_final["operational_health"]["score"])
print(
    "Score global:",
    resultado_final["contextual_global_health"]["global_score"],
)

fatores = resultado_final["operational_health"]["top_factors"]

print("\nPrincipais desvios:")
if fatores:
    for f in fatores:
        print(
            f"- {f['label']}: atual={f['value']:.2f} | "
            f"mediana própria={f['reference_median']:.2f} | "
            f"faixa={f['reference_p05']:.2f}-{f['reference_p95']:.2f}"
        )
else:
    print("- Nenhum desvio operacional relevante.")

print(
    "\nOBSERVAÇÃO: este arquivo valida o fluxo técnico de uma máquina "
    "com histórico. As 70 janelas são sintéticas e não devem ser "
    "tratadas como evidência de desempenho real do modelo."
)
