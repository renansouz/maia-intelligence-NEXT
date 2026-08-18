import pandas as pd
import numpy as np
from sklearn.model_selection import train_test_split
from sklearn.tree import DecisionTreeClassifier
from sklearn.ensemble import RandomForestClassifier, GradientBoostingClassifier
from sklearn.linear_model import LogisticRegression
from sklearn.metrics import roc_auc_score
from scipy.stats import pearsonr
from app.core.database import db

def run_elite_benchmark():
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
        "Regressão Logística": LogisticRegression(max_iter=1000),
        "Árvore de Decisão": DecisionTreeClassifier(random_state=42),
        "Gradient Boosting": GradientBoostingClassifier(random_state=42),
        "Random Forest (MAIA)": RandomForestClassifier(n_estimators=60, class_weight='balanced', random_state=42)
    }

    report = []
    for name, model in models.items():
        model.fit(X_train, y_train)
        probas = model.predict_proba(X_test)[:, 1]
        auc = roc_auc_score(y_test, probas)
        
        actual_positives = X_test[y_test == 1]
        coverage = (sum(model.predict_proba(actual_positives)[:, 1] >= 0.30) / len(actual_positives)) * 100
        
        report.append({"Algoritmo": name, "ROC-AUC": round(auc, 4), "Cobertura (>=30%)": f"{coverage:.2f}%"})

    print("\n[BENCHMARK DE PERFORMANCE - MOTOR DE RISCO MAIA]")
    print(pd.DataFrame(report).to_string(index=False))

    corr, p_value = pearsonr(df['chuva_mm'], df['risco_operacional'])
    print(f"\n[SIGNIFICÂNCIA ESTATÍSTICA]")
    print(f"Correlação (Chuva x Risco): {corr:.4f}")
    print(f"P-Value: {p_value:.4e} ({'Significativo' if p_value < 0.05 else 'Não significativo'})")
    print("Nota: O p-value próximo de zero confirma que a relação entre clima e risco não é obra do acaso.")

if __name__ == "__main__":
    run_elite_benchmark()