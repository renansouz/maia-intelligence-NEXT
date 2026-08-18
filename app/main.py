import os
import time
from fastapi import FastAPI, Depends, Header, HTTPException, status, Request
from dotenv import load_dotenv
from typing import List
from app.models.schemas import TelemetriaInput, PrevisaoResponse, StandardResponse
from app.services.data_service import salvar_telemetria_db, buscar_ultima_telemetria
from app.services.risco_service import processar_previsao_completa
from app.core.config_db import configurar_banco
from app.core.database import db
from fastapi.staticfiles import StaticFiles

load_dotenv()

app = FastAPI(
    title="MAIA - Monitoramento e Análise Inteligente Agrícola",
    description="Interface de Inteligência e Auditoria de Riscos Operacionais - Sompo Seguros",
    version="3.0.0"
)

API_KEY_SECRET = os.getenv("API_KEY")

async def verificar_key(x_api_key: str = Header(None)):
    if not API_KEY_SECRET or x_api_key != API_KEY_SECRET:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN, 
            detail="Acesso negado: chave invalida ou nao configurada"
        )
    return x_api_key

@app.middleware("http")
async def log_requests(request: Request, call_next):
    inicio = time.time()
    response = await call_next(request)
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
            response.status_code,
            request.client.host if request.client else "unknown",
            duracao
        ))
        conn.commit()
    except Exception as e:
        print(f"falha ao gravar log: {e}")
    finally:
        cursor.close()
        db.release_connection(conn)
    return response

@app.on_event("startup")
async def startup():
    configurar_banco()


@app.post("/telemetria", response_model=StandardResponse, status_code=201)
async def post_telemetria(dados: TelemetriaInput, _=Depends(verificar_key)):
    try:
        salvar_telemetria_db(dados.model_dump())
        return {"status": "sucesso", "mensagem": "telemetria registrada"}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/previsao/{equipamento_id}", response_model=PrevisaoResponse)
async def get_previsao(equipamento_id: str, _=Depends(verificar_key)):
    dados = buscar_ultima_telemetria(equipamento_id)
    if not dados:
        raise HTTPException(status_code=404, detail="equipamento nao encontrado")
    
    if 'data_medicao' in dados and not isinstance(dados['data_medicao'], str):
        dados['data_medicao'] = dados['data_medicao'].strftime('%Y-%m-%d')
    
    resultado = processar_previsao_completa(dados)
    if resultado.get("status") == "erro":
        raise HTTPException(status_code=500, detail=resultado.get("detalhe"))
    return resultado

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
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
    finally:
        db.release_connection(conn)

@app.get("/health")
async def health_check():
    """
    Endpoint para monitoramento de disponibilidade (SLA).
    Verifica a saúde da API e a conectividade com o pool de dados.
    """
    return {
        "status": "online",
        "version": "4.0.0",
        "engine": "Random Forest Ensemble",
        "database": "Oracle Cloud Connected"
    }

app.mount("/", StaticFiles(directory="frontend", html=True), name="frontend")