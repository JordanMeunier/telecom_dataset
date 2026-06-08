# Churn Prediction — Test technique

Prédiction de résiliation (churn) de clients télécom, exposée via une API et
conteneurisée avec Docker.

## Prérequis
- Python 3.14+
- Docker (pour la partie conteneur)

## Installation
```bash
python -m venv .venv && source .venv/bin/activate
pip install -r requirements.txt
```

> Note : les versions de `requirements.txt` ont été remontées par rapport au
> squelette d'origine. Les pins initiaux (ex. `pandas==2.2.2`, `scikit-learn==1.5.1`)
> n'ont pas de wheel précompilé pour Python 3.14 et tentaient une compilation
> depuis les sources qui échoue. J'ai retenu les versions stables les plus
> proches disposant d'un wheel 3.14.

## Récupérer les données
```bash
python scripts/download_data.py   # -> data/telco_churn.csv
```

## Lancer l'entraînement
```bash
PYTHONPATH=src python -m churn.train   # -> artifacts/model.joblib + métriques
```

## Lancer l'API (en local)
```bash
PYTHONPATH=src uvicorn churn.api:app --reload
# http://localhost:8000/health  ·  doc interactive : http://localhost:8000/docs
```

Exemple d'appel :
```bash
curl -X POST http://localhost:8000/predict -H "Content-Type: application/json" \
  -d '{"gender":"Female","SeniorCitizen":0,"Partner":"Yes","Dependents":"No","tenure":1,
       "PhoneService":"No","MultipleLines":"No phone service","InternetService":"DSL",
       "OnlineSecurity":"No","OnlineBackup":"Yes","DeviceProtection":"No","TechSupport":"No",
       "StreamingTV":"No","StreamingMovies":"No","Contract":"Month-to-month",
       "PaperlessBilling":"Yes","PaymentMethod":"Electronic check",
       "MonthlyCharges":29.85,"TotalCharges":29.85}'
# -> {"churn_probability":0.8064,"churn":true}
```

## Tests
```bash
PYTHONPATH=src pytest
```

## Docker
```bash
docker build -t churn-api .
docker run --rm -p 8000:8000 churn-api
# ou, en une commande :
docker compose up --build
```
L'API est alors joignable sur http://localhost:8000. Image ~536 Mo
(base `python:3.14-slim`, utilisateur non-root, `.dockerignore` pour exclure
données/venv/tests, cache des dépendances via copie de `requirements.txt` en
premier).

---

## Décisions de nettoyage des données

L'inspection (types, valeurs manquantes, distribution de la cible) révèle **deux
problèmes réels** ; je ne corrige que ceux-là pour rester justifiable.

| Décision | Pourquoi | Impact |
|---|---|---|
| **`TotalCharges` : texte → numérique, puis NaN imputés à 0** | La colonne est de type `object` à cause de **11 lignes contenant `" "`** (chaîne vide). Ces 11 clients ont **tous `tenure == 0`** : ils viennent de souscrire et n'ont jamais été facturés. `pd.to_numeric(errors="coerce")` transforme les `" "` en NaN, imputés à `0.0` (cohérent : 0 mois ⇒ 0 facturé). | Colonne utilisable comme variable numérique, **aucune ligne perdue** (vs. ~0,16 % si on les supprimait). |
| **Suppression de `customerID`** | Identifiant unique (7043 valeurs distinctes / 7043 lignes). Aucune information prédictive ; le garder ajoute du bruit / un risque de sur-apprentissage. | Retiré des features. |
| Encodage de la cible `Churn` (`Yes`/`No` → `1`/`0`) | Nécessaire pour la classification ; `Yes` = churn = classe positive à détecter. | — |

Le reste de l'encodage (one-hot des catégorielles, standardisation des
numériques) **n'est pas fait en dur** : il est intégré au pipeline scikit-learn
pour être appris uniquement sur le train (anti-fuite, voir ci-dessous).

## Choix des métriques

La cible est **déséquilibrée : 73,5 % `No` / 26,5 % `Yes`**. Conséquence :

