"""Chargement et préparation des données.
Les décisions de nettoyage sont commentées ici et justifiées dans le README"""

from __future__ import annotations

from pathlib import Path
import pandas as pd

DATA_PATH = Path(__file__).resolve().parents[2] / "data" / "telco_churn.csv"
TARGET = "Churn"

ID_COLUMN = "customerID"


def load_raw(path: Path | str = DATA_PATH) -> pd.DataFrame:
    """Charge le CSV brut, sans transformation."""
    return pd.read_csv(path)


def clean(df: pd.DataFrame) -> pd.DataFrame:
    """Nettoie le DataFrame.

    Deux problèmes réels sont présents dans ce dataset :

    1. `TotalCharges` est stockée en TEXTE (dtype object) alors que c'est un
       montant. La cause : 11 lignes contiennent une chaîne vide " " au lieu
       d'un nombre. Ces 11 clients ont tous `tenure == 0` (ils viennent de
       souscrire et n'ont donc jamais été facturés). On convertit la colonne en
       numérique (les " " deviennent NaN) puis on impute ces NaN à 0, ce qui est
       cohérent métier : 0 mois d'ancienneté => 0 facturé. Aucune ligne n'est
       perdue.

    2. `customerID` est un identifiant : on le supprime (cf. ID_COLUMN).
    """
    df = df.copy()

    # 1. TotalCharges : texte -> numérique. errors="coerce" transforme les " "
    #    en NaN, qu'on impute ensuite à 0 (clients à tenure == 0, jamais facturés).
    df["TotalCharges"] = pd.to_numeric(df["TotalCharges"], errors="coerce")
    df["TotalCharges"] = df["TotalCharges"].fillna(0.0)

    # 2. Suppression de l'identifiant.
    df = df.drop(columns=[ID_COLUMN])

    return df


def split_features_target(df: pd.DataFrame):
    """Sépare X (features) et y (cible) après nettoyage.

    La cible `Churn` ("Yes"/"No") est encodée en 1/0 ("Yes" = churn = 1, la
    classe que l'on cherche à détecter). AUCUN encodage des features
    ici : il est délégué au pipeline scikit-learn (cf. train.py) pour qu'il soit
    appris uniquement sur les données d'entraînement et éviter toute fuite.
    """
    y = (df[TARGET] == "Yes").astype(int)
    X = df.drop(columns=[TARGET])
    return X, y
