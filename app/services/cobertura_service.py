"""noted by renansouz
Contém o catálogo de cobertura real do produto Sompo Equipamentos
Agrícolas Benfeitorias (Básica, Adicionais, Condições Particulares),
usado para exibir ao gestor o que está incluso no plano contratado por ele.

O campo TIPO_COBERTURA em TB_USUARIO guarda os códigos separados por
vírgula (ex: "BASICA,ADICIONAL"), permitindo planos combinados.
"""
from app.core.database import db

CATALOGO_COBERTURA = {
    "BASICA": {
        "nome": "Cobertura Básica",
        "itens": [
            "Incêndio", "Queda de raio", "Explosão de qualquer natureza",
            "Vendaval", "Tombamento", "Colisão", "Roubo",
            "Furto Qualificado", "Furto Simples", "Quebra de Vidros",
            "Danos durante o transporte (equipamentos móveis)"
        ]
    },
    "ADICIONAL": {
        "nome": "Coberturas Adicionais",
        "itens": [
            "Danos elétricos", "Pagamento de aluguel a terceiros",
            "Responsabilidade Civil (danos materiais e corporais)",
            "Despesas de salvamento"
        ]
    },
    "PARTICULAR": {
        "nome": "Condições Particulares",
        "itens": [
            "Equipamentos em operação próxima de água",
            "Equipamentos alugados e/ou operados por terceiros"
        ]
    }
}


def obter_catalogo_completo():
    return CATALOGO_COBERTURA


def obter_cobertura_do_usuario(tipo_cobertura_raw: str):
    """
    Recebe o valor cru de TIPO_COBERTURA (ex: "BASICA,ADICIONAL") e
    devolve a lista expandida com nome e itens de cada plano contratado.
    Códigos desconhecidos ou campo vazio/nulo são ignorados.
    """
    if not tipo_cobertura_raw:
        return []

    codigos = [c.strip().upper() for c in tipo_cobertura_raw.split(",")]
    return [CATALOGO_COBERTURA[c] for c in codigos if c in CATALOGO_COBERTURA]


def buscar_tipo_cobertura_usuario(id_usuario: int):
    conn = db.get_connection()
    cursor = conn.cursor()
    try:
        cursor.execute("SELECT TIPO_COBERTURA FROM TB_USUARIO WHERE ID_USUARIO = :id", id=id_usuario)
        row = cursor.fetchone()
        return row[0] if row else None
    finally:
        cursor.close()
        db.release_connection(conn)