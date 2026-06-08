
**Durée indicative : 2 h 30 à 3 h** · Niveau Bac+3 · Take-home

Bienvenue. Ce test évalue ta capacité à manipuler des données réelles (avec leurs imperfections), à entraîner un modèle simple **proprement**, à packager ton code avec **Docker**, et à raisonner sur un **déploiement AWS**.

> On ne cherche **pas** le meilleur score possible. On cherche un travail **rigoureux, lisible et honnête**. Mieux vaut un pipeline propre et bien justifié qu'un modèle complexe mal maîtrisé. **Documente tes choix** : c'est ce qui compte le plus.

---

## Contexte métier

Un opérateur télécom veut anticiper le **churn** (résiliation) de ses clients pour les retenir. On te confie un extrait de leur base clients. Ta mission : construire un modèle qui prédit si un client va résilier (`Churn = Yes`), l'exposer via une petite API, et expliquer comment tu le mettrais en production sur AWS.

## Le dataset

**Telco Customer Churn** (IBM, public). Environ 7 000 clients, 21 colonnes (caractéristiques du contrat, services souscrits, facturation), cible = `Churn`.

Un script de téléchargement est fourni : `python scripts/download_data.py` (récupère le CSV dans `data/`). Tu peux aussi le retrouver sur Kaggle ("Telco Customer Churn") si besoin.

Attention : **les données ne sont pas propres.** À toi de les inspecter avant de coder quoi que ce soit. Une exploration bâclée se paie au moment de l'entraînement.

---

## Ce qui est attendu

### Partie 1 — Exploration & nettoyage des données (Python / pandas)

1. Charge le CSV et **explore-le réellement** : types des colonnes, valeurs manquantes, distribution de la cible, cohérence des valeurs.
2. Nettoie ce qui doit l'être. Pour chaque décision de nettoyage, **écris un commentaire ou une ligne dans le README expliquant pourquoi** (pourquoi tu supprimes / imputes / convertis, et l'impact).
3. Sépare proprement les données pour l'entraînement et l'évaluation.

> Une bonne question à se poser : est-ce que `df.describe()` te montre vraiment tout ? Est-ce que toutes tes colonnes ont le bon type ? Regarde aussi **quelle proportion** de clients a réellement résilié.

### Partie 2 — Modélisation (ML / scikit-learn)

1. Entraîne un modèle de classification (régression logistique, arbre, random forest… au choix — la simplicité est valorisée).
2. **Choisis et justifie tes métriques d'évaluation.** Explique pourquoi tu les regardes.
3. Évite toute fuite de données entre l'étape d'entraînement et l'évaluation.
4. Sauvegarde le modèle entraîné (ex. `model.joblib`) dans `data/` ou `artifacts/`.

> Sur ce dataset, un modèle qui prédit toujours « pas de churn » obtient déjà un score d'*accuracy* élevé. Est-ce un bon modèle ? Que regarderais-tu à la place ?

### Partie 3 — API d'inférence (Python)

1. Expose le modèle via une petite API HTTP (FastAPI recommandé, Flask accepté).
2. Au minimum :
   - `GET /health` → statut du service.
   - `POST /predict` → reçoit les caractéristiques d'un client (JSON), renvoie la probabilité de churn et la classe prédite.
3. Gère au moins un cas d'entrée invalide (champ manquant / mauvais type) sans planter.

### Partie 4 — Docker

1. Écris un `Dockerfile` qui build l'API et la lance.
2. L'image doit démarrer avec une commande simple (documentée dans le README).
3. Bonus : `docker-compose.yml`, image multi-stage, image légère (slim), utilisateur non-root.

> Une image qui pèse 2 Go ou qui réinstalle tout à chaque build perd des points. Pense à ce qui doit vraiment être copié dans l'image (`.dockerignore`).

### Partie 5 — Déploiement AWS (écrit + un peu de code)

Rédige dans le README une section **« Déploiement AWS »** (~15-25 lignes) expliquant comment tu mettrais cette API en production :
- Où stockerais-tu l'artefact du modèle ? (indice : un service de stockage objet)
- Comment exécuterais-tu le conteneur sur AWS ? Cite 1 ou 2 options et leurs compromis.
- Comment exposerais-tu l'API au monde extérieur ?
- Un mot sur les **secrets**, les **logs/monitoring**, et le **coût**.

**Code demandé :** complète `scripts/upload_to_s3.py` pour téléverser l'artefact du modèle dans un bucket S3 avec `boto3` (le bucket peut être fictif ; on regarde la qualité du code, la gestion d'erreur et la non-exposition des credentials — **aucune clé en dur**).

---

## Livrables

Un dépôt Git (ou un zip) contenant :

- Tout le code (`src/`, `scripts/`, `tests/`).
- Le `Dockerfile` (+ `docker-compose.yml` en bonus).
- Un **`README.md`** qui explique : comment lancer le projet, **tes décisions de nettoyage et leur justification**, le choix des métriques, et la section « Déploiement AWS ».
- Au moins **un test** automatisé (`pytest`) sur la logique de préparation des données.

## Comment on évalue (transparence)

| Domaine | Poids |
|---|---|
| Exploration / nettoyage des données + justifications | 30 % |
| Modélisation & choix des métriques | 25 % |
| Qualité du code Python (lisibilité, structure, tests, gestion d'erreurs) | 20 % |
| Docker | 15 % |
| Déploiement AWS (raisonnement + script S3) | 10 % |

**Ce qui fait la différence** : repérer les pièges des données sans qu'on te les pointe, justifier tes choix, et un code que quelqu'un d'autre pourrait reprendre.

## Conseils

- Ne cherche pas l'exhaustivité : un périmètre maîtrisé vaut mieux qu'un projet à moitié fini partout.
- Commits réguliers et lisibles appréciés.
- Si tu manques de temps sur une partie, **écris dans le README ce que tu aurais fait**. C'est valorisé.
- L'usage d'outils d'IA est autorisé, mais tu dois pouvoir **expliquer chaque ligne** en entretien.

Bonne chance.
