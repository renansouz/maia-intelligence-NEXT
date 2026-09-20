from __future__ import annotations

import json
from pathlib import Path


class ContextualHealthModel:
    """
    Motor contextual explicável do MVP.

    Não é um ML supervisionado neste momento porque ainda não há
    target real suficiente para aprender os pesos de forma confiável.
    """

    def __init__(self, weights_path, feedback_path):
        self.cfg = json.loads(
            Path(weights_path).read_text(encoding="utf-8")
        )
        self.feedback_cfg = json.loads(
            Path(feedback_path).read_text(encoding="utf-8")
        )

        pesos = self.cfg["global_weights"]
        soma = sum(float(v) for v in pesos.values())

        if abs(soma - 1.0) > 1e-6:
            raise ValueError(
                f"Os pesos globais devem somar 1.0. Soma atual: {soma}"
            )

    @staticmethod
    def maintenance_score(days_since_maintenance, recommended_days=None):
        if days_since_maintenance is None:
            return 70.0

        days = max(float(days_since_maintenance), 0.0)

        if recommended_days is not None and float(recommended_days) > 0:
            recommended = float(recommended_days)
            ratio = days / recommended

            if ratio <= 0.70:
                return 100.0

            if ratio <= 1.0:
                return max(
                    70.0,
                    100.0 - ((ratio - 0.70) / 0.30) * 30.0
                )

            return max(
                0.0,
                70.0 - (ratio - 1.0) * 70.0
            )

        if days <= 90:
            return 100.0
        if days <= 180:
            return 80.0
        if days <= 365:
            return 55.0
        return 30.0

    @staticmethod
    def age_score(machine_age_years):
        if machine_age_years is None:
            return 70.0

        years = max(float(machine_age_years), 0.0)

        if years <= 3:
            return 100.0
        if years <= 7:
            return 90.0
        if years <= 12:
            return 75.0
        if years <= 20:
            return 60.0
        return 45.0

    @staticmethod
    def environment_score(
        ambient_temp_c=None,
        recent_humidity_pct=None,
    ):
        score = 100.0
        reasons = []

        if ambient_temp_c is not None:
            temp = float(ambient_temp_c)

            if temp >= 40:
                score -= 30
                reasons.append("temperatura ambiente muito elevada")
            elif temp >= 35:
                score -= 15
                reasons.append("temperatura ambiente elevada")

        if recent_humidity_pct is not None:
            humidity = float(recent_humidity_pct)

            if humidity >= 90:
                score -= 10
                reasons.append("umidade ambiente muito elevada")

        return max(0.0, score), reasons

    def operator_feedback_score(self, feedback=None):
        if not feedback:
            return 100.0, []

        penalidade = 0.0
        reasons = []

        for item in feedback:
            categoria = item.get("category")
            severidade = item.get("severity")

            info = self.feedback_cfg["categories"].get(categoria)

            if info is None:
                reasons.append(
                    f"feedback ignorado: categoria desconhecida '{categoria}'"
                )
                continue

            if severidade not in info["severities"]:
                reasons.append(
                    f"feedback ignorado: severidade desconhecida "
                    f"'{severidade}' para '{categoria}'"
                )
                continue

            pontos = float(info["severities"][severidade])
            penalidade += pontos

            reasons.append(
                f"{info['label']} ({severidade})"
            )

        penalidade = min(100.0, penalidade)

        return 100.0 - penalidade, reasons

    def score(
        self,
        operational_score,
        machine_age_years=None,
        days_since_maintenance=None,
        recommended_maintenance_days=None,
        ambient_temp_c=None,
        recent_humidity_pct=None,
        operator_feedback=None,
        mechanical_claim_severity=0,
    ):
        operational_score = float(operational_score)

        if not 0 <= operational_score <= 100:
            raise ValueError(
                "operational_score deve estar entre 0 e 100."
            )

        weights = self.cfg["global_weights"]

        maintenance = self.maintenance_score(
            days_since_maintenance,
            recommended_maintenance_days,
        )

        age = self.age_score(machine_age_years)

        environment, environment_reasons = self.environment_score(
            ambient_temp_c,
            recent_humidity_pct,
        )

        operator, operator_reasons = self.operator_feedback_score(
            operator_feedback
        )

        components = {
            "operational": operational_score,
            "maintenance": maintenance,
            "age": age,
            "environment": environment,
            "operator_feedback": operator,
        }

        raw_score = sum(
            components[key] * float(weights[key])
            for key in components
        )

        severity = min(
            max(float(mechanical_claim_severity or 0), 0.0),
            1.0,
        )

        max_penalty = float(
            self.cfg["mechanical_claim_penalty"]["max_points"]
        )

        systemic_penalty = severity * max_penalty

        final_score = max(
            0.0,
            min(100.0, raw_score - systemic_penalty)
        )

        reasons = []

        for factor, value in components.items():
            if value < 60:
                reasons.append({
                    "factor": factor,
                    "score": round(value, 2),
                })

        for reason in environment_reasons:
            reasons.append({
                "factor": "environment",
                "detail": reason,
            })

        for reason in operator_reasons:
            reasons.append({
                "factor": "operator_feedback",
                "detail": reason,
            })

        if systemic_penalty > 0:
            reasons.append({
                "factor": "mechanical_claim_history",
                "penalty_points": round(systemic_penalty, 2),
            })

        return {
            "global_score": round(final_score, 2),
            "score_before_systemic_penalty": round(raw_score, 2),
            "components": {
                key: round(value, 2)
                for key, value in components.items()
            },
            "weights": weights,
            "systemic_penalty": round(systemic_penalty, 2),
            "main_reasons": reasons,
            "note": (
                "Score contextual de engenharia do MVP. "
                "Pesos e faixas exigem calibração futura."
            ),
        }