- Un **modèle naïf** qui prédit toujours « pas de churn » obtient déjà **~73,5 %
  d'accuracy**… mais détecte **0 %** des résiliations. L'accuracy seule est donc
  **trompeuse** et ne peut pas être la métrique principale.

Je regarde donc :
- **Recall (classe churn)** — *métrique métier prioritaire* : quelle proportion
  des clients qui partent réellement on parvient à détecter pour les retenir.
- **Precision (churn)** — parmi les clients alertés, combien churnent vraiment
  (coût des actions de rétention inutiles).
- **F1** — compromis precision/recall.
- **ROC-AUC** — qualité du classement par probabilité, indépendant du seuil 0,5.

**Résultats** (jeu de test, 20 %, `class_weight="balanced"`) :

| | precision | recall | f1 |
|---|---|---|---|
| No | 0,90 | 0,72 | 0,80 |
| **Yes (churn)** | **0,50** | **0,78** | **0,61** |

**ROC-AUC ≈ 0,84.** Le modèle détecte **78 % des résiliations** (contre 0 % pour
la baseline naïve), au prix d'une precision plus basse — compromis assumé : en
rétention, **rater un client qui part coûte plus cher** qu'alerter à tort.

### Choix du modèle : régression logistique
Conformément à la consigne (« la simplicité est valorisée »), j'ai choisi la
**régression logistique** plutôt qu'un arbre seul :
- baseline de référence pour le churn, rapide et interprétable (coefficients) ;
- elle produit des **probabilités bien calibrées**, ce dont l'API a besoin ;
- un arbre seul sur-apprend vite et donne des probabilités « en escalier ».

`class_weight="balanced"` compense le déséquilibre des classes.

### Anti-fuite de données
Tout le preprocessing (`StandardScaler`, `OneHotEncoder`) est encapsulé dans un
`Pipeline` scikit-learn, **`fit` uniquement sur le train**. Le `train_test_split`
utilise `stratify=y` pour conserver la proportion de churn dans les deux jeux.

---

## Déploiement AWS

**Stockage du modèle.** L'artefact `model.joblib` est versionné dans **S3**
(`s3://<bucket>/models/model.joblib`), avec versioning activé pour pouvoir
revenir à un modèle précédent. Le script `scripts/upload_to_s3.py` (boto3) gère
l'upload et les erreurs (fichier absent, credentials manquants, erreur S3) — sans
aucune clé en dur. L'image Docker peut soit embarquer l'artefact au build, soit
le télécharger depuis S3 au démarrage (découple le modèle du code).

**Exécution du conteneur.** Deux options :
- **AWS App Runner** — on lui donne l'image (depuis **ECR**), il gère le scaling,
  HTTPS et l'exposition automatiquement. *Compromis* : très simple, idéal ici,
  mais moins de contrôle réseau fin.
- **ECS Fargate** — conteneurs serverless derrière un **Application Load
  Balancer**. *Compromis* : plus de contrôle (VPC, autoscaling, multi-services)
  mais plus de configuration. Je partirais sur **App Runner** vu la taille du
  projet, ECS Fargate si le besoin grandit.

**Exposition.** App Runner fournit une URL HTTPS managée. En ECS, l'API est
exposée via l'ALB (+ ACM pour TLS, éventuellement API Gateway devant pour
l'authentification/throttling).

**Secrets.** Jamais de clé en dur : un **rôle IAM** attaché à la tâche donne
l'accès à S3 ; tout secret applicatif passe par **AWS Secrets Manager** /
SSM Parameter Store, injecté en variable d'environnement.

**Logs & monitoring.** Logs applicatifs (uvicorn) vers **CloudWatch Logs** ;
métriques (latence, taux d'erreur, nb de requêtes) sur **CloudWatch** avec une
alarme sur le taux de 5xx. À surveiller à plus long terme : le **drift** des
données d'entrée.

**Coût.** Petite charge : App Runner ou une tâche Fargate de petite taille
coûtent quelques dollars à quelques dizaines de dollars/mois ; S3 et CloudWatch
sont négligeables à ce volume. On peut scaler à zéro / au minimum hors charge.
```bash
python scripts/upload_to_s3.py --bucket mon-bucket --key models/model.joblib
```
