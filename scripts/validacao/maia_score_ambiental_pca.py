"""
MAIA — Pipeline Ambiental completo em UM arquivo

Você informa latitude e longitude. O script:

1. busca histórico REAL do local;
2. coleta Sentinel-1;
3. coleta Sentinel-2;
4. coleta clima histórico no Open-Meteo;
5. coleta JRC, SRTM e SoilGrids;
6. integra as fontes;
7. separa a observação mais recente;
8. treina o PCA somente com o histórico anterior;
9. calcula o score da observação mais recente;
10. salva o modelo treinado.

Uso:

1. Edite o bloco "CONFIGURAÇÃO DO TESTE" no início do arquivo.
2. Rode:

    python scripts/validacao/maia_score_ambiental.py

Dependências:

    python -m pip install earthengine-api requests python-dotenv pandas numpy \
        scikit-learn joblib

No .env:

    GEE_PROJECT_ID=seu-projeto-google-cloud

Antes da primeira execução:

    earthengine authenticate
    earthengine set_project SEU_GEE_PROJECT_ID

IMPORTANTE
----------
O score mede proximidade ao padrão histórico aprendido para o local.
Ele NÃO é probabilidade de risco, sinistro, falha ou perigo.
"""

from __future__ import annotations

import json
import os
import sys
from dataclasses import dataclass
from pathlib import Path
from typing import Any, Dict, List, Optional

import ee
import joblib
import numpy as np
import pandas as pd
import requests
from dotenv import load_dotenv
from sklearn.decomposition import PCA
from sklearn.preprocessing import StandardScaler



# ============================================================
# CONFIGURAÇÃO DO TESTE — ALTERE SOMENTE AQUI
# ============================================================

NOME_LOCAL = "FAZENDA_TESTE"

LATITUDE = -19.7472
LONGITUDE = -47.9381

# Se quiser um período exato, preencha as duas datas:
DATA_INICIO = "2026-08-15"          # Exemplo: "2025-01-01"
DATA_FIM = "2026-09-15"             # Exemplo: "2026-09-15"

# Se DATA_INICIO ficar como None, usa essa quantidade de dias:
DIAS_HISTORICO = 365

# Raio da área analisada em metros:
AOI_BUFFER_M = 500

# Onde salvar o modelo treinado.
# None = salva automaticamente em machine_learning/artifacts/
CAMINHO_MODELO = None

# ============================================================
# 0. CONFIGURAÇÕES GERAIS
# ============================================================

OPEN_METEO_ARCHIVE_URL = "https://archive-api.open-meteo.com/v1/archive"

S2_TOLERANCIA_DIAS = 5
MAX_CLOUD_SCENE_PERCENT = 70

MIN_VALID_PIXELS_S1 = 100
MIN_VALID_PIXELS_S2 = 30

AOI_BUFFER_M_PADRAO = 500


# ============================================================
# 1. MODELO PCA — EMBUTIDO NO MESMO ARQUIVO
# ============================================================

COLUNAS_CONTROLE = {
    "farm_latitude",
    "farm_longitude",
    "aoi_buffer_m",
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
    "farm_id",
    "data_observacao",
    "latitude",
    "longitude",
}


def normalizar_colunas(df: pd.DataFrame) -> pd.DataFrame:
    out = df.copy()
    out.columns = [
        str(c).strip().lower().replace(" ", "_")
        for c in out.columns
    ]
    return out


def percentile_empirico(
    referencia: np.ndarray,
    valores: np.ndarray,
) -> np.ndarray:
    ref = np.sort(np.asarray(referencia, dtype=float))

    if ref.size == 0:
        return np.zeros_like(
            np.asarray(valores, dtype=float)
        )

    idx = np.searchsorted(
        ref,
        np.asarray(valores, dtype=float),
        side="right",
    )

    return idx / ref.size


@dataclass
class PCAFitSummary:
    n_rows: int
    n_features: int
    n_components: int
    explained_variance_ratio: List[float]
    cumulative_explained_variance: List[float]


