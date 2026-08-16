import pandas as pd
from app.core.database import db
from app.services.risco_service import processar_previsao_completa

def processar_massa_dados(limite_amostra=2500):
    conn = db.get_connection()
    cursor = conn.cursor()
    
    sucessos = 0
    erros = 0
    
    try:
        print("limpando tabela de previsoes para a demo...")
        cursor.execute("TRUNCATE TABLE TB_PREVISAO_RISCO")
        conn.commit()

        print("lendo dados da frota tratada...")
        query = "SELECT * FROM TB_RISCO_AGRICOLA_TRATADO ORDER BY DATA_MEDICAO DESC"
        df = pd.read_sql(query, conn)
    finally:
        cursor.close()
        db.release_connection(conn)

    df.columns = [col.lower() for col in df.columns]

    if len(df) > limite_amostra:
        df = df.head(limite_amostra)

    total = len(df)
    print(f"processando {total} registros. aguarde...")

    for i, row in df.iterrows():
        try:
            dados = row.to_dict()
            if isinstance(dados['data_medicao'], pd.Timestamp):
                dados['data_medicao'] = dados['data_medicao'].strftime('%Y-%m-%d')
            
            processar_previsao_completa(dados)
            sucessos += 1
        except Exception as e:
            erros += 1
            print(f"erro no registro {i}: {e}")
        
        if (i + 1) % 100 == 0:
            print(f"progresso: {i+1}/{total} (sucessos: {sucessos} | erros: {erros})")

    print(f"\nprocessamento finalizado.")
    print(f"total: {total} | sucessos: {sucessos} | falhas: {erros}")

if __name__ == "__main__":
    processar_massa_dados(2500)