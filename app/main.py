import os
import time
import logging
from fastapi import FastAPI, Depends, Header, HTTPException, status, Request
from fastapi.responses import JSONResponse
from dotenv import load_dotenv
from typing import List
from app.models.schemas import TelemetriaInput, PrevisaoResponse, StandardResponse
from app.services.data_service import salvar_telemetria_db, buscar_ultima_telemetria, buscar_ultima_previsao
from app.services.risco_service import processar_previsao_completa
from app.core.config_db import configurar_banco
from app.core.database import db
from fastapi.staticfiles import StaticFiles

load_dotenv()

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger("maia")

app = FastAPI(
    title="MAIA - Monitoramento e Análise Inteligente Agrícola",
    description="Interface de Inteligência e Auditoria de Riscos Operacionais - Sompo Seguros",
    version="4.0.0"
)

API_KEY_SECRET = os.getenv("API_KEY")

async def verificar_key(x_api_key: str = Header(None)):
    if not API_KEY_SECRET or x_api_key != API_KEY_SECRET:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN, 
            detail="Acesso negado: chave invalida ou nao configurada"
        )
    return x_api_key

@app.exception_handler(Exception)
async def excecao_global_handler(request: Request, exc: Exception):
    codigo_rastreio = f"{int(time.time())}-{id(exc) % 100000}"
    logger.error(
        f"[{codigo_rastreio}] Erro nao tratado em {request.method} {request.url.path}: {exc}",
        exc_info=True
    )
    return JSONResponse(
        status_code=500,
        content={
            "status": "erro",
            "mensagem": "Ocorreu um erro interno ao processar a requisicao.",
            "codigo_rastreio": codigo_rastreio
        }
    )


@app.middleware("http")
async def log_requests(request: Request, call_next):
    inicio = time.time()
    status_code_resposta = 500

    try:
        response = await call_next(request)
        status_code_resposta = response.status_code
        return response
    finally:
        duracao = int((time.time() - inicio) * 1000)
        conn = db.get_connection()
        cursor = conn.cursor()
        try:
            sql = """
                INSERT INTO TB_LOG_ACESSO (METODO, ROTA, STATUS_CODE, IP_ORIGEM, TEMPO_MS)
                VALUES (:1, :2, :3, :4, :5)
            """
            cursor.execute(sql, (
                request.method,
                request.url.path,
                status_code_resposta,
                request.client.host if request.client else "unknown",
                duracao
            ))
            conn.commit()
        except Exception as e:
            logger.warning(f"Falha ao gravar log de acesso: {e}")
        finally:
            cursor.close()
            db.release_connection(conn)

@app.on_event("startup")
async def startup():
    configurar_banco()


@app.post("/telemetria", response_model=StandardResponse, status_code=201)
async def post_telemetria(dados: TelemetriaInput, _=Depends(verificar_key)):
    salvar_telemetria_db(dados.model_dump())
    return {"status": "sucesso", "mensagem": "telemetria registrada"}

@app.post("/previsao/{equipamento_id}", response_model=PrevisaoResponse)
async def post_previsao(equipamento_id: str, _=Depends(verificar_key)):
    dados = buscar_ultima_telemetria(equipamento_id)
    if not dados:
        raise HTTPException(status_code=404, detail="equipamento nao encontrado")

    if 'data_medicao' in dados and not isinstance(dados['data_medicao'], str):
        dados['data_medicao'] = dados['data_medicao'].strftime('%Y-%m-%d')

    resultado = processar_previsao_completa(dados)
    return resultado

@app.get("/previsao/{equipamento_id}/ultima", response_model=PrevisaoResponse)
async def get_ultima_previsao(equipamento_id: str, _=Depends(verificar_key)):
    dados = buscar_ultima_previsao(equipamento_id)
    if not dados:
        raise HTTPException(status_code=404, detail="nenhuma previsao encontrada para este equipamento")

    return {
        "score": dados['probabilidade_alto'],
        "classificacao": dados['classificacao'],
        "explicacao_completa": dados['explicacao'],
        "hash_auditoria": dados['hash_integridade'],
        "status": "sucesso"
    }

@app.get("/historico", response_model=List[dict])
async def get_historico(_=Depends(verificar_key)):
    import pandas as pd
    conn = db.get_connection()
    try:
        query = "SELECT * FROM TB_PREVISAO_RISCO ORDER BY DATA_PREVISAO DESC"
        df = pd.read_sql(query, conn)
        for col in df.select_dtypes(include=['datetime64', 'datetime']).columns:
            df[col] = df[col].dt.strftime('%Y-%m-%d %H:%M:%S')
        return df.to_dict(orient="records")
    finally:
        db.release_connection(conn)

@app.get("/health")
async def health_check():
    return {
        "status": "online",
        "version": "4.0.0",
        "engine": "Random Forest Ensemble",
        "database": "Oracle Cloud Connected"
    }

app.mount("/", StaticFiles(directory="frontend", html=True), name="frontend")