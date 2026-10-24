from pathlib import Path
from machine_learning import OperationalHealthModel

m = OperationalHealthModel.load(
    Path("ml_assets/modelo_saude_operacional_tumosan_final.pkl")
)

atual = {
    "EngCoolantTemp": 78.0, "EngOilTemp1": 89.0, "EngOilPress": 375.0,
    "ActualEngine_PercTorque": 65.0, "EngineSpeed": 1800.0,
    "EngFuelRate": 12.0, "WheelBasedVehicleSpeed": 8.0,
}
medianas = {v: m.profile[v]["mediana"] for v in m.profile}

for nome, vals in [("payload atual do simulador", atual),
                   ("medianas do perfil", medianas)]:
    r = m.predict(vals)
    print(f"\n{nome}: score {r['score']} / {r['status']}")
    for f in r["top_factors"]:
        print("  ", f["label"], f["value"],
              "| mediana", round(f["reference_median"], 1),
              "| faixa", round(f["reference_p05"], 1), "a",
              round(f["reference_p95"], 1))

print("\nPerfil aprendido (p25 / mediana / p75):")
for v, p in m.profile.items():
    print(f"  {v}: {p['p25']:.1f} / {p['mediana']:.1f} / {p['p75']:.1f}")