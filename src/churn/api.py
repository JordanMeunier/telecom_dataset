"""API d'inférence (FastAPI).

  - GET  /health  -> statut du service
  - POST /predict -> reçoit les features d'un client (JSON), renvoie
    {"churn_probability": float, "churn": bool}

La validation des entrées est déléguée à Pydantic : un champ manquant ou d'un
mauvais type renvoie automatiquement une réponse 422 explicite, sans planter.
"""
from __future__ import annotations

from pathlib import Path

import joblib
import pandas as pd
from fastapi import FastAPI, HTTPException

from churn.features import CustomerFeatures

ARTIFACT_PATH = Path(__file__).resolve().parents[2] / "artifacts" / "model.joblib"

app = FastAPI(title="Churn API")

# Le modèle est chargé une seule fois au démarrage (pas à chaque requête).
try:
    _model = joblib.load(ARTIFACT_PATH)
except FileNotFoundError:
    _model = None


@app.get("/health")
def health():
    """Statut du service et disponibilité du modèle."""
    return {"status": "ok", "model_loaded": _model is not None}


@app.post("/predict")
def predict(features: CustomerFeatures):
    """Prédit la probabilité de churn pour un client."""
    if _model is None:
        raise HTTPException(
            status_code=503,
            detail="Modèle indisponible. Lancer l'entraînement (python -m churn.train).",
        )

    row = pd.DataFrame([features.model_dump()])
    proba = float(_model.predict_proba(row)[0, 1])
    return {"churn_probability": round(proba, 4), "churn": proba >= 0.5}
