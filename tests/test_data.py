"""Tests de la préparation des données.

On vérifie le comportement de nettoyage le plus risqué : la colonne TotalCharges
arrive en texte avec des valeurs vides, et l'identifiant doit disparaître.
"""
import pandas as pd
import pytest

from churn.data import clean, split_features_target, ID_COLUMN, TARGET


def _raw_sample() -> pd.DataFrame:
    # Échantillon minimal reproduisant le piège : TotalCharges en texte avec un vide.
    return pd.DataFrame(
        {
            "customerID": ["0001-AAAA", "0002-BBBB"],
            "tenure": [0, 12],
            "MonthlyCharges": [50.0, 70.0],
            "TotalCharges": [" ", "840.0"],  # <-- piège : texte + valeur vide
            "Churn": ["No", "Yes"],
        }
    )


def test_clean_returns_dataframe():
    out = clean(_raw_sample())
    assert isinstance(out, pd.DataFrame)


def test_total_charges_is_numeric_after_clean():
    """La colonne texte doit devenir numérique."""
    out = clean(_raw_sample())
    assert pd.api.types.is_numeric_dtype(out["TotalCharges"])


def test_empty_total_charges_imputed_to_zero():
    """La valeur vide (client à tenure 0) doit être imputée à 0, pas laissée en NaN."""
    out = clean(_raw_sample())
    assert out["TotalCharges"].isna().sum() == 0
    assert out.loc[0, "TotalCharges"] == 0.0


def test_id_column_is_dropped():
    """L'identifiant ne doit pas servir de feature."""
    out = clean(_raw_sample())
    assert ID_COLUMN not in out.columns


def test_split_target_is_binary_and_excluded_from_features():
    """La cible est encodée en 0/1 et retirée des features."""
    out = clean(_raw_sample())
    X, y = split_features_target(out)
    assert set(y.unique()).issubset({0, 1})
    assert TARGET not in X.columns
    assert y.tolist() == [0, 1]  # No -> 0, Yes -> 1
