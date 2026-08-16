import os
from fastapi import FastAPI, Depends, Header, HTTPException, status
from dotenv import load_dotenv

from app.models.schemas import TelemetriaInput, PrevisaoResponse, StandardResponse
from app.services.data_service import salvar_telemetria_db, buscar_ultima_telemetria
from app.services.risco_service import processar_previsao_completa
from app.core.config_db import configurar_banco

load_dotenv()

app = FastAPI(title="SompoRisk AI", version="3.0.0")

# --- seguranca ---
API_KEY_SECRET = os.getenv("API_KEY")

async def verificar_key(x_api_key: str = Header(None)):
    if x_api_key != API_KEY_SECRET:
        raise HTTPException(status_code=403, detail="chave invalida")
    return x_api_key

# --- startup ---
@app.on_event("startup")
async def startup():
    configurar_banco()

# --- rotas ---

@app.post("/telemetria", response_model=StandardResponse, status_code=201)
async def post_telemetria(dados: TelemetriaInput, _=Depends(verificar_key)):
    """
    recebe dados do sensor, valida e salva no oracle
    """
    try:
        salvar_telemetria_db(dados.model_dump())
        return {"status": "sucesso", "mensagem": "telemetria registrada"}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/previsao/{equipamento_id}", response_model=PrevisaoResponse)
async def get_previsao(equipamento_id: str, _=Depends(verificar_key)):
    """
    busca o dado mais novo, roda o ML e gera auditoria
    """
    dados = buscar_ultima_telemetria(equipamento_id)
    if not dados:
        raise HTTPException(status_code=404, detail="equipamento nao encontrado")
    
    if 'data_medicao' in dados and not isinstance(dados['data_medicao'], str):
        dados['data_medicao'] = dados['data_medicao'].strftime('%Y-%m-%d')
    
    resultado = processar_previsao_completa(dados)
    
    if resultado.get("status") == "erro":
        raise HTTPException(status_code=500, detail=resultado.get("detalhe"))
        
    return resultado

from typing import List

@app.get("/historico", response_model=List[dict])
async def get_historico(token: str = Depends(verificar_key)):
    """
    retorna todos os registros de previsao para popular o dashboard.
    dashboard para de acessar o oracle diretamente.
    """
    from app.core.database import db
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