# API NidBuyer — deployee sur Cloud Run
FROM python:3.12-slim
WORKDIR /app

# torch en version CPU : image ~4x plus legere que la version CUDA, inutile sur Cloud Run
RUN pip install --no-cache-dir torch --index-url https://download.pytorch.org/whl/cpu
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Modele d'embedding telecharge au build, pas au demarrage : demarrage a froid plus court
ARG EMBEDDING_MODEL=paraphrase-multilingual-MiniLM-L12-v2
ENV EMBEDDING_MODEL=${EMBEDDING_MODEL}
RUN python -c "from sentence_transformers import SentenceTransformer; SentenceTransformer('${EMBEDDING_MODEL}')"

COPY backend/ backend/
COPY vision/ vision/
COPY prompts/ prompts/
COPY data/ data/

ENV CHROMA_PATH=/tmp/chroma_db
CMD exec uvicorn backend.main:app --host 0.0.0.0 --port ${PORT:-8080}
