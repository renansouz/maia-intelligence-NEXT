from app.core.database import db

def check():
    conn = db.get_connection()
    cursor = conn.cursor()
    tabelas = ["TB_RISCO_AGRICOLA", "TB_RISCO_AGRICOLA_TRATADO", "TB_PREVISAO_RISCO"]
    
    print("--- Contagem Real de Registros ---")
    for t in tabelas:
        cursor.execute(f"SELECT COUNT(*) FROM {t}")
        count = cursor.fetchone()[0]
        print(f"{t}: {count} registros")
    
    cursor.close()
    db.release_connection(conn)

if __name__ == "__main__":
    check()