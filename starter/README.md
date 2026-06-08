# Churn Prediction — Test technique (squelette de départ)

Ce dépôt est un **point de départ**. Complète les `TODO`, remplis ce README avec tes décisions, et livre le tout.

## Prérequis
- Python 3.14+
- Docker (pour la partie conteneur)

## Installation
```bash
python -m venv .venv && source .venv/bin/activate
pip install -r requirements.txt
```

## Récupérer les données
```bash
python scripts/download_data.py
# -> écrit data/telco_churn.csv
```

## Lancer l'entraînement
```bash
python -m churn.train          # à compléter
```

## Lancer l'API (en local)
```bash
uvicorn churn.api:app --reload  # à compléter
```

## Tests
```bash
pytest
```

## Docker
```bash
# TODO: documenter la commande de build et de run
```

---

## ✍️ À remplir par le candidat

### Décisions de nettoyage des données
> Explique ici CE QUE tu as nettoyé et POURQUOI (avec l'impact). Une décision sans justification ne compte pas.

- ...

### Choix des métriques
> Quelles métriques regardes-tu et pourquoi ? Que vaut un modèle "naïf" ici ?

- ...

### Déploiement AWS
> ~15-25 lignes : stockage du modèle, exécution du conteneur, exposition de l'API, secrets, logs, coût.

- ...
