from __future__ import annotations

from pathlib import Path
import pickle
import numpy as np
import pandas as pd
from sklearn.ensemble import IsolationForest
from sklearn.preprocessing import RobustScaler

VARIABLES = [
    "EngCoolantTemp",
    "EngOilTemp1",
    "EngOilPress",
    "ActualEngine_PercTorque",
    "EngineSpeed",
    "EngFuelRate",
    "WheelBasedVehicleSpeed",
]

LABELS = {
    "EngCoolantTemp": "Temperatura do líquido de arrefecimento",
    "EngOilTemp1": "Temperatura do óleo",
    "EngOilPress": "Pressão do óleo",
    "ActualEngine_PercTorque": "Torque do motor",
    "EngineSpeed": "RPM",
    "EngFuelRate": "Taxa de combustível",
    "WheelBasedVehicleSpeed": "Velocidade da máquina",
}


class OperationalHealthModel:
    """
    Modelo de aderência ao padrão operacional.

    Compatível com o artefato real gerado pelo notebook:
      - scaler
      - modelo
      - referencia_anomaly
      - perfil_robusto
      - demais metadados em português

    O score NÃO representa probabilidade de falha.
    """

    def __init__(self, artefato: dict):
        obrigatorias = {
            "scaler", "modelo", "referencia_anomaly", "perfil_robusto"
        }
        faltantes = obrigatorias - set(artefato)
        if faltantes:
            raise ValueError(
                "Artefato operacional incompatível. "
                f"Chaves faltantes: {sorted(faltantes)}"
            )

        self.artefato = artefato
        self.scaler = artefato["scaler"]
        self.model = artefato["modelo"]
        self.ref = np.asarray(artefato["referencia_anomaly"], dtype=float)
        self.profile = artefato["perfil_robusto"]

        self.versao = artefato.get("versao", "desconhecida")
        self.perfil_id = artefato.get("perfil_id", "desconhecido")
        self.tipo = artefato.get("tipo", "IsolationForest")
        self.janela_segundos = artefato.get("janela_segundos", 60)
        self.variaveis = artefato.get("variaveis", VARIABLES)
        self.rotulos = artefato.get("rotulos", LABELS)
        self.interpretacao = artefato.get(
            "interpretacao",
            "Aderência ao padrão operacional aprendido."
        )

        if len(self.ref) == 0:
            raise ValueError("referencia_anomaly está vazia.")

    @classmethod
    def train(
        cls,
        df: pd.DataFrame,
        perfil_id: str = "PERFIL_INDIVIDUAL",
        random_state: int = 42,
    ):
        faltantes = [v for v in VARIABLES if v not in df.columns]
        if faltantes:
            raise ValueError(
                f"Variáveis ausentes para treinamento: {faltantes}"
            )

        x = df[VARIABLES].apply(pd.to_numeric, errors="coerce").dropna()

        if len(x) < 10:
            raise ValueError(
                "Dados válidos insuficientes para treinar o perfil."
            )

        scaler = RobustScaler()
        xs = scaler.fit_transform(x)

        modelo = IsolationForest(
            n_estimators=700,
            contamination="auto",
            random_state=random_state,
            n_jobs=-1,
        )
        modelo.fit(xs)

        perfil_robusto = {}

        for coluna in VARIABLES:
            serie = x[coluna].astype(float)
            mediana = float(serie.median())
            mad = float(np.median(np.abs(serie - mediana)))
            escala = 1.4826 * mad

            if not np.isfinite(escala) or escala < 1e-9:
                desvio = float(serie.std()) if len(serie) > 1 else 1.0
                escala = desvio if np.isfinite(desvio) and desvio > 1e-9 else 1.0

            perfil_robusto[coluna] = {
                "mediana": mediana,
                "escala_robusta": float(escala),
                "p05": float(serie.quantile(0.05)),
                "p25": float(serie.quantile(0.25)),
                "p75": float(serie.quantile(0.75)),
                "p95": float(serie.quantile(0.95)),
            }

        artefato = {
            "versao": "1.0",
            "perfil_id": perfil_id,
            "tipo": "isolation_forest",
            "janela_segundos": 60,
            "variaveis": VARIABLES,
            "rotulos": LABELS,
            "scaler": scaler,
            "modelo": modelo,
            "referencia_anomaly": -modelo.score_samples(xs),
            "perfil_robusto": perfil_robusto,
            "interpretacao": (
                "Score 0-100 de aderência ao padrão operacional. "
                "Não representa probabilidade de falha."
            ),
        }

        return cls(artefato)

    def predict(self, values: dict) -> dict:
        faltantes = [v for v in VARIABLES if v not in values]
        if faltantes:
            raise ValueError(
                f"Variáveis faltantes para inferência: {faltantes}"
            )

        dados = {}
        for variavel in VARIABLES:
            try:
                dados[variavel] = float(values[variavel])
            except (TypeError, ValueError):
                raise ValueError(
                    f"Valor inválido para {variavel}: {values[variavel]!r}"
                )

        row = pd.DataFrame([dados])

        xs = self.scaler.transform(row[VARIABLES])
        anomaly = float(-self.model.score_samples(xs)[0])

        ref_ordenada = np.sort(self.ref)
        percentile = (
            np.searchsorted(ref_ordenada, anomaly, side="right")
            / len(ref_ordenada)
        )
        score = float(np.clip(100 * (1 - percentile), 0, 100))

        fatores = []

        for variavel in VARIABLES:
            if variavel not in self.profile:
                continue

            p = self.profile[variavel]

            mediana = float(p["mediana"])
            escala = float(p["escala_robusta"])
            p05 = float(p["p05"])
            p95 = float(p["p95"])
            valor = dados[variavel]

            if not np.isfinite(escala) or escala < 1e-9:
                escala = 1.0

            desvio_robusto = (valor - mediana) / escala

            if valor > mediana:
                direcao = "acima"
            elif valor < mediana:
                direcao = "abaixo"
            else:
                direcao = "igual"

            fora_faixa = valor < p05 or valor > p95

            fatores.append({
                "variable": variavel,
                "label": self.rotulos.get(
                    variavel, LABELS.get(variavel, variavel)
                ),
                "value": valor,
                "reference_median": mediana,
                "reference_p05": p05,
                "reference_p95": p95,
                "robust_deviation": round(float(desvio_robusto), 4),
                "direction": direcao,
                "outside_band": bool(fora_faixa),
            })

        fatores.sort(
            key=lambda f: abs(f["robust_deviation"]),
            reverse=True,
        )

        relevantes = [
            f for f in fatores
            if abs(f["robust_deviation"]) >= 1.5
            or f["outside_band"]
        ][:4]

        if score >= 75:
            status = "ADERENTE"
        elif score >= 50:
            status = "ATENCAO"
        elif score >= 25:
            status = "DESVIO_RELEVANTE"
        else:
            status = "DESVIO_FORTE"

        if relevantes:
            explicacao = (
                "Foram encontrados sinais mais distantes do padrão "
                "operacional aprendido."
            )
        elif score < 75:
            explicacao = (
                "O conjunto das variáveis apresentou comportamento "
                "multivariado incomum, sem um único fator dominante."
            )
        else:
            explicacao = (
                "Os sinais avaliados estão aderentes ao padrão "
                "operacional aprendido."
            )

        return {
            "score": round(score, 2),
            "status": status,
            "anomaly_score": round(anomaly, 6),
            "perfil_id": self.perfil_id,
            "modelo_versao": self.versao,
            "top_factors": relevantes,
            "explanation": explicacao,
            "interpretation": self.interpretacao,
        }

    def save(self, path):
        path = Path(path)
        path.parent.mkdir(parents=True, exist_ok=True)

        with path.open("wb") as arquivo:
            pickle.dump(self.artefato, arquivo)

    @classmethod
    def load(cls, path):
        path = Path(path)

        if not path.exists():
            raise FileNotFoundError(
                f"Modelo operacional não encontrado: {path}"
            )

        with path.open("rb") as arquivo:
            artefato = pickle.load(arquivo)

        if not isinstance(artefato, dict):
            raise TypeError(
                "O arquivo .pkl não contém o dicionário de artefato esperado."
            )

        return cls(artefato)
