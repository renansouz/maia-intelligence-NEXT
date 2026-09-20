from __future__ import annotations


class HealthScoringService:
    """
    Fachada única para integração futura com API/banco.
    """

    def __init__(
        self,
        operational_model,
        contextual_model,
        profile_manager=None,
    ):
        self.operational = operational_model
        self.contextual = contextual_model
        self.profiles = profile_manager

    def generate_score(
        self,
        machine_id,
        telemetry,
        context=None,
        timestamp="",
        persist_history=False,
        quality_ok=True,
    ):
        context = context or {}

        operational = self.operational.predict(telemetry)

        ingestion = None

        if persist_history:
            if self.profiles is None:
                raise RuntimeError(
                    "persist_history=True, mas nenhum "
                    "MachineProfileManager foi configurado."
                )

            ingestion = self.profiles.insert_window(
                machine_id=machine_id,
                values=telemetry,
                operational_result=operational,
                timestamp=timestamp,
                quality_ok=quality_ok,
            )

        contextual = self.contextual.score(
            operational_score=operational["score"],
            machine_age_years=context.get("machine_age_years"),
            days_since_maintenance=context.get(
                "days_since_maintenance"
            ),
            recommended_maintenance_days=context.get(
                "recommended_maintenance_days"
            ),
            ambient_temp_c=context.get("ambient_temp_c"),
            recent_humidity_pct=context.get(
                "recent_humidity_pct"
            ),
            operator_feedback=context.get("operator_feedback"),
            mechanical_claim_severity=context.get(
                "mechanical_claim_severity", 0
            ),
        )

        return {
            "machine_id": machine_id,
            "machine_model": context.get("machine_model"),
            "profile_stage": (
                self.profiles.stage(machine_id)
                if self.profiles is not None
                else None
            ),
            "operational_health": operational,
            "contextual_global_health": contextual,
            "profile_ingestion": ingestion,
        }
