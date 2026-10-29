from pydantic import BaseModel, Field
from typing import Optional
from datetime import date

class TelemetriaInput(BaseModel):
    equipamento_id: str = Field(..., example="EQP-SP-04")
    cidade: str | None = Field(None, example="Ribeirão Preto")
    data_medicao: date
    temp_coolant: float = Field(..., description="Temperatura do líquido de arrefecimento (°C)")
    temp_oleo: float = Field(..., description="Temperatura do óleo (°C)")
    pressao_oleo: float = Field(..., description="Pressão do óleo")
    torque_pct: float = Field(..., description="Percentual de torque do motor")
    rpm: float = Field(..., description="Rotação do motor")
    combustivel_l_h: float = Field(..., description="Taxa de consumo de combustível")
    velocidade_kmh: float = Field(..., description="Velocidade da máquina")
    manutencao_dias: int | None = Field(None, description="Dias desde a última manutenção")
    
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
    email: str = Field(..., example="seguradora@maia.com")
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