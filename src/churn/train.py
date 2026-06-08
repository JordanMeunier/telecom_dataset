"""Entraînement et évaluation du modèle.

Choix de modèle : régression logistique
  - Modèle simple, rapide à entraîner et ressort bien des proba pour l'API (route /predict).

Anti-fuite de données : tout le preprocessing (scaling, one-hot) est encapsulé
dans un Pipeline scikit-learn, donc appris UNIQUEMENT sur le train via fit()
Le test n'est touché qu'au moment de l'évaluation
"""
from __future__ import annotations

from pathlib import Path

import joblib
from sklearn.compose import ColumnTransformer
from sklearn.linear_model import LogisticRegression
from sklearn.metrics import (
    classification_report,
    confusion_matrix,
    roc_auc_score,
)
from sklearn.model_selection import train_test_split
from sklearn.pipeline import Pipeline
from sklearn.preprocessing import OneHotEncoder, StandardScaler

from churn.data import load_raw, clean, split_features_target

ARTIFACT_PATH = Path(__file__).resolve().parents[2] / "artifacts" / "model.joblib"
RANDOM_STATE = 42


def build_pipeline(X) -> Pipeline:
    """Construit le pipeline preprocessing + modèle.

    Les colonnes numériques sont standardisées (uile pour la convergence de la
    régression logistique) ; les colonnes catégorielles sont encodées en one-hot.
    `handle_unknown="ignore"` rend le modèle robuste à une modalité jamais vue en
    production (ex. une valeur inattendue reçue par l'API).
    """
    numeric_cols = X.select_dtypes(include=["int64", "float64"]).columns.tolist()
    categorical_cols = X.select_dtypes(include=["object"]).columns.tolist()

    preprocessor = ColumnTransformer(
        transformers=[
            ("num", StandardScaler(), numeric_cols),
            ("cat", OneHotEncoder(handle_unknown="ignore"), categorical_cols),
        ]
    )

    # class_weight="balanced" : la classe "churn" ne représente que ~26,5 % des
    # clients. Sans pondération, le modèle est tenté de toujours prédire "pas de
    # churn". On rééquilibre pour ne pas rater les clients à risque (recall).
    model = LogisticRegression(max_iter=1000, class_weight="balanced")

    return Pipeline([("preprocess", preprocessor), ("model", model)])


def main() -> None:
    df = clean(load_raw())
    X, y = split_features_target(df)

    X_train, X_test, y_train, y_test = train_test_split(
        X, y, test_size=0.2, stratify=y, random_state=RANDOM_STATE
    )

    pipeline = build_pipeline(X_train)
    pipeline.fit(X_train, y_train)

    y_pred = pipeline.predict(X_test)
    y_proba = pipeline.predict_proba(X_test)[:, 1]

    # --- Métriques ---
    # L'accuracy seule est trompeuse ici : un modèle naïf qui prédit toujours
    # "pas de churn" atteint déjà ~73,5 % d'accuracy sans rien apprendre. On
    # regarde donc surtout :
    #   - recall (classe churn) : quelle proportion des résiliations on détecte
    #     -> c'est l'enjeu métier (retenir les clients avant qu'ils partent) ;
    #   - precision : parmi les clients alertés, combien churnent vraiment ;
    print("=== Baseline naïve (prédit toujours 'pas de churn') ===")
    print(f"accuracy = {(y_test == 0).mean():.4f}  (recall churn = 0)")
    print("\n=== Régression logistique ===")
    print(classification_report(y_test, y_pred, target_names=["No", "Yes"], digits=4))
    print(f"ROC-AUC : {roc_auc_score(y_test, y_proba):.4f}")
    print("\nMatrice de confusion [ligne=vrai, colonne=prédit] :")
    print(confusion_matrix(y_test, y_pred))

    ARTIFACT_PATH.parent.mkdir(parents=True, exist_ok=True)
    joblib.dump(pipeline, ARTIFACT_PATH)
    print(f"\nModèle sauvegardé -> {ARTIFACT_PATH}")


if __name__ == "__main__":
    main()
