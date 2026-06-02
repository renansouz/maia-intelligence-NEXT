from pathlib import Path

import joblib
from preparar_features import preparar_features
from sklearn.metrics import (accuracy_score, classification_report,
                             confusion_matrix)
from sklearn.model_selection import train_test_split
from sklearn.tree import DecisionTreeClassifier


def treinar_modelo():
    X, y, features, df = preparar_features()

    X_treino, X_teste, y_treino, y_teste = train_test_split(
        X,
        y,
        test_size=0.25,
        random_state=42,
        stratify=y
    )

    modelo = DecisionTreeClassifier(
        criterion="gini",
        max_depth=5,
        random_state=42
    )

    modelo.fit(X_treino, y_treino)

    previsoes = modelo.predict(X_teste)

    acuracia = accuracy_score(y_teste, previsoes)

    print("\nModelo treinado com sucesso!")
    print(f"Acurácia: {acuracia:.4f}")

    print("\nRelatório de classificação:")
    print(classification_report(y_teste, previsoes))

    print("\nMatriz de confusão:")
    print(confusion_matrix(y_teste, previsoes))

    pasta_modelos = Path("./models")
    pasta_modelos.mkdir(exist_ok=True)

    caminho_modelo = pasta_modelos / "arvore_decisao.pkl"
    caminho_features = pasta_modelos / "features.pkl"

    joblib.dump(modelo, caminho_modelo)
    joblib.dump(features, caminho_features)

    print(f"\nModelo salvo em: {caminho_modelo}")
    print(f"Features salvas em: {caminho_features}")

    return modelo


if __name__ == "__main__":
    treinar_modelo()
