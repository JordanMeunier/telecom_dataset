"""Téléverse l'artefact du modèle vers un bucket S3 (boto3).

TODO:
  - Téléverse artifacts/model.joblib vers s3://<bucket>/<key>.
  - Gère les erreurs (fichier absent, credentials manquants, erreur S3).
  - AUCUNE clé d'accès en dur : utilise la chaîne de credentials standard de boto3
    (variables d'environnement, profil, rôle IAM...).

Exemple d'usage visé :
    python scripts/upload_to_s3.py --bucket mon-bucket --key models/model.joblib
"""
from __future__ import annotations

import argparse


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--bucket", required=True)
    parser.add_argument("--key", default="models/model.joblib")
    parser.parse_args()
    raise NotImplementedError


if __name__ == "__main__":
    main()
