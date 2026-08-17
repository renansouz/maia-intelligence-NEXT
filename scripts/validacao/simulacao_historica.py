import pandas as pd
from app.core.database import db
from app.services.ml_service import ml_service

def run_historical_simulation():
    conn = db.get_connection()
    try:
        # Extração de massa bruta para o período crítico
        query = """
            SELECT * FROM TB_RISCO_AGRICOLA_TRATADO 
            WHERE CIDADE = 'São Paulo' 
            AND DATA_MEDICAO BETWEEN TO_DATE('2024-02-01', 'YYYY-MM-DD') 
                             AND TO_DATE('2024-02-29', 'YYYY-MM-DD')
            ORDER BY DATA_MEDICAO
        """
        df = pd.read_sql(query, conn)
    finally:
        db.release_connection(conn)

    if df.empty:
        return

    df.columns = [col.lower() for col in df.columns]
    
    print("\n[HISTORICAL VALIDATION: SAO PAULO - FEB/2024]")
    
    unique_dates = sorted(df['data_medicao'].unique())

    for date_val in unique_dates:
        daily_batch = df[df['data_medicao'] == date_val]
        scores = []
        
        for _, row in daily_batch.iterrows():
            payload = row.to_dict()
            if not isinstance(payload['data_medicao'], str):
                payload['data_medicao'] = payload['data_medicao'].strftime('%Y-%m-%d')
            
            res = ml_service.prever_score(payload)
            scores.append(res['score'])
        
        avg_score = sum(scores) / len(scores)
        tag = "CRITICAL" if avg_score > 0.7 else "WARNING" if avg_score >= 0.3 else "STABLE"
        
        print(f"Date: {pd.to_datetime(date_val).strftime('%Y-%m-%d')} | Avg Score: {avg_score:.4f} | Status: {tag}")

if __name__ == "__main__":
    run_historical_simulation()