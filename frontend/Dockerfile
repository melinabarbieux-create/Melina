# Interface Streamlit — deuxieme service Cloud Run
# Deploiement : gcloud run deploy nidbuyer-front-<groupe> --source frontend ...
FROM python:3.12-slim
WORKDIR /app
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt
COPY app.py .
CMD exec streamlit run app.py --server.port ${PORT:-8080} --server.address 0.0.0.0 --server.headless true
