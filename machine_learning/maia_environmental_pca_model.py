
from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path
from typing import Any, Dict, List, Optional

import joblib
import numpy as np
import pandas as pd
from sklearn.decomposition import PCA
from sklearn.preprocessing import StandardScaler


COLUNAS_CONTROLE = {
    "farm_latitude",
    "farm_longitude",
    "aoi_buffer_m",
    "ml_training_ready",
}

COLUNAS_NAO_FEATURE = {
    "date",
    "date_day",
    "s2_date",
    "orbit_pass",
    "platform",
    "dataset_stage",
    "target_status",
    "location_precise",
    "fonte",
    "data_observacao",
    "latitude",
    "longitude",
    "hash_registro",
}


def _normalizar_colunas(df: pd.DataFrame) -> pd.DataFrame:
    out = df.copy()
    out.columns = [
        str(c).strip().lower().replace(" ", "_")
        for c in out.columns
    ]
    return out


def _percentile_linear(values: np.ndarray, x: np.ndarray) -> np.ndarray:
    ref = np.sort(np.asarray(values, dtype=float))
    if ref.size == 0:
        return np.zeros_like(np.asarray(x, dtype=float))
    idx = np.searchsorted(ref, np.asarray(x, dtype=float), side="right")
    return idx / ref.size


@dataclass
class PCAFitSummary:
    n_rows: int
    n_features: int
    n_components: int
    explained_variance_ratio: List[float]
    cumulative_explained_variance: List[float]


