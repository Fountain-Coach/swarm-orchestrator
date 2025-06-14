FROM python:3.11-slim

RUN apt-get update \
    && apt-get install -y --no-install-recommends docker.io \
    && rm -rf /var/lib/apt/lists/*

WORKDIR /app
ENV PYTHONPATH=/app    

COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt \
    && pip install pytest httpx

COPY app/ ./app/
COPY tests/ ./tests/
COPY fountainai-stack.yml ./fountainai-stack.yml

EXPOSE 8000

CMD ["python", "app/entrypoint.py"]