class EnvironmentalPCAModel:

    def __init__(
        self,
        explained_variance_target: float = 0.90,
        min_components: int = 2,
        max_components: Optional[int] = None,
    ):
        self.explained_variance_target = float(
            explained_variance_target
        )
        self.min_components = int(
            min_components
        )
        self.max_components = max_components

        self.feature_names_: List[str] = []
        self.constant_features_: List[str] = []

        self.scaler_: Optional[
            StandardScaler
        ] = None

        self.pca_: Optional[
            PCA
        ] = None

        self.reference_distances_: Optional[
            np.ndarray
        ] = None

        self.component_std_: Optional[
            np.ndarray
        ] = None

        self.fit_summary_: Optional[
            PCAFitSummary
        ] = None

    def _selecionar_features(
        self,
        df: pd.DataFrame,
    ) -> pd.DataFrame:

        base = normalizar_colunas(df)

        numeric = base.select_dtypes(
            include=[np.number]
        ).copy()

        remover = [
            c
            for c in numeric.columns
            if (
                c in COLUNAS_CONTROLE
                or c in COLUNAS_NAO_FEATURE
            )
        ]

        numeric = numeric.drop(
            columns=remover,
            errors="ignore",
        )

        numeric = numeric.replace(
            [np.inf, -np.inf],
            np.nan,
        )

        numeric = numeric.dropna(
            axis=1,
            how="all",
        )

        for coluna in numeric.columns:

            serie = pd.to_numeric(
                numeric[coluna],
                errors="coerce",
            )

            mediana = serie.median()

            if pd.notna(mediana):
                numeric[coluna] = (
                    serie.fillna(mediana)
                )

        numeric = numeric.dropna(
            axis=1,
            how="any",
        )

        if numeric.empty:
            raise ValueError(
                "Nenhuma feature numérica válida."
            )

        return numeric.astype(float)

    def fit(
        self,
        df: pd.DataFrame,
    ) -> "EnvironmentalPCAModel":

        X = self._selecionar_features(
            df
        )

        variancias = X.var(
            ddof=0
        )

        self.constant_features_ = (
            variancias[
                variancias <= 1e-10
            ]
            .index
            .tolist()
        )

        if self.constant_features_:

            X = X.drop(
                columns=self.constant_features_
            )

        if X.shape[1] < 2:
            raise ValueError(
                "PCA precisa de pelo menos "
                "2 features com variância."
            )

        if len(X) < 3:
            raise ValueError(
                "PCA precisa de pelo menos "
                "3 observações."
            )

        self.feature_names_ = (
            X.columns.tolist()
        )

        self.scaler_ = StandardScaler()

        Xz = self.scaler_.fit_transform(
            X
        )

        max_allowed = min(
            Xz.shape[0],
            Xz.shape[1],
        )

        if self.max_components is not None:
            max_allowed = min(
                max_allowed,
                int(self.max_components),
            )

        pca_full = PCA(
            n_components=max_allowed
        )

        pca_full.fit(Xz)

        cumulative = np.cumsum(
            pca_full.explained_variance_ratio_
        )

        chosen = int(
            np.searchsorted(
                cumulative,
                self.explained_variance_target,
                side="left",
            )
            + 1
        )

        chosen = max(
            min(
                self.min_components,
                max_allowed,
            ),
            chosen,
        )

        chosen = min(
            chosen,
            max_allowed,
        )

        self.pca_ = PCA(
            n_components=chosen
        )

        scores = self.pca_.fit_transform(
            Xz
        )

        component_std = scores.std(
            axis=0,
            ddof=0,
        )

        component_std[
            component_std <= 1e-12
        ] = 1.0

        self.component_std_ = (
            component_std
        )

        distances = np.sqrt(
            np.sum(
                (
                    scores
                    / component_std
                )
                ** 2,
                axis=1,
            )
        )

        self.reference_distances_ = (
            np.sort(distances)
        )

        evr = (
            self.pca_
            .explained_variance_ratio_
        )

        self.fit_summary_ = (
            PCAFitSummary(
                n_rows=int(
                    X.shape[0]
                ),
                n_features=int(
                    X.shape[1]
                ),
                n_components=int(
                    chosen
                ),
                explained_variance_ratio=(
                    evr.tolist()
                ),
                cumulative_explained_variance=(
                    np.cumsum(evr).tolist()
                ),
            )
        )

        return self

    def _check_fitted(
        self,
    ) -> None:

        if (
            self.scaler_ is None
            or self.pca_ is None
            or self.reference_distances_ is None
            or self.component_std_ is None
        ):
            raise RuntimeError(
                "Modelo ainda não treinado."
            )

    def transform(
        self,
        df: pd.DataFrame,
    ) -> pd.DataFrame:

        self._check_fitted()

        base = normalizar_colunas(
            df
        )

        faltantes = [
            c
            for c in self.feature_names_
            if c not in base.columns
        ]

        if faltantes:
            raise ValueError(
                "Features ausentes na inferência: "
                + ", ".join(faltantes)
            )

        X = base[
            self.feature_names_
        ].copy()

        X = X.replace(
            [np.inf, -np.inf],
            np.nan,
        )

        for i, coluna in enumerate(
            self.feature_names_
        ):

            X[coluna] = pd.to_numeric(
                X[coluna],
                errors="coerce",
            )

            X[coluna] = X[
                coluna
            ].fillna(
                float(
                    self.scaler_.mean_[i]
                )
            )

        Xz = self.scaler_.transform(
            X
        )

        pc = self.pca_.transform(
            Xz
        )

        cols = [
            f"PC{i+1}"
            for i in range(
                pc.shape[1]
            )
        ]

        out = pd.DataFrame(
            pc,
            columns=cols,
            index=df.index,
        )

        distance = np.sqrt(
            np.sum(
                (
                    pc
                    / self.component_std_
                )
                ** 2,
                axis=1,
            )
        )

        percentile = (
            percentile_empirico(
                self.reference_distances_,
                distance,
            )
        )

        out[
            "pca_distance"
        ] = distance

        out[
            "indice_atipicidade_pct"
        ] = np.clip(
            percentile * 100.0,
            0.0,
            100.0,
        )

        out[
            "score_condicao_ambiental"
        ] = np.clip(
            100.0
            - out[
                "indice_atipicidade_pct"
            ],
            0.0,
            100.0,
        )

        def faixa(score: float) -> str:

            if score >= 75:
                return (
                    "muito_proxima_do_padrao"
                )

            if score >= 50:
                return (
                    "proxima_do_padrao"
                )

            if score >= 25:
                return (
                    "afastada_do_padrao"
                )

            return (
                "muito_afastada_do_padrao"
            )

        out[
            "faixa_condicao"
        ] = [
            faixa(float(s))
            for s
            in out[
                "score_condicao_ambiental"
            ]
        ]

        return out

    def predict_one(
        self,
        features: Dict[str, Any],
    ) -> Dict[str, Any]:

        result = self.transform(
            pd.DataFrame(
                [features]
            )
        ).iloc[0].to_dict()

        return {
            k: (
                float(v)
                if isinstance(
                    v,
                    (
                        np.floating,
                        np.integer,
                    ),
                )
                else v
            )
            for k, v
            in result.items()
        }

    def save(
        self,
        path: str | Path,
    ) -> None:

        self._check_fitted()

        joblib.dump(
            self,
            Path(path),
        )


