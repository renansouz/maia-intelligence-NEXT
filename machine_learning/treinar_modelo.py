import pandas as pd
import joblib
import os
import numpy as np
from sklearn.model_selection import train_test_split
from sklearn.ensemble import RandomForestClassifier
from sklearn.metrics import classification_report
from app.core.database import db

def carregar_dados():
    conn = db.get_connection()
    try:
        return pd.read_sql("SELECT * FROM TB_RISCO_AGRICOLA_TRATADO", conn)
    finally:
        db.release_connection(conn)

def treinar():
    df = carregar_dados()
    df.columns = [col.lower() for col in df.columns]

    features = [
        'temperatura', 'chuva_mm', 'umidade_solo', 'velocidade_kmh', 
        'proximidade_agua_m', 'inclinacao_graus', 'tempo_uso_horas', 'manutencao_dias',
        'indicador_chuva_alta', 'indicador_solo_umido', 'indicador_velocidade_alta',
        'indicador_perto_agua', 'indicador_inclinacao_alta', 'indicador_manutencao_atrasada'
    ]
    
    X = df[features]
    y = df['risco_operacional']

    X_train, X_test, y_train, y_test = train_test_split(X, y, test_size=0.2, random_state=42)

    modelo = RandomForestClassifier(n_estimators=80, class_weight='balanced', random_state=42)
    modelo.fit(X_train, y_train)

    # calculo das probabilidades para a classe 1 (risco alto)
    probas = modelo.predict_proba(X_test)[:, 1]

    # definicao das faixas conforme regras de negocio
    baixo = probas[probas < 0.30]
    medio = probas[(probas >= 0.30) & (probas <= 0.70)]
    alto = probas[probas > 0.70]

    total = len(probas)

    print("\n--- Analise de Faixas de Risco (predict_proba) ---")
    print(f"Risco Baixo  (< 30%): {len(baixo)} ({len(baixo)/total:.1%})")
    print(f"Risco Medio (30-70%): {len(medio)} ({len(medio)/total:.1%})")
    print(f"Risco Alto   (> 70%): {len(alto)} ({len(alto)/total:.1%})")

    print("\n--- Relatorio Binario (Threshold 0.5) ---")
    print(classification_report(y_test, modelo.predict(X_test)))

    os.makedirs('ml_assets', exist_ok=True)
    joblib.dump(modelo, 'ml_assets/modelo_risco.pkl', compress=3)
    joblib.dump(features, 'ml_assets/features.pkl')
    print("\nModelo e features salvos em ml_assets/")

if __name__ == "__main__":
    treinar()