"""Téléverse l'artefact du modèle vers un bucket S3 (boto3).

Usage :
    python scripts/upload_to_s3.py --bucket mon-bucket --key models/model.joblib
"""
from __future__ import annotations

import argparse
import sys
from pathlib import Path

import boto3
from botocore.exceptions import BotoCoreError, ClientError, NoCredentialsError

DEFAULT_ARTIFACT = Path(__file__).resolve().parents[1] / "artifacts" / "model.joblib"


def upload(artifact: Path, bucket: str, key: str) -> None:
    """Téléverse `artifact` vers s3://bucket/key. Lève une exception en cas d'échec."""
    if not artifact.is_file():
        raise FileNotFoundError(
            f"Artefact introuvable : {artifact}. Lancer d'abord l'entraînement."
        )

    s3 = boto3.client("s3")
    s3.upload_file(str(artifact), bucket, key)


def main() -> int:
    parser = argparse.ArgumentParser(description="Upload du modèle vers S3.")
    parser.add_argument("--bucket", required=True, help="Nom du bucket S3 cible.")
    parser.add_argument("--key", default="models/model.joblib", help="Clé S3 (chemin).")
    parser.add_argument(
        "--artifact",
        type=Path,
        default=DEFAULT_ARTIFACT,
        help="Chemin local de l'artefact à téléverser.",
    )
    args = parser.parse_args()

    try:
        upload(args.artifact, args.bucket, args.key)
    except FileNotFoundError as e:
        print(f"[erreur] {e}", file=sys.stderr)
        return 1
    except NoCredentialsError:
        print(
            "[erreur] Aucun credential AWS trouvé. Configure AWS_ACCESS_KEY_ID/"
            "AWS_SECRET_ACCESS_KEY, un profil, ou un rôle IAM.",
            file=sys.stderr,
        )
        return 1
    except (ClientError, BotoCoreError) as e:
        print(f"[erreur] Échec de l'upload S3 : {e}", file=sys.stderr)
        return 1

    print(f"OK -> s3://{args.bucket}/{args.key}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