# ============================================================
# 2. CONFIGURAÇÃO INTERNA
# ============================================================

class Configuracao:
    pass


def parse_args():
    """
    Mantém o restante do pipeline igual, mas agora os valores vêm
    diretamente do bloco CONFIGURAÇÃO DO TESTE no início do arquivo.
    """

    args = Configuracao()

    args.latitude = float(LATITUDE)
    args.longitude = float(LONGITUDE)
    args.nome = NOME_LOCAL
    args.inicio = DATA_INICIO
    args.fim = DATA_FIM
    args.dias = int(DIAS_HISTORICO)
    args.buffer = int(AOI_BUFFER_M)
    args.salvar_modelo = CAMINHO_MODELO

    return args


# ============================================================
# 3. EARTH ENGINE
# ============================================================

def iniciar_gee():

    gee_project_id = os.getenv(
        "GEE_PROJECT_ID"
    )

    if not gee_project_id:

        raise RuntimeError(
            "GEE_PROJECT_ID não encontrado "
            "no .env."
        )

    try:

        ee.Initialize(
            project=gee_project_id
        )

    except Exception as exc:

        raise RuntimeError(
            "Earth Engine não inicializou. "
            "Execute earthengine authenticate "
            "e earthengine set_project. "
            f"Erro original: {exc!r}"
        ) from exc


# ============================================================
# 4. SENTINEL-1
# ============================================================

def obter_sentinel1(
    aoi,
    inicio,
    fim_exclusivo,
):

    return (
        ee.ImageCollection(
            "COPERNICUS/S1_GRD"
        )
        .filterBounds(aoi)
        .filterDate(
            inicio,
            fim_exclusivo,
        )
        .filter(
            ee.Filter.eq(
                "instrumentMode",
                "IW",
            )
        )
        .filter(
            ee.Filter.eq(
                "resolution_meters",
                10,
            )
        )
        .filter(
            ee.Filter.listContains(
                "transmitterReceiverPolarisation",
                "VV",
            )
        )
        .filter(
            ee.Filter.listContains(
                "transmitterReceiverPolarisation",
                "VH",
            )
        )
        .select(
            [
                "VV",
                "VH",
                "angle",
            ]
        )
    )


def extrair_sentinel1(
    colecao,
    aoi,
):

    reducer = (
        ee.Reducer.mean()
        .combine(
            ee.Reducer.median(),
            sharedInputs=True,
        )
        .combine(
            ee.Reducer.stdDev(),
            sharedInputs=True,
        )
        .combine(
            ee.Reducer.count(),
            sharedInputs=True,
        )
    )

    def converter(img):

        vv = img.select("VV")
        vh = img.select("VH")

        vv_minus_vh = (
            vv.subtract(vh)
            .rename(
                "VV_minus_VH"
            )
        )

        imagem = (
            vv
            .addBands(vh)
            .addBands(
                vv_minus_vh
            )
            .addBands(
                img.select("angle")
            )
        )

        stats = imagem.reduceRegion(
            reducer=reducer,
            geometry=aoi,
            scale=10,
            bestEffort=True,
            maxPixels=10_000_000,
        )

        return ee.Feature(
            None,
            {
                "date": (
                    img.date()
                    .format(
                        "YYYY-MM-dd HH:mm:ss"
                    )
                ),
                "orbit_pass": img.get(
                    "orbitProperties_pass"
                ),
                "relative_orbit": img.get(
                    "relativeOrbitNumber_start"
                ),
                "platform": img.get(
                    "platform_number"
                ),
                "VV_mean_db": stats.get(
                    "VV_mean"
                ),
                "VV_median_db": stats.get(
                    "VV_median"
                ),
                "VV_std_db": stats.get(
                    "VV_stdDev"
                ),
                "VH_mean_db": stats.get(
                    "VH_mean"
                ),
                "VH_median_db": stats.get(
                    "VH_median"
                ),
                "VH_std_db": stats.get(
                    "VH_stdDev"
                ),
                "VV_minus_VH_mean_db": (
                    stats.get(
                        "VV_minus_VH_mean"
                    )
                ),
                "angle_mean_deg": stats.get(
                    "angle_mean"
                ),
                "valid_pixels_s1": stats.get(
                    "VV_count"
                ),
            },
        )

    info = (
        ee.FeatureCollection(
            colecao.map(
                converter
            )
        )
        .getInfo()
    )

    df = pd.DataFrame(
        [
            f["properties"]
            for f
            in info.get(
                "features",
                []
            )
        ]
    )

    if df.empty:
        return df

    df["date"] = pd.to_datetime(
        df["date"],
        errors="coerce",
    )

    for coluna in df.columns:

        if coluna not in {
            "date",
            "orbit_pass",
            "platform",
        }:

            df[coluna] = pd.to_numeric(
                df[coluna],
                errors="coerce",
            )

    df = (
        df
        .dropna(
            subset=["date"]
        )
        .sort_values("date")
        .reset_index(drop=True)
    )

    df[
        "VV_baseline_median_db"
    ] = (
        df
        .groupby(
            "orbit_pass"
        )[
            "VV_mean_db"
        ]
        .transform("median")
    )

    df[
        "VH_baseline_median_db"
    ] = (
        df
        .groupby(
            "orbit_pass"
        )[
            "VH_mean_db"
        ]
        .transform("median")
    )

    df[
        "VV_anomaly_db"
    ] = (
        df["VV_mean_db"]
        - df[
            "VV_baseline_median_db"
        ]
    )

    df[
        "VH_anomaly_db"
    ] = (
        df["VH_mean_db"]
        - df[
            "VH_baseline_median_db"
        ]
    )

    return df


