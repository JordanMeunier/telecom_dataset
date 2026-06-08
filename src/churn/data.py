"""Chargement et préparation des données.

Complète les fonctions ci-dessous et JUSTIFIE tes choix (commentaires + README).
"""
from __future__ import annotations

from pathlib import Path
import pandas as pd

DATA_PATH = Path(__file__).resolve().parents[2] / "data" / "telco_churn.csv"
TARGET = "Churn"


def load_raw(path: Path | str = DATA_PATH) -> pd.DataFrame:
    """Charge le CSV brut, sans transformation."""
    return pd.read_csv(path)


def clean(df: pd.DataFrame) -> pd.DataFrame:
    """Nettoie le DataFrame.

    TODO:
      - Regarde le type de CHAQUE colonne. Certaines ne sont pas du type attendu.
      - Cherche les valeurs manquantes / vides (elles ne sont pas toujours des NaN).
      - Décide quoi faire des colonnes inutiles ou dangereuses pour le modèle.
      - Documente chaque décision et son impact.
    """
    raise NotImplementedError


def split_features_target(df: pd.DataFrame):
    """Sépare X (features) et y (cible) après nettoyage.

    TODO: renvoie (X, y). Pense à encoder la cible et à exclure ce qui ne doit
    pas servir de feature.
    """
    raise NotImplementedError
