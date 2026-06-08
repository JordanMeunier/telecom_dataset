"""Entraînement et évaluation du modèle.

TODO:
  - Construis un pipeline de preprocessing + modèle (évite la fuite de données).
  - Sépare train/test correctement (pense au déséquilibre des classes).
  - Choisis et AFFICHE des métriques pertinentes (pas seulement l'accuracy).
  - Sauvegarde le modèle entraîné.
"""
from __future__ import annotations

from pathlib import Path

ARTIFACT_PATH = Path(__file__).resolve().parents[2] / "artifacts" / "model.joblib"


def main() -> None:
    raise NotImplementedError


if __name__ == "__main__":
    main()
