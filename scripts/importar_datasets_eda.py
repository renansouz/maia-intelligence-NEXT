"""Importa os datasets do EDA para o Oracle em formato canônico.

Uso:
    python -m scripts.importar_datasets_eda
    python -m scripts.importar_datasets_eda --dataset tumosan
    python -m scripts.importar_datasets_eda --replace

O script não altera os arquivos brutos e não apaga tabelas da aplicação.
"""

from __future__ import annotations

import argparse
import hashlib
import re
from datetime import datetime, timedelta
from pathlib import Path

import numpy as np
import pandas as pd

from app.core.config_db import configurar_banco
from app.core.database import db

PROJECT_ROOT = Path(__file__).resolve().parents[1]
DATA_ROOT = PROJECT_ROOT / "machine_learning" / "data" / "raw"
CHUNK_SIZE = 10_000

DATASETS = {
    "tumosan": {
        "codigo": "TUMOSAN",
        "nome": "Tümosan 81.110 Powershuttle",
        "fonte": "Mendeley Data 10.17632/bbjtjrsxvx.2",
        "frequencia_hz": 10,
        "tipo_dado": "REAL",
    },
    "fendt": {
        "codigo": "FENDT",
        "nome": "Agricultural Load Cycles",
        "fonte": "Zenodo 10.5281/zenodo.14619787",
        "frequencia_hz": 10,
        "tipo_dado": "REAL",
    },
    "new_holland": {
        "codigo": "NEW_HOLLAND",
        "nome": "GNSS-CAN Farm Tractor Operations Dataset",
        "fonte": "GitHub lindiap/tractor-field-operations-dataset",
        "frequencia_hz": 1,
        "tipo_dado": "REAL_E_SINTETICO",
    },
}

ALIASES = {
    "timestamp": ["timestamps", "timestamp", "time"],
    "tempo_ms": ["time_ms"],
    "temp_coolant": [
        "EngCoolantTemp", "EngineCoolantTemperature", "coolant_temp"
    ],
    "temp_oleo": [
        "EngOilTemp1", "EngineOilTemperature1", "oil_temp"
    ],
    "temp_ambiente": [
        "AmbientAirTemperature", "Ambient Air Temperature", "ambient_temp"
    ],
    "temp_admissao": [
        "EngnIntkMnfld1Tmprtr", "EngineIntakeManifold1Temperature", "intake_temp"
    ],
    "pressao_oleo": [
        "EngOilPress", "EngineOilPressure1", "oil_pressure"
    ],
    "torque_pct": [
        "ActualEngine_PercTorque", "ActualEnginePercentTorque", "torque_pct"
    ],
    "carga_motor_pct": [
        "EnginePercentLoadAtCurrentSpeed", "engine_load_pct"
    ],
    "rpm": ["EngineSpeed", "engine_speed"],
    "combustivel_l_h": ["EngFuelRate", "EngineFuelRate", "fuel_rate"],
    "velocidade_kmh": [
        "WheelBasedVehicleSpeed", "GroundBasedMachineSpeed", "vehicle_speed"
    ],
    "ventoinha_pct": [
        "FanSpeed", "EngineFan1EstimatedPercentSpeed", "fan_speed"
    ],
    "posicao_engate_pct": ["HtcPositionSensPerc", "hitch_position_pct"],
    "draft1_pct": ["HtcDraftSens1Perc", "draft1_pct"],
    "draft2_pct": ["HtcDraftSens2Perc", "draft2_pct"],
    "tracao_4x4": ["TransferCaseStatus", "four_wheel_drive"],
    "pto_status": ["PTO_Status", "pto_status"],
    "implemento_codigo": ["KeypadButon", "implement_code"],
    "estado_operacional": ["STATE", "operational_state", "state"],
    "anomalia_sintetica": ["anomaly_label", "class_label"],
}

INSERT_SQL = """
    INSERT INTO TB_ML_TELEMETRIA (
        SESSAO_ID, LINHA_ORIGEM, TIMESTAMP_ORIGEM, TEMPO_MS,
        TEMP_COOLANT_C, TEMP_OLEO_C, TEMP_AMBIENTE_C, TEMP_ADMISSAO_C,
        PRESSAO_OLEO_KPA, TORQUE_PCT, CARGA_MOTOR_PCT, RPM,
        COMBUSTIVEL_L_H, VELOCIDADE_KMH, VENTOINHA_PCT,
        POSICAO_ENGATE_PCT, DRAFT1_PCT, DRAFT2_PCT, TRACAO_4X4,
        PTO_STATUS, IMPLEMENTO_CODIGO, ESTADO_OPERACIONAL, ANOMALIA_SINTETICA
    ) VALUES (
        :1, :2, :3, :4, :5, :6, :7, :8, :9, :10, :11, :12,
        :13, :14, :15, :16, :17, :18, :19, :20, :21, :22, :23
    )
"""