# ============================================================
# 5. SENTINEL-2
# ============================================================

def mascarar_s2_scl(img):

    scl = img.select("SCL")

    mascara = (
        scl.neq(0)
        .And(
            scl.neq(1)
        )
        .And(
            scl.neq(3)
        )
        .And(
            scl.neq(8)
        )
        .And(
            scl.neq(9)
        )
        .And(
            scl.neq(10)
        )
        .And(
            scl.neq(11)
        )
    )

    return img.updateMask(
        mascara
    )


def adicionar_indices_s2(
    img,
):

    ndwi = (
        img.normalizedDifference(
            [
                "B3",
                "B8",
            ]
        )
        .rename("NDWI")
    )

    ndmi = (
        img.normalizedDifference(
            [
                "B8",
                "B11",
            ]
        )
        .rename("NDMI")
    )

    ndwi_positive = (
        ndwi.gt(0)
        .rename(
            "NDWI_positive"
        )
    )

    return (
        img
        .addBands(ndwi)
        .addBands(ndmi)
        .addBands(
            ndwi_positive
        )
    )


def obter_sentinel2(
    aoi,
    inicio,
    fim_exclusivo,
):

    return (
        ee.ImageCollection(
            "COPERNICUS/S2_SR_HARMONIZED"
        )
        .filterBounds(aoi)
        .filterDate(
            inicio,
            fim_exclusivo,
        )
        .filter(
            ee.Filter.lt(
                "CLOUDY_PIXEL_PERCENTAGE",
                MAX_CLOUD_SCENE_PERCENT,
            )
        )
        .map(
            mascarar_s2_scl
        )
        .map(
            adicionar_indices_s2
        )
    )


def extrair_sentinel2(
    colecao,
    aoi,
):

    reducer = (
        ee.Reducer.mean()
        .combine(
            ee.Reducer.median(),
            sharedInputs=True,
        )
        .combine(
            ee.Reducer.stdDev(),
            sharedInputs=True,
        )
        .combine(
            ee.Reducer.count(),
            sharedInputs=True,
        )
    )

    def converter(img):

        stats = (
            img
            .select(
                [
                    "NDWI",
                    "NDMI",
                    "NDWI_positive",
                ]
            )
            .reduceRegion(
                reducer=reducer,
                geometry=aoi,
                scale=20,
                bestEffort=True,
                maxPixels=10_000_000,
            )
        )

        return ee.Feature(
            None,
            {
                "date": (
                    img.date()
                    .format(
                        "YYYY-MM-dd HH:mm:ss"
                    )
                ),
                "cloud_pct_scene": img.get(
                    "CLOUDY_PIXEL_PERCENTAGE"
                ),
                "NDWI_mean": stats.get(
                    "NDWI_mean"
                ),
                "NDWI_median": stats.get(
                    "NDWI_median"
                ),
                "NDWI_std": stats.get(
                    "NDWI_stdDev"
                ),
                "NDMI_mean": stats.get(
                    "NDMI_mean"
                ),
                "NDMI_median": stats.get(
                    "NDMI_median"
                ),
                "NDMI_std": stats.get(
                    "NDMI_stdDev"
                ),
                "NDWI_positive_fraction": (
                    stats.get(
                        "NDWI_positive_mean"
                    )
                ),
                "valid_pixels_s2": stats.get(
                    "NDWI_count"
                ),
            },
        )

    info = (
        ee.FeatureCollection(
            colecao.map(
                converter
            )
        )
        .getInfo()
    )

    df = pd.DataFrame(
        [
            f["properties"]
            for f
            in info.get(
                "features",
                []
            )
        ]
    )

    if df.empty:
        return df

    df["date"] = pd.to_datetime(
        df["date"],
        errors="coerce",
    )

    for coluna in df.columns:

        if coluna != "date":

            df[coluna] = pd.to_numeric(
                df[coluna],
                errors="coerce",
            )

    return (
        df
        .dropna(
            subset=["date"]
        )
        .sort_values("date")
        .reset_index(drop=True)
    )


# ============================================================
# 6. OPEN-METEO HISTÓRICO
# ============================================================

def buscar_open_meteo(
    latitude,
    longitude,
    inicio,
    fim,
):

    resposta = requests.get(
        OPEN_METEO_ARCHIVE_URL,
        params={
            "latitude": latitude,
            "longitude": longitude,
            "start_date": inicio,
            "end_date": fim,
            "daily": (
                "precipitation_sum,"
                "et0_fao_evapotranspiration"
            ),
            "hourly": (
                "soil_moisture_0_to_7cm"
            ),
            "timezone": "auto",
        },
        timeout=60,
    )

    resposta.raise_for_status()

    return resposta.json()


