from pydantic import BaseModel, Field
from typing import Optional
from datetime import date

class TelemetriaInput(BaseModel):
    equipamento_id: str = Field(..., example="EQP-SAO-01")
    cidade: str = Field(..., example="Sao Paulo")
    data_medicao: date = Field(..., example="2024-05-20")
    temperatura: float = Field(..., ge=-10, le=55)
    chuva_mm: float = Field(..., ge=0, le=500)
    umidade_solo: float = Field(..., ge=0, le=100)
    velocidade_kmh: float = Field(..., ge=0, le=120)
    proximidade_agua_m: float = Field(..., ge=0, le=5000)
    inclinacao_graus: float = Field(..., ge=0, le=90)
    tempo_uso_horas: float = Field(..., ge=0, le=24)
    manutencao_dias: int = Field(..., ge=0, le=365)

class PrevisaoResponse(BaseModel):
    score: float
    classificacao: str
    explicacao_completa: str
    hash_auditoria: str
    status: str

class StandardResponse(BaseModel):
    status: str
    mensagem: str

class LoginInput(BaseModel):
    email: str = Field(..., example="sompo@maia.com")
    senha: str = Field(..., example="senha-super-secreta")

class TokenResponse(BaseModel):
    token: str
    papel: str
    nome: str

class CriarUsuarioInput(BaseModel):
    nome: str = Field(..., example="Kevin Gestor")
    email: str = Field(..., example="kevin@fazendeiro.com")
    senha: str = Field(..., min_length=6, example="senhaboa123")
    papel: str = Field(..., example="OPERADOR")  # "GESTOR" ou "OPERADOR"
    tipo_cobertura: str | None = Field(None, example="BASICA")

class CriarFazendaInput(BaseModel):
    nome: str = Field(..., example="Fazenda Boa Vista")
    latitude: float
    longitude: float
    endereco: str | None = None

class CriarMaquinaInput(BaseModel):
    equipamento_id: str = Field(..., example="EQP-SAO-99")
    tipo: str | None = Field(None, example="Trator")
    modelo: str | None = None
    ano: int | None = None

class VincularFazendaInput(BaseModel):
    fazenda_id: int

class VincularOperadorInput(BaseModel):
    operador_id: int