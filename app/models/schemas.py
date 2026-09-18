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
    cidade: str = Field(..., example="Campinas")
    latitude: float | None = None
    longitude: float | None = None
    endereco: str | None = None

class CriarMaquinaInput(BaseModel):
    equipamento_id: str = Field(..., example="EQP-SAO-99")
    gestor_id: int = Field(..., example=2)
    tipo: str | None = Field(None, example="Trator")
    modelo: str | None = None
    ano: int | None = None
    valor_segurado: float | None = Field(None, example=350000.00)

class VincularFazendaInput(BaseModel):
    fazenda_id: int

class VincularOperadorInput(BaseModel):
    operador_id: int

class AbrirTicketInput(BaseModel):
    equipamento_id: str = Field(..., example="DEMO-01")
    categoria: str = Field(..., example="Falha ou Ruído Mecânico")
    observacao: str | None = Field(None, example="Motor fazendo barulho estranho ao ligar.")

class SolicitarManutencaoInput(BaseModel):
    equipamento_id: str = Field(..., example="DEMO-01")
    descricao: str | None = Field(None, example="Verificar barulho reportado pelo operador.")
    tipo: str = Field("PREVENTIVA", example="PREVENTIVA")

class ConcluirManutencaoInput(BaseModel):
    data_realizada: str = Field(..., example="2026-09-17")
    hora_realizada: str = Field(..., example="14:30")
    descricao: str = Field(..., example="Troca de correia e verificação geral.")