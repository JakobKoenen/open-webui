# Agentic AI Planner Backend

FastAPI Backend für den Agentic AI Planner Step mit Azure OpenAI Integration.

## 🎯 Funktionalität

Dieses Backend stellt einen Agentic AI Planner Agent bereit, der:
- Benutzeranfragen analysiert
- Strukturierte Pläne erstellt
- Priorisierte Schritte generiert
- Komplexe Aufgaben zerlegt

## 🚀 Schnellstart

### Mit Docker (empfohlen)

```bash
# Aus dem Hauptverzeichnis
docker-compose up -d planner-backend
```

### Lokale Entwicklung

```bash
cd backend

# Virtual Environment erstellen
python -m venv venv
source venv/bin/activate  # Windows: venv\Scripts\activate

# Dependencies installieren
pip install -r requirements.txt

# Server starten
python main.py
```

Der Server läuft auf `http://localhost:8000`

## 📡 API Endpoints

### Health Check
```bash
GET /health
```

### Planner Step
```bash
POST /api/v1/planner
```

**Request Body:**
```json
{
  "message": "Erstelle einen Plan für X",
  "conversation_history": [
    {"role": "user", "content": "Vorherige Nachricht"},
    {"role": "assistant", "content": "Vorherige Antwort"}
  ]
}
```

**Response:**
```json
{
  "result": "Strukturierter Plan...",
  "status": "success"
}
```

### Chat Endpoint
```bash
POST /api/v1/chat
```
Alias für `/api/v1/planner` - für einfache Chat-Integration.

## ⚙️ Konfiguration

### Environment Variables

Kopieren Sie `env.template` zu `.env` und konfigurieren Sie:

```bash
AZURE_OPENAI_ENDPOINT=https://your-resource-name.openai.azure.com/
AZURE_OPENAI_API_KEY=your_azure_openai_api_key_here
AZURE_OPENAI_DEPLOYMENT_NAME=gpt-4
AZURE_OPENAI_API_VERSION=2024-02-15-preview
BACKEND_PORT=8000
```

### Azure OpenAI Setup

1. Erstellen Sie eine Azure OpenAI Resource im Azure Portal
2. Stellen Sie ein Modell bereit (z.B. GPT-4, GPT-3.5-turbo)
3. Kopieren Sie Endpoint und API Key
4. Fügen Sie diese in `.env` ein

## 🔧 Entwicklung

### Dependencies

- `fastapi`: Web Framework
- `uvicorn`: ASGI Server
- `openai`: Azure OpenAI Client
- `pydantic`: Data Validation
- `python-dotenv`: Environment Variables

### Struktur

```
backend/
├── main.py              # FastAPI Application
├── requirements.txt     # Python Dependencies
├── Dockerfile          # Docker Image
├── .dockerignore       # Docker Ignore Rules
└── README.md           # Diese Datei
```

## 📚 Dokumentation

Nach dem Start ist die API Dokumentation verfügbar unter:
- Swagger UI: `http://localhost:8000/docs`
- ReDoc: `http://localhost:8000/redoc`

## 🔌 Open WebUI Integration

Das Backend ist für die Integration mit Open WebUI vorbereitet:

1. Backend läuft auf Port 8000
2. Open WebUI läuft auf Port 3000
3. Beide Services sind im gleichen Docker Network
4. Open WebUI kann das Backend via `http://planner-backend:8000` erreichen

## 🧪 Testing

```bash
# Health Check
curl http://localhost:8000/health

# Planner Test
curl -X POST http://localhost:8000/api/v1/planner \
  -H "Content-Type: application/json" \
  -d '{"message": "Erstelle einen Plan für ein neues Projekt"}'
```

## 📝 Logs

```bash
# Docker Logs
docker logs -f agentic-ai-planner-backend

# Docker Compose Logs
docker-compose logs -f planner-backend
```

## 🔄 Erweiterte Konfiguration

### System Prompt anpassen

Bearbeiten Sie `PLANNER_SYSTEM_PROMPT` in `main.py` für spezifische Anforderungen.

### Model Parameters

Anpassen in der `planner_step` Funktion:
```python
response = client.chat.completions.create(
    model=AZURE_OPENAI_DEPLOYMENT_NAME,
    messages=messages,
    temperature=0.7,    # Kreativität (0.0-1.0)
    max_tokens=2000     # Max. Ausgabe-Länge
)
```
