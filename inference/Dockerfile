FROM python:3.11-slim

WORKDIR /app

RUN apt-get update \
    && apt-get install -y --no-install-recommends \
        libgl1 \
        libglib2.0-0 \
    && rm -rf /var/lib/apt/lists/*

COPY inference/requirements.txt inference/requirements.txt

# CPU-only PyTorch before ultralytics to avoid pulling a CUDA wheel.
RUN pip install --no-cache-dir \
        torch torchvision \
        --index-url https://download.pytorch.org/whl/cpu

RUN pip install --no-cache-dir -r inference/requirements.txt

RUN python -c "import cv2; import torch; print('opencv', cv2.__version__); print('torch', torch.__version__); assert not torch.cuda.is_available()"

COPY backend/ backend/
COPY database/ database/
COPY analytics/ analytics/
COPY inference/ inference/
COPY sample-data/ sample-data/
COPY tests/ tests/

RUN mkdir -p data/heatmaps data/frame-previews data/run inference/models

ENV PYTHONPATH=/app
ENV PYTHONUNBUFFERED=1

CMD ["python", "-m", "inference.pipeline.live_analytics_worker", "--reconcile-interval", "30"]
