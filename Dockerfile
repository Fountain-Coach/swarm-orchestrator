FROM python:3.11-slim

WORKDIR /app
ENV PYTHONPATH=/app    

# Install only what's needed
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt \
    && pip install --no-cache-dir pytest httpx

# Copy entire repo layout
COPY . .

# Expose for FastAPI
EXPOSE 8000

# Always call entrypoint.py
CMD ["python", "app/entrypoint.py"]