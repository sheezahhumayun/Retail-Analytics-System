FROM python:3.11-slim

WORKDIR /app

RUN apt-get update \
    && apt-get install -y --no-install-recommends \
        libgl1 \
        libglib2.0-0 \
    && rm -rf /var/lib/apt/lists/*

COPY backend/requirements.txt backend/requirements.txt
COPY database/requirements.txt database/requirements.txt

RUN pip install --no-cache-dir -r backend/requirements.txt -r database/requirements.txt

COPY backend/ backend/
COPY database/ database/
COPY analytics/ analytics/
COPY inference/ inference/
COPY sample-data/ sample-data/

RUN mkdir -p data/heatmaps data/frame-previews data/run

COPY backend/docker-entrypoint.sh /docker-entrypoint.sh
RUN chmod +x /docker-entrypoint.sh

ENV PYTHONPATH=/app
ENV SPAWN_INFERENCE_SUBPROCESS=false

EXPOSE 8000

ENTRYPOINT ["/docker-entrypoint.sh"]
