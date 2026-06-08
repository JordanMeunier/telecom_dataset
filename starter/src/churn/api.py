"""API d'inférence.

TODO:
  - GET  /health  -> statut du service
  - POST /predict -> reçoit les features d'un client (JSON), renvoie
    {"churn_probability": float, "churn": bool}
  - Gère proprement une entrée invalide (champ manquant / mauvais type).

FastAPI est recommandé (voir requirements). Flask est accepté.
"""
from fastapi import FastAPI

app = FastAPI(title="Churn API")


@app.get("/health")
def health():
    raise NotImplementedError


# TODO: définir le schéma d'entrée (Pydantic) et la route POST /predict