def montar_clima(
    payload,
    data_inicio_real,
):

    daily = payload.get(
        "daily",
        {},
    )

    df_daily = pd.DataFrame(
        {
            "date": pd.to_datetime(
                daily.get(
                    "time",
                    [],
                ),
                errors="coerce",
            ),
            "precipitation_mm": (
                pd.to_numeric(
                    pd.Series(
                        daily.get(
                            "precipitation_sum",
                            [],
                        )
                    ),
                    errors="coerce",
                )
            ),
            "et0_mm": (
                pd.to_numeric(
                    pd.Series(
                        daily.get(
                            "et0_fao_evapotranspiration",
                            [],
                        )
                    ),
                    errors="coerce",
                )
            ),
        }
    )

    df_daily = (
        df_daily
        .sort_values("date")
        .reset_index(drop=True)
    )

    for janela in [
        3,
        7,
        14,
    ]:

        df_daily[
            f"rain_{janela}d_mm"
        ] = (
            df_daily[
                "precipitation_mm"
            ]
            .rolling(
                window=janela,
                min_periods=1,
            )
            .sum()
        )

    evento_chuva = (
        df_daily[
            "precipitation_mm"
        ]
        >= 1.0
    )

    ultima_chuva = (
        df_daily["date"]
        .where(
            evento_chuva
        )
        .ffill()
    )

    df_daily[
        "days_since_rain_ge_1mm"
    ] = (
        df_daily["date"]
        - ultima_chuva
    ).dt.days

    hourly = payload.get(
        "hourly",
        {},
    )

    df_hourly = pd.DataFrame(
        {
            "datetime": pd.to_datetime(
                hourly.get(
                    "time",
                    [],
                ),
                errors="coerce",
            ),
            "soil_moisture_0_7cm_m3_m3": (
                pd.to_numeric(
                    pd.Series(
                        hourly.get(
                            "soil_moisture_0_to_7cm",
                            [],
                        )
                    ),
                    errors="coerce",
                )
            ),
        }
    )

    if not df_hourly.empty:

        df_hourly["date"] = (
            df_hourly[
                "datetime"
            ]
            .dt
            .normalize()
        )

        df_soil_daily = (
            df_hourly
            .groupby(
                "date",
                as_index=False,
            )
            .agg(
                soil_moisture_0_7cm_mean_m3_m3=(
                    "soil_moisture_0_7cm_m3_m3",
                    "mean",
                ),
                soil_moisture_0_7cm_min_m3_m3=(
                    "soil_moisture_0_7cm_m3_m3",
                    "min",
                ),
                soil_moisture_0_7cm_max_m3_m3=(
                    "soil_moisture_0_7cm_m3_m3",
                    "max",
                ),
            )
        )

    else:

        df_soil_daily = (
            pd.DataFrame(
                columns=[
                    "date",
                    "soil_moisture_0_7cm_mean_m3_m3",
                    "soil_moisture_0_7cm_min_m3_m3",
                    "soil_moisture_0_7cm_max_m3_m3",
                ]
            )
        )

    df = df_daily.merge(
        df_soil_daily,
        on="date",
        how="left",
    )

    col_umidade = (
        "soil_moisture_0_7cm_mean_m3_m3"
    )

    if (
        col_umidade in df.columns
        and df[
            col_umidade
        ].notna().any()
    ):

        mediana = df[
            col_umidade
        ].median()

        df[
            "soil_moisture_anomaly_m3_m3"
        ] = (
            df[col_umidade]
            - mediana
        )

    return (
        df[
            df["date"]
            >= data_inicio_real
        ]
        .sort_values("date")
        .reset_index(drop=True)
    )


# ============================================================
# 7. JRC
# ============================================================

def extrair_jrc(
    aoi,
):

    gsw = ee.Image(
        "JRC/GSW1_4/GlobalSurfaceWater"
    )

    water_any = (
        gsw.select(
            "max_extent"
        )
        .unmask(0)
        .eq(1)
    )

    water_recurrent = (
        gsw.select(
            "occurrence"
        )
        .unmask(0)
        .gte(50)
    )

    scale = 30

    distance_any = (
        water_any
        .fastDistanceTransform(
            neighborhood=512
        )
        .sqrt()
        .multiply(scale)
        .rename(
            "distance_any_water_m"
        )
    )

    distance_recurrent = (
        water_recurrent
        .fastDistanceTransform(
            neighborhood=512
        )
        .sqrt()
        .multiply(scale)
        .rename(
            "distance_recurrent_water_m"
        )
    )

    img = (
        gsw
        .select(
            [
                "occurrence",
                "seasonality",
                "recurrence",
            ]
        )
        .addBands(
            distance_any
        )
        .addBands(
            distance_recurrent
        )
    )

    stats = img.reduceRegion(
        reducer=(
            ee.Reducer.mean()
            .combine(
                ee.Reducer.min(),
                sharedInputs=True,
            )
            .combine(
                ee.Reducer.max(),
                sharedInputs=True,
            )
        ),
        geometry=aoi,
        scale=scale,
        bestEffort=True,
        maxPixels=10_000_000,
    ).getInfo()

    return {
        "water_occurrence_mean_pct": (
            stats.get(
                "occurrence_mean"
            )
        ),
        "water_occurrence_max_pct": (
            stats.get(
                "occurrence_max"
            )
        ),
        "water_seasonality_mean_months": (
            stats.get(
                "seasonality_mean"
            )
        ),
        "water_recurrence_mean_pct": (
            stats.get(
                "recurrence_mean"
            )
        ),
        "distance_any_water_min_m": (
            stats.get(
                "distance_any_water_m_min"
            )
        ),
        "distance_recurrent_water_min_m": (
            stats.get(
                "distance_recurrent_water_m_min"
            )
        ),
    }


