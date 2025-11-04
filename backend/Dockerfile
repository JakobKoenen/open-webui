FROM python:3.11-slim

WORKDIR /app

# Dependencies installieren
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Application Code kopieren (wird in Dev-Mode durch Volume überschrieben)
COPY . .

# Expose Port
EXPOSE 8000

# Healthcheck
HEALTHCHECK --interval=30s --timeout=10s --start-period=5s --retries=3 \
  CMD python -c "import requests; requests.get('http://localhost:8000/health')"

# Server starten mit optionalem Reload
CMD sh -c "if [ \"$DEV_MODE\" = \"true\" ]; then uvicorn main:app --host 0.0.0.0 --port 8000 --reload; else uvicorn main:app --host 0.0.0.0 --port 8000; fi"

