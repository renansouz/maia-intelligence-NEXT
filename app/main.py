import os
import time
import logging
from fastapi import FastAPI, Depends, Header, HTTPException, status, Request
from fastapi.responses import JSONResponse
from dotenv import load_dotenv
from typing import List
from app.models.schemas import TelemetriaInput, PrevisaoResponse, StandardResponse, LoginInput, TokenResponse
from app.services.data_service import salvar_telemetria_db, buscar_ultima_telemetria, buscar_ultima_previsao
from app.services.risco_service import processar_previsao_completa
from app.core.config_db import configurar_banco
from app.core.database import db
from fastapi.staticfiles import StaticFiles
from app.services.user_service import (
    buscar_usuario_por_email, garantir_usuario_sompo_inicial,
    criar_usuario, listar_operadores_do_gestor
)
from app.services.auth_service import verificar_senha, criar_token, requer_papel, obter_usuario_atual
from app.models.schemas import (
    TelemetriaInput, PrevisaoResponse, StandardResponse, LoginInput, TokenResponse,
    CriarUsuarioInput, CriarFazendaInput, CriarMaquinaInput,
    VincularFazendaInput, VincularOperadorInput
)
from app.services.maquina_service import (
    usuario_tem_acesso_equipamento, listar_equipamentos_permitidos,
    criar_maquina, buscar_maquina_por_equipamento_id,
    vincular_maquina_fazenda, vincular_operador_maquina
)
from app.services.fazenda_service import criar_fazenda, listar_fazendas_do_gestor, buscar_fazenda_por_id

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
    garantir_usuario_sompo_inicial()


@app.post("/auth/login", response_model=TokenResponse)
async def login(dados: LoginInput):
    usuario = buscar_usuario_por_email(dados.email)

    if not usuario or not usuario["ativo"]:
        raise HTTPException(status_code=401, detail="Credenciais invalidas.")

    if not verificar_senha(dados.senha, usuario["senha_hash"]):
        raise HTTPException(status_code=401, detail="Credenciais invalidas.")

    token = criar_token(usuario["id_usuario"], usuario["papel"], usuario["gestor_id"])

    return {
        "token": token,
        "papel": usuario["papel"],
        "nome": usuario["nome"]
    }


@app.post("/telemetria", response_model=StandardResponse, status_code=201)
async def post_telemetria(dados: TelemetriaInput, _=Depends(verificar_key)):
    salvar_telemetria_db(dados.model_dump())
    return {"status": "sucesso", "mensagem": "telemetria registrada"}

@app.post("/previsao/{equipamento_id}", response_model=PrevisaoResponse)
async def post_previsao(equipamento_id: str, usuario_logado: dict = Depends(obter_usuario_atual)):
    if not usuario_tem_acesso_equipamento(usuario_logado, equipamento_id):
        raise HTTPException(status_code=403, detail="Sem permissao para acessar este equipamento.")

    dados = buscar_ultima_telemetria(equipamento_id)
    if not dados:
        raise HTTPException(status_code=404, detail="equipamento nao encontrado")

    if 'data_medicao' in dados and not isinstance(dados['data_medicao'], str):
        dados['data_medicao'] = dados['data_medicao'].strftime('%Y-%m-%d')

    resultado = processar_previsao_completa(dados)
    return resultado


@app.get("/previsao/{equipamento_id}/ultima", response_model=PrevisaoResponse)
async def get_ultima_previsao(equipamento_id: str, usuario_logado: dict = Depends(obter_usuario_atual)):
    if not usuario_tem_acesso_equipamento(usuario_logado, equipamento_id):
        raise HTTPException(status_code=403, detail="Sem permissao para acessar este equipamento.")

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
async def get_historico(usuario_logado: dict = Depends(obter_usuario_atual)):
    import pandas as pd
    conn = db.get_connection()
    try:
        query = "SELECT * FROM TB_PREVISAO_RISCO ORDER BY DATA_PREVISAO DESC"
        df = pd.read_sql(query, conn)

        equipamentos_permitidos = listar_equipamentos_permitidos(usuario_logado)
        if equipamentos_permitidos is not None:  # None = SOMPO, ve tudo
            df = df[df['EQUIPAMENTO_ID'].isin(equipamentos_permitidos)]

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