# ============================================================
# 8. TOPOGRAFIA
# ============================================================

def extrair_topografia(
    aoi,
    ponto,
):

    srtm = (
        ee.Image(
            "USGS/SRTMGL1_003"
        )
        .select(
            "elevation"
        )
    )

    slope = (
        ee.Terrain.slope(
            srtm
        )
        .rename(
            "slope_deg"
        )
    )

    contexto = ponto.buffer(
        1000
    )

    reducer = (
        ee.Reducer.mean()
        .combine(
            ee.Reducer.minMax(),
            sharedInputs=True,
        )
    )

    aoi_stats = (
        srtm
        .rename(
            "elevation"
        )
        .addBands(
            slope
        )
        .reduceRegion(
            reducer=reducer,
            geometry=aoi,
            scale=30,
            bestEffort=True,
            maxPixels=10_000_000,
        )
        .getInfo()
    )

    ctx_stats = (
        srtm
        .rename(
            "elevation"
        )
        .addBands(
            slope
        )
        .reduceRegion(
            reducer=reducer,
            geometry=contexto,
            scale=30,
            bestEffort=True,
            maxPixels=10_000_000,
        )
        .getInfo()
    )

    out = {
        "elevation_aoi_mean_m": (
            aoi_stats.get(
                "elevation_mean"
            )
        ),
        "elevation_aoi_min_m": (
            aoi_stats.get(
                "elevation_min"
            )
        ),
        "elevation_aoi_max_m": (
            aoi_stats.get(
                "elevation_max"
            )
        ),
        "slope_aoi_mean_deg": (
            aoi_stats.get(
                "slope_deg_mean"
            )
        ),
        "slope_aoi_max_deg": (
            aoi_stats.get(
                "slope_deg_max"
            )
        ),
        "elevation_1km_mean_m": (
            ctx_stats.get(
                "elevation_mean"
            )
        ),
        "elevation_1km_min_m": (
            ctx_stats.get(
                "elevation_min"
            )
        ),
        "elevation_1km_max_m": (
            ctx_stats.get(
                "elevation_max"
            )
        ),
        "slope_1km_mean_deg": (
            ctx_stats.get(
                "slope_deg_mean"
            )
        ),
    }

    if (
        out[
            "elevation_aoi_mean_m"
        ] is not None
        and out[
            "elevation_1km_mean_m"
        ] is not None
    ):

        out[
            "relative_elevation_aoi_vs_1km_m"
        ] = (
            out[
                "elevation_aoi_mean_m"
            ]
            - out[
                "elevation_1km_mean_m"
            ]
        )

    if (
        out[
            "elevation_1km_max_m"
        ] is not None
        and out[
            "elevation_1km_min_m"
        ] is not None
    ):

        out[
            "local_relief_1km_m"
        ] = (
            out[
                "elevation_1km_max_m"
            ]
            - out[
                "elevation_1km_min_m"
            ]
        )

    return out


# ============================================================
# 9. SOILGRIDS
# ============================================================

SOILGRIDS_CONFIG = {
    "clay_pct": {
        "asset": "clay_mean",
        "divisor": 10.0,
    },
    "sand_pct": {
        "asset": "sand_mean",
        "divisor": 10.0,
    },
    "silt_pct": {
        "asset": "silt_mean",
        "divisor": 10.0,
    },
    "bulk_density_kg_dm3": {
        "asset": "bdod_mean",
        "divisor": 100.0,
    },
    "soc_g_kg": {
        "asset": "soc_mean",
        "divisor": 10.0,
    },
}


def bandas_superficiais(
    bandas,
):

    desejadas = [
        b
        for b in bandas
        if (
            "0-5cm" in b
            or "5-15cm" in b
        )
    ]

    if len(desejadas) >= 2:
        return desejadas[:2]

    return bandas[:2]


def extrair_soilgrids(
    aoi,
):

    resultado = {}

    for (
        feature_name,
        config,
    ) in SOILGRIDS_CONFIG.items():

        asset_id = (
            "projects/soilgrids-isric/"
            + config["asset"]
        )

        imagem = ee.Image(
            asset_id
        )

        bandas = (
            imagem
            .bandNames()
            .getInfo()
        )

        selecionadas = (
            bandas_superficiais(
                bandas
            )
        )

        stats = (
            imagem
            .select(
                selecionadas
            )
            .reduceRegion(
                reducer=(
                    ee.Reducer.mean()
                ),
                geometry=aoi,
                scale=250,
                bestEffort=True,
                maxPixels=10_000_000,
            )
            .getInfo()
        )

        for (
            banda,
            valor,
        ) in stats.items():

            chave = (
                f"{feature_name}__{banda}"
            )

            resultado[chave] = (
                np.nan
                if valor is None
                else (
                    float(valor)
                    / config["divisor"]
                )
            )

    return resultado


# ============================================================
# 10. INTEGRAÇÃO
# ============================================================

