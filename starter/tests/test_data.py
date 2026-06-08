"""Tests de la préparation des données.

Un test d'exemple est fourni. AJOUTE au moins un test pertinent
(ex. : la colonne TotalCharges est bien numérique après nettoyage,
les valeurs vides sont gérées, la cible est binaire...).
"""
import pandas as pd

from churn.data import clean


def _raw_sample() -> pd.DataFrame:
    # Échantillon minimal reproduisant un piège : TotalCharges en texte avec un vide.
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


# TODO: ajoute un test qui vérifie un comportement de nettoyage précis.