class EnvironmentalPCAModel:
    """
    PCA ambiental não supervisionado.

    O modelo aprende a estrutura multivariada histórica das features ambientais.
    O score retornado é relativo ao padrão aprendido, não uma probabilidade
    de perigo, falha, sinistro ou atolamento.
    """

    def __init__(
        self,
        explained_variance_target: float = 0.90,
        min_components: int = 2,
        max_components: Optional[int] = None,
    ):
        self.explained_variance_target = float(explained_variance_target)
        self.min_components = int(min_components)
        self.max_components = max_components

        self.feature_names_: List[str] = []
        self.constant_features_: List[str] = []
        self.scaler_: Optional[StandardScaler] = None
        self.pca_: Optional[PCA] = None
        self.reference_distances_: Optional[np.ndarray] = None
        self.component_std_: Optional[np.ndarray] = None
        self.fit_summary_: Optional[PCAFitSummary] = None

    def _selecionar_features(self, df: pd.DataFrame) -> pd.DataFrame:
        base = _normalizar_colunas(df)

        numeric = base.select_dtypes(include=[np.number]).copy()
        numeric = numeric.drop(
            columns=[
                c for c in numeric.columns
                if c in COLUNAS_CONTROLE or c in COLUNAS_NAO_FEATURE
            ],
            errors="ignore",
        )

        numeric = numeric.replace([np.inf, -np.inf], np.nan)
        numeric = numeric.dropna(axis=1, how="all")

        for c in numeric.columns:
            serie = pd.to_numeric(numeric[c], errors="coerce")
            med = serie.median()
            if pd.notna(med):
                numeric[c] = serie.fillna(med)

        numeric = numeric.dropna(axis=1, how="any")

        if numeric.empty:
            raise ValueError("Nenhuma feature numérica válida foi encontrada.")

        return numeric.astype(float)

    def fit(self, df: pd.DataFrame) -> "EnvironmentalPCAModel":
        X = self._selecionar_features(df)

        variances = X.var(ddof=0)
        self.constant_features_ = variances[variances <= 1e-10].index.tolist()

        if self.constant_features_:
            X = X.drop(columns=self.constant_features_)

        if X.shape[1] < 2:
            raise ValueError("O PCA precisa de pelo menos 2 features com variância.")

        if len(X) < 3:
            raise ValueError("Use pelo menos 3 observações para ajustar o PCA.")

        self.feature_names_ = X.columns.tolist()

        self.scaler_ = StandardScaler()
        Xz = self.scaler_.fit_transform(X)

        max_allowed = min(Xz.shape[0], Xz.shape[1])
        if self.max_components is not None:
            max_allowed = min(max_allowed, int(self.max_components))

        pca_full = PCA(n_components=max_allowed)
        pca_full.fit(Xz)

        cumulative = np.cumsum(pca_full.explained_variance_ratio_)
        chosen = int(
            np.searchsorted(
                cumulative,
                self.explained_variance_target,
                side="left",
            )
            + 1
        )

        chosen = max(min(self.min_components, max_allowed), chosen)
        chosen = min(chosen, max_allowed)

        self.pca_ = PCA(n_components=chosen)
        scores = self.pca_.fit_transform(Xz)

        component_std = scores.std(axis=0, ddof=0)
        component_std[component_std <= 1e-12] = 1.0
        self.component_std_ = component_std

        distances = np.sqrt(
            np.sum((scores / component_std) ** 2, axis=1)
        )
        self.reference_distances_ = np.sort(distances)

        evr = self.pca_.explained_variance_ratio_
        self.fit_summary_ = PCAFitSummary(
            n_rows=int(X.shape[0]),
            n_features=int(X.shape[1]),
            n_components=int(chosen),
            explained_variance_ratio=evr.tolist(),
            cumulative_explained_variance=np.cumsum(evr).tolist(),
        )

        return self

    def _check_fitted(self) -> None:
        if (
            self.scaler_ is None
            or self.pca_ is None
            or self.reference_distances_ is None
            or self.component_std_ is None
        ):
            raise RuntimeError("Modelo ainda não foi ajustado. Execute fit().")

    def _prepare_for_transform(self, df: pd.DataFrame) -> pd.DataFrame:
        self._check_fitted()
        base = _normalizar_colunas(df)

        missing = [c for c in self.feature_names_ if c not in base.columns]
        if missing:
            raise ValueError("Features ausentes: " + ", ".join(missing))

        X = base[self.feature_names_].copy()
        X = X.replace([np.inf, -np.inf], np.nan)

        for i, c in enumerate(self.feature_names_):
            X[c] = pd.to_numeric(X[c], errors="coerce")
            X[c] = X[c].fillna(float(self.scaler_.mean_[i]))

        return X.astype(float)

    def transform(self, df: pd.DataFrame) -> pd.DataFrame:
        X = self._prepare_for_transform(df)

        Xz = self.scaler_.transform(X)
        pc = self.pca_.transform(Xz)

        cols = [f"PC{i+1}" for i in range(pc.shape[1])]
        out = pd.DataFrame(pc, columns=cols, index=df.index)

        distance = np.sqrt(
            np.sum((pc / self.component_std_) ** 2, axis=1)
        )

        percentile = _percentile_linear(
            self.reference_distances_,
            distance,
        )

        out["pca_distance"] = distance
        out["indice_atipicidade_pct"] = np.clip(
            percentile * 100.0,
            0.0,
            100.0,
        )
        out["score_condicao_ambiental"] = np.clip(
            100.0 - out["indice_atipicidade_pct"],
            0.0,
            100.0,
        )

        def faixa(score: float) -> str:
            if score >= 75:
                return "muito_proxima_do_padrao"
            if score >= 50:
                return "proxima_do_padrao"
            if score >= 25:
                return "afastada_do_padrao"
            return "muito_afastada_do_padrao"

        out["faixa_condicao"] = [
            faixa(float(s))
            for s in out["score_condicao_ambiental"]
        ]

        return out

    def predict_one(self, features: Dict[str, Any]) -> Dict[str, Any]:
        result = self.transform(
            pd.DataFrame([features])
        ).iloc[0].to_dict()

        return {
            k: (
                float(v)
                if isinstance(v, (np.floating, np.integer))
                else v
            )
            for k, v in result.items()
        }

    def loadings(self) -> pd.DataFrame:
        self._check_fitted()

        cols = [
            f"PC{i+1}"
            for i in range(self.pca_.n_components_)
        ]

        return pd.DataFrame(
            self.pca_.components_.T,
            index=self.feature_names_,
            columns=cols,
        )

    def top_loadings(self, n: int = 8) -> pd.DataFrame:
        load = self.loadings()
        rows = []

        for pc in load.columns:
            serie = load[pc]
            top = serie.reindex(
                serie.abs().sort_values(ascending=False).index
            ).head(n)

            for feature, value in top.items():
                rows.append(
                    {
                        "component": pc,
                        "feature": feature,
                        "loading": float(value),
                        "abs_loading": float(abs(value)),
                    }
                )

        return pd.DataFrame(rows)

    def explained_variance(self) -> pd.DataFrame:
        self._check_fitted()

        ratios = self.pca_.explained_variance_ratio_

        return pd.DataFrame(
            {
                "component": [
                    f"PC{i+1}"
                    for i in range(len(ratios))
                ],
                "explained_variance_ratio": ratios,
                "cumulative_explained_variance": np.cumsum(ratios),
            }
        )

    def save(self, path: str | Path) -> None:
        self._check_fitted()
        joblib.dump(self, Path(path))

    @staticmethod
    def load(path: str | Path) -> "EnvironmentalPCAModel":
        obj = joblib.load(Path(path))

        if not isinstance(obj, EnvironmentalPCAModel):
            raise TypeError(
                "O arquivo não contém EnvironmentalPCAModel."
            )

        return obj
