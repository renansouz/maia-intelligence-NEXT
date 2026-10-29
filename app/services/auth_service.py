"""noted by renansouz
Responsável por:
1. Hash e verificação de senha (bcrypt via passlib).
2. Geração e validação de token JWT, contendo identidade (id_usuario) e
   papel (seguradora/GESTOR/OPERADOR) do usuário.
3. Dependências do FastAPI para proteger rotas por autenticação e por papel.
"""
import os
import jwt
from datetime import datetime, timedelta, timezone
from fastapi import Header, HTTPException, status, Depends
from passlib.context import CryptContext

pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")

JWT_SECRET_KEY = os.getenv("JWT_SECRET_KEY")
JWT_ALGORITHM = "HS256"
JWT_EXPIRACAO_HORAS = 24


def hash_senha(senha_plana: str) -> str:
    return pwd_context.hash(senha_plana)


def verificar_senha(senha_plana: str, senha_hash: str) -> bool:
    return pwd_context.verify(senha_plana, senha_hash)


def criar_token(id_usuario: int, papel: str, gestor_id: int = None) -> str:
    if not JWT_SECRET_KEY:
        raise RuntimeError("JWT_SECRET_KEY nao configurada no .env")

    agora = datetime.now(timezone.utc)
    payload = {
        "sub": str(id_usuario),
        "papel": papel,
        "gestor_id": gestor_id,
        "iat": agora,
        "exp": agora + timedelta(hours=JWT_EXPIRACAO_HORAS)
    }
    return jwt.encode(payload, JWT_SECRET_KEY, algorithm=JWT_ALGORITHM)


def decodificar_token(token: str) -> dict:
    try:
        return jwt.decode(token, JWT_SECRET_KEY, algorithms=[JWT_ALGORITHM])
    except jwt.ExpiredSignatureError:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Sessao expirada, faca login novamente."
        )
    except jwt.InvalidTokenError:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Token invalido.")


async def obter_usuario_atual(authorization: str = Header(None)) -> dict:
    if not authorization or not authorization.startswith("Bearer "):
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Token nao fornecido.")

    token = authorization.replace("Bearer ", "", 1)
    payload = decodificar_token(token)
    return {
        "id_usuario": int(payload["sub"]),
        "papel": payload["papel"],
        "gestor_id": payload.get("gestor_id")
    }


def requer_papel(*papeis_permitidos):
    async def verificador(usuario: dict = Depends(obter_usuario_atual)) -> dict:
        if usuario["papel"] not in papeis_permitidos:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail=f"Acesso restrito a: {', '.join(papeis_permitidos)}."
            )
        return usuario
    return verificador