def normalizar_nome(nome: str) -> str:
    return re.sub(r"[^a-z0-9]", "", str(nome).lower())


def localizar_coluna(colunas, aliases):
    mapa = {normalizar_nome(coluna): coluna for coluna in colunas}
    for alias in aliases:
        chave = normalizar_nome(alias)
        if chave in mapa:
            return mapa[chave]
    for alias in aliases:
        chave = normalizar_nome(alias)
        for normalizado, original in mapa.items():
            if chave and chave in normalizado:
                return original
    return None


def numero_field(path: Path) -> int | None:
    match = re.search(r"FIELD_(\d+)", path.name, flags=re.IGNORECASE)
    return int(match.group(1)) if match else None


def arquivos_dataset(nome: str) -> list[Path]:
    if nome == "tumosan":
        return sorted((DATA_ROOT / "tumosan").rglob("*.tab"))
    if nome == "fendt":
        arquivos = sorted((DATA_ROOT / "fendt").rglob("*.csv"))
        campos = [p for p in arquivos if p.stem.lower().startswith("field_")]
        return campos or arquivos
    if nome == "new_holland":
        return sorted((DATA_ROOT / "new_holland").rglob("*.csv"))
    raise ValueError(f"Dataset desconhecido: {nome}")


def hash_arquivo(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as arquivo:
        for bloco in iter(lambda: arquivo.read(1024 * 1024), b""):
            digest.update(bloco)
    return digest.hexdigest()


def valor_numerico(valor):
    if pd.isna(valor):
        return None
    convertido = pd.to_numeric(valor, errors="coerce")
    return None if pd.isna(convertido) else float(convertido)


def valor_texto(valor):
    if pd.isna(valor):
        return None
    return str(valor)


def timestamp_origem(valor):
    if pd.isna(valor):
        return None
    if isinstance(valor, (int, float, np.integer, np.floating)):
        return datetime(1970, 1, 1) + timedelta(seconds=float(valor))
    convertido = pd.to_datetime(valor, errors="coerce")
    if pd.isna(convertido):
        return None
    return convertido.to_pydatetime()


def metadados_sessao(dataset: str, path: Path):
    identificador = path.stem
    operacao = None
    implemento = None

    field_id = numero_field(path)
    if dataset == "tumosan" and field_id is not None:
        identificador = f"FIELD_{field_id}"
        operacao = "Rotary tilling" if field_id in (7, 10) else "Ploughing"
        implemento = (
            "Hisarlar Alabora 300"
            if field_id in (7, 10)
            else "Unallar plough"
        )
    elif dataset == "fendt":
        operacao = path.parent.name
    elif dataset == "new_holland":
        operacao = "anomalia_sintetica" if "anomalous_datasets" in path.parts else "sessao_real"

    return identificador, operacao, implemento


def linha_canonica(row, mapa, linha: int, sessao_id: int, dataset: str):
    timestamp_col = mapa.get("timestamp")
    tempo_ms_col = mapa.get("tempo_ms")
    timestamp_valor = row[timestamp_col] if timestamp_col else None
    tempo_ms = valor_numerico(row[tempo_ms_col]) if tempo_ms_col else None

    if tempo_ms is None and timestamp_col and dataset == "tumosan":
        tempo_ms = valor_numerico(timestamp_valor)

    anomalia = valor_texto(row[mapa["anomalia_sintetica"]]) if mapa.get("anomalia_sintetica") else None
    if dataset == "new_holland" and "anomalous_datasets" not in str(row.get("__arquivo__", "")):
        anomalia = None

    if tempo_ms is not None and timestamp_col == tempo_ms_col:
        timestamp = (
            datetime(1970, 1, 1)
            + timedelta(milliseconds=tempo_ms)
        )
    else:
        timestamp = timestamp_origem(timestamp_valor)

    valores = [
        sessao_id,
        linha,
        timestamp,
        tempo_ms,
    ]

    for campo in [
        "temp_coolant", "temp_oleo", "temp_ambiente", "temp_admissao",
        "pressao_oleo", "torque_pct", "carga_motor_pct", "rpm",
        "combustivel_l_h", "velocidade_kmh", "ventoinha_pct",
        "posicao_engate_pct", "draft1_pct", "draft2_pct", "tracao_4x4",
        "pto_status",
    ]:
        coluna = mapa.get(campo)
        valores.append(valor_numerico(row[coluna]) if coluna else None)

    valores.extend([
        valor_texto(row[mapa["implemento_codigo"]]) if mapa.get("implemento_codigo") else None,
        valor_texto(row[mapa["estado_operacional"]]) if mapa.get("estado_operacional") else None,
        anomalia,
    ])
    return tuple(valores)


def garantir_dataset(cursor, dados):
    id_dataset = cursor.var(int)
    cursor.execute(
        "SELECT ID_DATASET FROM TB_ML_DATASET WHERE CODIGO = :codigo",
        codigo=dados["codigo"],
    )
    row = cursor.fetchone()
    if row:
        return int(row[0])
    cursor.execute(
        """
        INSERT INTO TB_ML_DATASET (CODIGO, NOME, FONTE, FREQUENCIA_HZ, TIPO_DADO)
        VALUES (:codigo, :nome, :fonte, :frequencia, :tipo)
        RETURNING ID_DATASET INTO :id_dataset
        """,
        codigo=dados["codigo"], nome=dados["nome"], fonte=dados["fonte"],
        frequencia=dados["frequencia_hz"], tipo=dados["tipo_dado"],
        id_dataset=id_dataset,
    )
    return int(id_dataset.getvalue()[0])


def obter_ou_criar_sessao(cursor, dataset_id, path, dataset, replace):
    identificador, operacao, implemento = metadados_sessao(dataset, path)
    cursor.execute(
        "SELECT ID_SESSAO FROM TB_ML_SESSAO WHERE DATASET_ID = :dataset AND IDENTIFICADOR = :identificador",
        dataset=dataset_id, identificador=identificador,
    )
    row = cursor.fetchone()
    if row:
        if not replace:
            return None
        cursor.execute("DELETE FROM TB_ML_TELEMETRIA WHERE SESSAO_ID = :sessao", sessao=int(row[0]))
        cursor.execute(
            """
            UPDATE TB_ML_SESSAO
            SET ARQUIVO_ORIGEM = :arquivo, HASH_ARQUIVO = :hash, TOTAL_LINHAS = NULL
            WHERE ID_SESSAO = :sessao
            """,
            arquivo=str(path.relative_to(PROJECT_ROOT)), hash=hash_arquivo(path), sessao=int(row[0]),
        )
        return int(row[0])

    cursor.execute(
        """
        INSERT INTO TB_ML_SESSAO (
            DATASET_ID, IDENTIFICADOR, OPERACAO, IMPLEMENTO,
            ARQUIVO_ORIGEM, HASH_ARQUIVO
        ) VALUES (:dataset, :identificador, :operacao, :implemento, :arquivo, :hash)
        RETURNING ID_SESSAO INTO :id_sessao
        """,
        dataset=dataset_id, identificador=identificador, operacao=operacao,
        implemento=implemento, arquivo=str(path.relative_to(PROJECT_ROOT)),
        hash=hash_arquivo(path), id_sessao=cursor.var(int),
    )
    cursor.execute(
        "SELECT ID_SESSAO FROM TB_ML_SESSAO WHERE DATASET_ID = :dataset AND IDENTIFICADOR = :identificador",
        dataset=dataset_id, identificador=identificador,
    )
    return int(cursor.fetchone()[0])


def importar_arquivo(cursor, dataset_id, dataset, path, replace):
    sessao_id = obter_ou_criar_sessao(cursor, dataset_id, path, dataset, replace)
    if sessao_id is None:
        print(f"Ignorado (já carregado): {path.name}")
        return 0

    total = 0
    separador = "\t" if path.suffix.lower() == ".tab" else ","
    for chunk in pd.read_csv(path, sep=separador, chunksize=CHUNK_SIZE, low_memory=False):
        mapa = {campo: localizar_coluna(chunk.columns, aliases) for campo, aliases in ALIASES.items()}
        chunk["__arquivo__"] = str(path)
        registros = [
            linha_canonica(row, mapa, total + indice + 1, sessao_id, dataset)
            for indice, (_, row) in enumerate(chunk.iterrows())
        ]
        cursor.executemany(INSERT_SQL, registros)
        total += len(registros)

    cursor.execute(
        "UPDATE TB_ML_SESSAO SET TOTAL_LINHAS = :total WHERE ID_SESSAO = :sessao",
        total=total, sessao=sessao_id,
    )
    print(f"Carregado: {dataset}/{path.name} -> {total:,} amostras".replace(",", "."))
    return total


def main():
    parser = argparse.ArgumentParser(description="Importa datasets do EDA para o Oracle")
    parser.add_argument("--dataset", choices=["tumosan", "fendt", "new_holland", "todos"], default="todos")
    parser.add_argument("--replace", action="store_true", help="recarrega sessões já existentes")
    args = parser.parse_args()

    configurar_banco()
    conn = db.get_connection()
    cursor = conn.cursor()
    try:
        nomes = list(DATASETS) if args.dataset == "todos" else [args.dataset]
        total_geral = 0
        for nome in nomes:
            dataset_id = garantir_dataset(cursor, DATASETS[nome])
            for path in arquivos_dataset(nome):
                total_geral += importar_arquivo(cursor, dataset_id, nome, path, args.replace)
        conn.commit()
        print(f"Importação concluída: {total_geral:,} amostras".replace(",", "."))
    except Exception:
        conn.rollback()
        raise
    finally:
        cursor.close()
        db.release_connection(conn)


if __name__ == "__main__":
    main()
