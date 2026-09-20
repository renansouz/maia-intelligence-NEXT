from __future__ import annotations

from pathlib import Path
import pandas as pd

from .operational_model import VARIABLES, OperationalHealthModel


class MachineProfileManager:
    """
    Simula a futura persistência do banco usando CSV local.

    Toda janela pode ser armazenada.
    Somente janelas aprovadas podem alimentar o perfil individual.
    """

    def __init__(
        self,
        history_dir,
        min_adapt=300,
        min_mature=1000,
        candidate_min_score=50,
        max_windows=5000,
    ):
        self.history_dir = Path(history_dir)
        self.history_dir.mkdir(parents=True, exist_ok=True)

        self.min_adapt = int(min_adapt)
        self.min_mature = int(min_mature)
        self.candidate_min_score = float(candidate_min_score)
        self.max_windows = int(max_windows)

    def _path(self, machine_id):
        safe_id = str(machine_id).replace("/", "_").replace("\\", "_")
        return self.history_dir / f"{safe_id}.csv"

    def history(self, machine_id):
        path = self._path(machine_id)

        if not path.exists():
            return pd.DataFrame()

        return pd.read_csv(path)

    def approved(self, machine_id):
        df = self.history(machine_id)

        if df.empty or "approved_for_baseline" not in df.columns:
            return pd.DataFrame(columns=VARIABLES)

        approved_mask = (
            df["approved_for_baseline"]
            .astype(str)
            .str.lower()
            .isin(["true", "1"])
        )

        return df.loc[approved_mask].copy()

    def stage(self, machine_id):
        approved_windows = len(self.approved(machine_id))

        if approved_windows < self.min_adapt:
            stage = "INITIAL"
        elif approved_windows < self.min_mature:
            stage = "ADAPTING"
        else:
            stage = "INDIVIDUAL"

        return {
            "stage": stage,
            "approved_windows": approved_windows,
            "min_adapt": self.min_adapt,
            "min_mature": self.min_mature,
        }

    def insert_window(
        self,
        machine_id,
        values,
        operational_result,
        timestamp="",
        quality_ok=True,
    ):
        faltantes = [v for v in VARIABLES if v not in values]
        if faltantes:
            raise ValueError(
                f"Variáveis faltantes para histórico: {faltantes}"
            )

        score = float(operational_result["score"])

        approved_for_baseline = bool(
            quality_ok
            and score >= self.candidate_min_score
        )

        row = {
            "machine_id": machine_id,
            "timestamp": timestamp,
            **{
                variable: float(values[variable])
                for variable in VARIABLES
            },
            "score_at_ingestion": score,
            "quality_ok": bool(quality_ok),
            "approved_for_baseline": approved_for_baseline,
            "source_profile_id": operational_result.get("perfil_id"),
            "source_model_version": operational_result.get("modelo_versao"),
        }

        path = self._path(machine_id)

        pd.DataFrame([row]).to_csv(
            path,
            mode="a",
            header=not path.exists(),
            index=False,
        )

        return {
            "stored": True,
            "approved_for_baseline": approved_for_baseline,
            **self.stage(machine_id),
        }

    def train_individual_candidate(self, machine_id):
        df = self.approved(machine_id).tail(self.max_windows)

        if len(df) < self.min_adapt:
            raise ValueError(
                "Histórico aprovado insuficiente para criar "
                "um perfil individual candidato."
            )

        return OperationalHealthModel.train(
            df[VARIABLES],
            perfil_id=f"INDIVIDUAL_{machine_id}",
        )