def integrar(
    df_s1,
    df_s2,
    df_clima,
    jrc,
    topo,
    soil,
    latitude,
    longitude,
    nome,
    buffer_m,
):

    if df_s1.empty:
        raise ValueError(
            "Nenhuma observação Sentinel-1."
        )

    base = df_s1.copy()

    base[
        "date_day"
    ] = (
        base["date"]
        .dt
        .normalize()
    )

    clima = df_clima.copy()

    clima[
        "date_day"
    ] = (
        pd.to_datetime(
            clima["date"]
        )
        .dt
        .normalize()
    )

    clima = clima.drop(
        columns=["date"],
        errors="ignore",
    )

    base = base.merge(
        clima,
        on="date_day",
        how="left",
    )

    if not df_s2.empty:

        optico = (
            df_s2
            .rename(
                columns={
                    "date": "s2_date"
                }
            )
            .sort_values(
                "s2_date"
            )
        )

        base = pd.merge_asof(
            base.sort_values(
                "date"
            ),
            optico,
            left_on="date",
            right_on="s2_date",
            direction="nearest",
            tolerance=pd.Timedelta(
                days=S2_TOLERANCIA_DIAS
            ),
            suffixes=(
                "_s1",
                "_s2",
            ),
        )

        base[
            "s2_time_distance_days"
        ] = (
            (
                base["date"]
                - base["s2_date"]
            )
            .abs()
            .dt
            .total_seconds()
            / 86400.0
        )

    for (
        chave,
        valor,
    ) in jrc.items():

        base[
            f"jrc__{chave}"
        ] = valor

    for (
        chave,
        valor,
    ) in topo.items():

        base[
            f"topo__{chave}"
        ] = valor

    for (
        chave,
        valor,
    ) in soil.items():

        base[
            f"soil__{chave}"
        ] = valor

    base["farm_id"] = nome
    base["farm_latitude"] = latitude
    base["farm_longitude"] = longitude
    base["aoi_buffer_m"] = buffer_m
    base["location_precise"] = True
    base["dataset_stage"] = (
        "historico_real"
    )
    base["target_status"] = (
        "sem_target"
    )

    return (
        base
        .sort_values("date")
        .reset_index(drop=True)
    )


# ============================================================
# 11. LIMPEZA
# ============================================================

def limpar(
    df,
):

    out = normalizar_colunas(
        df
    )

    out = out.replace(
        [np.inf, -np.inf],
        np.nan,
    )

    out = (
        out
        .drop_duplicates()
        .reset_index(drop=True)
    )

    if (
        "valid_pixels_s1"
        in out.columns
    ):

        out = out[
            out[
                "valid_pixels_s1"
            ].fillna(0)
            >= MIN_VALID_PIXELS_S1
        ].copy()

    if (
        "valid_pixels_s2"
        in out.columns
    ):

        invalid_s2 = (
            out[
                "valid_pixels_s2"
            ].notna()
            & (
                out[
                    "valid_pixels_s2"
                ]
                < MIN_VALID_PIXELS_S2
            )
        )

        cols_s2 = [
            c
            for c in [
                "ndwi_mean",
                "ndwi_median",
                "ndwi_std",
                "ndmi_mean",
                "ndmi_median",
                "ndmi_std",
                "ndwi_positive_fraction",
                "valid_pixels_s2",
                "cloud_pct_scene",
                "s2_time_distance_days",
            ]
            if c in out.columns
        ]

        out.loc[
            invalid_s2,
            cols_s2,
        ] = np.nan

    return (
        out
        .sort_values("date")
        .reset_index(drop=True)
    )


# ============================================================
# 12. MAIN
# ============================================================