@app.post("/usuarios", response_model=StandardResponse, status_code=201)
async def criar_novo_usuario(dados: CriarUsuarioInput, usuario_logado: dict = Depends(requer_papel("SOMPO", "GESTOR"))):
    if usuario_logado["papel"] == "SOMPO" and dados.papel != "GESTOR":
        raise HTTPException(status_code=403, detail="Sompo so pode criar usuarios com papel GESTOR.")

    if usuario_logado["papel"] == "GESTOR" and dados.papel != "OPERADOR":
        raise HTTPException(status_code=403, detail="Gestor so pode criar usuarios com papel OPERADOR.")

    if buscar_usuario_por_email(dados.email):
        raise HTTPException(status_code=409, detail="Ja existe um usuario com este email.")

    gestor_id = usuario_logado["id_usuario"] if dados.papel == "OPERADOR" else None

    criar_usuario(
        nome=dados.nome, email=dados.email, senha_plana=dados.senha,
        papel=dados.papel, gestor_id=gestor_id, tipo_cobertura=dados.tipo_cobertura
    )
    return {"status": "sucesso", "mensagem": f"Usuario {dados.papel} criado com sucesso."}

@app.get("/usuarios/meus-operadores", response_model=List[dict])
async def get_meus_operadores(usuario_logado: dict = Depends(requer_papel("GESTOR"))):
    return listar_operadores_do_gestor(usuario_logado["id_usuario"])

@app.post("/fazendas", response_model=StandardResponse, status_code=201)
async def post_fazenda(dados: CriarFazendaInput, usuario_logado: dict = Depends(requer_papel("GESTOR"))):
    criar_fazenda(usuario_logado["id_usuario"], dados.nome, dados.latitude, dados.longitude, dados.endereco)
    return {"status": "sucesso", "mensagem": "Fazenda cadastrada com sucesso."}


@app.get("/fazendas", response_model=List[dict])
async def get_fazendas(usuario_logado: dict = Depends(requer_papel("GESTOR"))):
    return listar_fazendas_do_gestor(usuario_logado["id_usuario"])


@app.post("/maquinas", response_model=StandardResponse, status_code=201)
async def post_maquina(dados: CriarMaquinaInput, usuario_logado: dict = Depends(requer_papel("SOMPO"))):
    if buscar_maquina_por_equipamento_id(dados.equipamento_id):
        raise HTTPException(status_code=409, detail="Ja existe uma maquina com este equipamento_id.")
    criar_maquina(dados.equipamento_id, dados.tipo, dados.modelo, dados.ano, criado_por=usuario_logado["id_usuario"])
    return {"status": "sucesso", "mensagem": "Maquina cadastrada com sucesso."}


@app.post("/maquinas/{equipamento_id}/vincular-fazenda", response_model=StandardResponse)
async def post_vincular_fazenda(
    equipamento_id: str, dados: VincularFazendaInput,
    usuario_logado: dict = Depends(requer_papel("GESTOR"))
):
    maquina = buscar_maquina_por_equipamento_id(equipamento_id)
    if not maquina:
        raise HTTPException(status_code=404, detail="Maquina nao encontrada.")

    fazenda = buscar_fazenda_por_id(dados.fazenda_id)
    if not fazenda or fazenda["gestor_id"] != usuario_logado["id_usuario"]:
        raise HTTPException(status_code=403, detail="Fazenda nao encontrada ou nao pertence a voce.")

    vincular_maquina_fazenda(equipamento_id, dados.fazenda_id)
    return {"status": "sucesso", "mensagem": "Maquina vinculada a fazenda com sucesso."}


@app.post("/maquinas/{equipamento_id}/vincular-operador", response_model=StandardResponse)
async def post_vincular_operador(
    equipamento_id: str, dados: VincularOperadorInput,
    usuario_logado: dict = Depends(requer_papel("GESTOR"))
):
    maquina = buscar_maquina_por_equipamento_id(equipamento_id)
    if not maquina:
        raise HTTPException(status_code=404, detail="Maquina nao encontrada.")

    fazendas_do_gestor = [f["id_fazenda"] for f in listar_fazendas_do_gestor(usuario_logado["id_usuario"])]
    if not maquina["fazenda_id"] or maquina["fazenda_id"] not in fazendas_do_gestor:
        raise HTTPException(status_code=403, detail="Maquina nao pertence a uma fazenda sua.")

    operadores_do_gestor = [op["id_usuario"] for op in listar_operadores_do_gestor(usuario_logado["id_usuario"])]
    if dados.operador_id not in operadores_do_gestor:
        raise HTTPException(status_code=403, detail="Operador nao pertence a voce.")

    vincular_operador_maquina(equipamento_id, dados.operador_id)
    return {"status": "sucesso", "mensagem": "Operador vinculado a maquina com sucesso."}

app.mount("/", StaticFiles(directory="frontend", html=True), name="frontend")
