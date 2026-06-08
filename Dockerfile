FROM python:3.14-slim

ENV PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1 \
    PYTHONPATH=/app/src

WORKDIR /app

# On copie d'ABORD requirements.txt : tant qu'il ne change pas, Docker réutilise
# le cache de cette couche et ne réinstalle pas les dépendances à chaque build.
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Puis le code + l'artefact du modèle
COPY src/ ./src/
COPY artifacts/ ./artifacts/

# bonus user non-root
RUN useradd --create-home appuser
USER appuser

EXPOSE 8000

CMD ["uvicorn", "churn.api:app", "--host", "0.0.0.0", "--port", "8000"]
