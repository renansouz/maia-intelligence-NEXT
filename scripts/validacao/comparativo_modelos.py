import pandas as pd
import joblib
from sklearn.model_selection import train_test_split
from sklearn.tree import DecisionTreeClassifier
from sklearn.ensemble import RandomForestClassifier
from sklearn.metrics import roc_auc_score
from app.core.database import db

def run_benchmark():
    conn = db.get_connection()
    try:
        df = pd.read_sql("SELECT * FROM TB_RISCO_AGRICOLA_TRATADO", conn)
    finally:
        db.release_connection(conn)

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

    models = {
        "Decision Tree": DecisionTreeClassifier(random_state=42),
        "Random Forest": RandomForestClassifier(n_estimators=100, class_weight='balanced', random_state=42)
    }

    report = []

    for name, model in models.items():
        model.fit(X_train, y_train)
        probas = model.predict_proba(X_test)[:, 1]
        
        # Cálculo de AUC e Cobertura
        auc = roc_auc_score(y_test, probas)
        actual_positives = X_test[y_test == 1]
        coverage = (sum(model.predict_proba(actual_positives)[:, 1] >= 0.30) / len(actual_positives)) * 100

        report.append({
            "Algorithm": name,
            "ROC-AUC": round(auc, 4),
            "Risk Coverage (>= 30%)": f"{coverage:.2f}%"
        })

    print("\n[TECHNICAL BENCHMARK - RISK ENGINE]")
    print(pd.DataFrame(report).to_string(index=False))

if __name__ == "__main__":
    run_benchmark()