def main():

    args = parse_args()

    if not (
        -90 <= args.latitude <= 90
        and -180 <= args.longitude <= 180
    ):

        raise ValueError(
            "Latitude/longitude inválida."
        )

    hoje = (
        pd.Timestamp.today()
        .normalize()
    )

    if args.fim:

        data_fim = (
            pd.Timestamp(
                args.fim
            )
            .normalize()
        )

    else:

        # Evita últimos dias ainda não consolidados
        # em algumas fontes históricas.
        data_fim = (
            hoje
            - pd.Timedelta(
                days=7
            )
        )

    if args.inicio:

        data_inicio = (
            pd.Timestamp(
                args.inicio
            )
            .normalize()
        )

    else:

        data_inicio = (
            data_fim
            - pd.Timedelta(
                days=args.dias
            )
        )

    if data_fim <= data_inicio:

        raise ValueError(
            "Período inválido."
        )

    # 13 dias extras para calcular corretamente
    # a janela de chuva de 14 dias no começo da série.
    clima_inicio = (
        data_inicio
        - pd.Timedelta(
            days=13
        )
    )

    inicio_str = (
        data_inicio
        .strftime("%Y-%m-%d")
    )

    clima_inicio_str = (
        clima_inicio
        .strftime("%Y-%m-%d")
    )

    fim_str = (
        data_fim
        .strftime("%Y-%m-%d")
    )

    fim_gee = (
        data_fim
        + pd.Timedelta(
            days=1
        )
    ).strftime(
        "%Y-%m-%d"
    )

    # .env a partir da raiz atual.
    current = Path.cwd().resolve()

    env_path = (
        current
        / ".env"
    )

    if env_path.exists():

        load_dotenv(
            env_path,
            override=False,
        )

    else:

        # tenta achar .env acima
        for p in [
            current,
            *current.parents,
        ]:

            candidate = (
                p
                / ".env"
            )

            if candidate.exists():

                load_dotenv(
                    candidate,
                    override=False,
                )

                break

    iniciar_gee()

    ponto = ee.Geometry.Point(
        [
            args.longitude,
            args.latitude,
        ]
    )

    aoi = ponto.buffer(
        args.buffer
    )

    print(
        "\n"
        + "=" * 72
    )

    print(
        "MAIA — PIPELINE AMBIENTAL COMPLETO"
    )

    print(
        "=" * 72
    )

    print(
        "Local:",
        args.nome,
    )

    print(
        "Latitude:",
        args.latitude,
    )

    print(
        "Longitude:",
        args.longitude,
    )

    print(
        "Período:",
        inicio_str,
        "até",
        fim_str,
    )

    print()

    # --------------------------------------------------------
    # COLETA
    # --------------------------------------------------------

    print(
        "1/6 — Sentinel-1..."
    )

    s1 = obter_sentinel1(
        aoi,
        inicio_str,
        fim_gee,
    )

    df_s1 = extrair_sentinel1(
        s1,
        aoi,
    )

    print(
        "      observações:",
        len(df_s1),
    )

    print(
        "2/6 — Sentinel-2..."
    )

    s2 = obter_sentinel2(
        aoi,
        inicio_str,
        fim_gee,
    )

    df_s2 = extrair_sentinel2(
        s2,
        aoi,
    )

    print(
        "      observações:",
        len(df_s2),
    )

    print(
        "3/6 — Open-Meteo..."
    )

    clima_json = buscar_open_meteo(
        args.latitude,
        args.longitude,
        clima_inicio_str,
        fim_str,
    )

    df_clima = montar_clima(
        clima_json,
        data_inicio,
    )

    print(
        "      dias:",
        len(df_clima),
    )

    print(
        "4/6 — Contexto estático..."
    )

    jrc = extrair_jrc(
        aoi
    )

    topo = extrair_topografia(
        aoi,
        ponto,
    )

    soil = extrair_soilgrids(
        aoi
    )

    print(
        "5/6 — Integração..."
    )

    df = integrar(
        df_s1,
        df_s2,
        df_clima,
        jrc,
        topo,
        soil,
        args.latitude,
        args.longitude,
        args.nome,
        args.buffer,
    )

    df = limpar(
        df
    )

    print(
        "      linhas integradas:",
        len(df),
    )

    if len(df) < 4:

        raise RuntimeError(
            "Histórico insuficiente. "
            "Aumente o período com --dias 540 "
            "ou --dias 730."
        )

    # --------------------------------------------------------
    # HOLDOUT TEMPORAL
    # --------------------------------------------------------

    observacao_atual = (
        df.iloc[-1]
        .copy()
    )

    historico = (
        df.iloc[:-1]
        .copy()
    )

    print(
        "6/6 — PCA..."
    )

    print(
        "      treino:",
        len(historico),
        "observações",
    )

    print(
        "      teste:",
        observacao_atual[
            "date"
        ],
    )

    modelo = (
        EnvironmentalPCAModel(
            explained_variance_target=0.90,
            min_components=2,
        )
        .fit(
            historico
        )
    )

    resultado = (
        modelo.predict_one(
            observacao_atual.to_dict()
        )
    )

    # --------------------------------------------------------
    # SAÍDA
    # --------------------------------------------------------

    print(
        "\n"
        + "=" * 72
    )

    print(
        "RESULTADO FINAL"
    )

    print(
        "=" * 72
    )

    print(
        "Data testada:",
        observacao_atual[
            "date"
        ],
    )

    print(
        "Histórico usado no treino:",
        len(historico),
    )

    print(
        "Features usadas:",
        modelo.fit_summary_.n_features,
    )

    print(
        "Componentes PCA:",
        modelo.fit_summary_.n_components,
    )

    print()

    print(
        "SCORE DE CONDIÇÃO AMBIENTAL:",
        f"{resultado['score_condicao_ambiental']:.2f}/100",
    )

    print(
        "ATIPICIDADE:",
        f"{resultado['indice_atipicidade_pct']:.2f}%",
    )

    print(
        "FAIXA:",
        resultado[
            "faixa_condicao"
        ],
    )

    print(
        "DISTÂNCIA PCA:",
        f"{resultado['pca_distance']:.4f}",
    )

    print()

    print(
        "Interpretação: o score mede "
        "proximidade ao padrão histórico "
        "multivariado deste período."
    )

    print(
        "Não representa probabilidade "
        "de risco ou sinistro."
    )

    # --------------------------------------------------------
    # SALVA MODELO
    # --------------------------------------------------------

    if args.salvar_modelo:

        model_path = Path(
            args.salvar_modelo
        )

    else:

        safe_name = (
            args.nome
            .strip()
            .lower()
            .replace(
                " ",
                "_",
            )
        )

        model_path = (
            Path.cwd()
            / "machine_learning"
            / "artifacts"
            / (
                f"environmental_pca_"
                f"{safe_name}.joblib"
            )
        )

    model_path.parent.mkdir(
        parents=True,
        exist_ok=True,
    )

    modelo.save(
        model_path
    )

    print()

    print(
        "Modelo salvo em:"
    )

    print(
        model_path
    )


if __name__ == "__main__":
    main()
