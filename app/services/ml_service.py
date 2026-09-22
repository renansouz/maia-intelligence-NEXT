"""noted by renansouz
Integra o motor de saúde operacional construído pelo Kevin/JV
(Isolation Forest sobre telemetria CAN/J1939 + camada contextual +
perfil evolutivo por máquina) ao restante do backend, mantendo o
mesmo contrato de saída que o resto do sistema (risco_service,
auditoria, frontend) já espera: score, classificacao, explicacao_completa.
"""
from pathlib import Path

from machine_learning import (
    OperationalHealthModel,
    ContextualHealthModel,
    MachineProfileManager,
    HealthScoringService,
)

BASE_DIR = Path(__file__).resolve().parents[2]

MODEL_PATH = BASE_DIR / "ml_assets" / "modelo_saude_operacional_tumosan_final.pkl"
WEIGHTS_PATH = BASE_DIR / "machine_learning" / "config" / "weights.json"
FEEDBACK_PATH = BASE_DIR / "machine_learning" / "config" / "operator_feedback.json"
HISTORY_DIR = BASE_DIR / "data" / "machine_history"

RECOMMENDED_MAINTENANCE_DAYS = 180


class MLService:
    def __init__(self):
        self.operational = OperationalHealthModel.load(MODEL_PATH)
        self.contextual = ContextualHealthModel(WEIGHTS_PATH, FEEDBACK_PATH)
        self.profiles = MachineProfileManager(HISTORY_DIR)
        self.service = HealthScoringService(self.operational, self.contextual, self.profiles)

    def _mapear_classificacao(self, status):
        return {
            "ADERENTE": "BAIXO",
            "ATENCAO": "MEDIO",
            "DESVIO_RELEVANTE": "ALTO",
            "DESVIO_FORTE": "ALTO",
        }.get(status, "MEDIO")

    def _montar_explicacao(self, resultado):
        """
        Mantém o mesmo formato de seções "RESUMO ... || FATORES: ... || ..."
        que o frontend (diagnostico.js) já sabe extrair, trocando apenas
        o conteúdo pelas informações do novo motor.
        """
        operacional = resultado["operational_health"]
        contextual = resultado["contextual_global_health"]

        partes = [f"RESUMO: {operacional['explanation']}"]

        if operacional["top_factors"]:
            fatores = ", ".join(f["label"] for f in operacional["top_factors"])
            partes.append(f"FATORES: {fatores}")

        if contextual["main_reasons"]:
            motivos = "; ".join(
                r.get("detail") or f"{r['factor']}: {r.get('score', '')}"
                for r in contextual["main_reasons"]
            )
            partes.append(f"CONTEXTO: {motivos}")

        return " || ".join(partes)

    def prever_score(self, dados_telemetria):
        equipamento_id = dados_telemetria.get("equipamento_id")

        telemetry = {
            "EngCoolantTemp": dados_telemetria.get("temp_coolant"),
            "EngOilTemp1": dados_telemetria.get("temp_oleo"),
            "EngOilPress": dados_telemetria.get("pressao_oleo"),
            "ActualEngine_PercTorque": dados_telemetria.get("torque_pct"),
            "EngineSpeed": dados_telemetria.get("rpm"),
            "EngFuelRate": dados_telemetria.get("combustivel_l_h"),
            "WheelBasedVehicleSpeed": dados_telemetria.get("velocidade_kmh"),
        }

        faltantes = [k for k, v in telemetry.items() if v is None]
        if faltantes:
            raise ValueError(f"Telemetria CAN incompleta, faltando: {faltantes}")

        context = {
            "days_since_maintenance": dados_telemetria.get("manutencao_dias"),
            "recommended_maintenance_days": RECOMMENDED_MAINTENANCE_DAYS,
        }

        resultado = self.service.generate_score(
            machine_id=equipamento_id,
            telemetry=telemetry,
            context=context,
            timestamp=str(dados_telemetria.get("data_medicao", "")),
            persist_history=True,
        )

        score = resultado["contextual_global_health"]["global_score"] / 100.0
        classificacao = self._mapear_classificacao(resultado["operational_health"]["status"])
        explicacao = self._montar_explicacao(resultado)

        return {
            "score": round(score, 4),
            "classificacao": classificacao,
            "explicacao_completa": explicacao,
        }


ml_service = MLService()