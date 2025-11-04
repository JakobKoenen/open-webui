# Agentic AI Process - Open WebUI Integration

Dieses Projekt verbindet Open WebUI (mit Admin-Interface) mit einem eigenen FastAPI Backend für Azure OpenAI Integration.

## 🎯 Struktur

- **Backend** (`./backend/`): FastAPI Backend mit Azure OpenAI Integration
  - Port: 8000
  - OpenAI-kompatible API: `/v1/chat/completions`
  - Models API: `/v1/models`
  
- **Frontend** (Open WebUI): SvelteKit-basiertes Admin-Interface
  - Port: 3000
  - Admin-Route: `/admin`
  - Verbunden mit Backend über `OPENAI_API_BASE_URL`

## 🚀 Installation

### Voraussetzungen

- Docker und Docker Compose installiert
- Azure OpenAI Credentials (siehe `.env`)

### Schnellstart

```bash
# 1. .env Datei konfigurieren
# Bearbeiten Sie .env und fügen Sie Ihre Azure OpenAI Credentials ein

# 2. Docker Compose starten
docker-compose up -d

# 3. Services prüfen
docker-compose ps

# 4. Interface öffnen (nach kurzer Startzeit)
# http://localhost:3000
# Admin-Interface: http://localhost:3000/admin
```

**Hinweis**: Das Projekt verwendet das offizielle Open WebUI Docker Image (`ghcr.io/open-webui/open-webui:main`) für optimale Performance und Stabilität.

## 📁 Projektstruktur

```
agentic-ai-process/
├── docker-compose.yml          # Docker Setup für Backend + Open WebUI
├── .env                        # Konfiguration (Azure OpenAI, etc.)
├── backend/                    # Eigenes FastAPI Backend
│   ├── main.py                # FastAPI Application
│   ├── requirements.txt       # Python Dependencies
│   ├── Dockerfile             # Backend Docker Image
│   └── README.md              # Backend-Dokumentation
├── src/                       # Open WebUI Frontend (SvelteKit)
│   └── routes/(app)/admin/    # Admin-Interface Route
├── Dockerfile                 # Open WebUI Docker Image
└── README.md                  # Diese Datei
```

## ⚙️ Konfiguration

### Environment Variables (.env)

**Backend:**
```bash
BACKEND_PORT=8000
AZURE_OPENAI_ENDPOINT=https://your-resource.openai.azure.com/
AZURE_OPENAI_API_KEY=your_api_key_here
AZURE_OPENAI_DEPLOYMENT_NAME=gpt-4
AZURE_OPENAI_API_VERSION=2024-02-15-preview
```

**Open WebUI:**
Die Open WebUI Konfiguration erfolgt über `docker-compose.yml`:
- `OPENAI_API_BASE_URL=http://planner-backend:8000/v1` - Verbindung zum eigenen Backend
- `OPENAI_API_KEY=dummy` - Nicht verwendet, da Azure OpenAI genutzt wird

## 🔌 Backend-Integration

### Backend API Endpoints

Das Backend läuft auf **Port 8000** und bietet folgende Endpoints:

- **Health Check**: `http://localhost:8000/health`
- **Chat Completions** (OpenAI-kompatibel): `http://localhost:8000/v1/chat/completions`
- **Models** (OpenAI-kompatibel): `http://localhost:8000/v1/models`
- **Planner Step**: `http://localhost:8000/api/v1/planner`
- **API Docs**: `http://localhost:8000/docs`

### Open WebUI → Backend Verbindung

Open WebUI ist konfiguriert, um das eigene Backend zu nutzen:
1. Open WebUI Frontend läuft auf Port 3000
2. Backend läuft auf Port 8000
3. Beide Services sind im Docker-Netzwerk `agentic-network`
4. Open WebUI sendet Requests an `http://planner-backend:8000/v1`

## 📝 Verwendung

### 1. Backend prüfen

```bash
curl http://localhost:8000/health
```

### 2. Open WebUI öffnen

- **Hauptinterface**: http://localhost:3000
- **Admin-Interface**: http://localhost:3000/admin

### 3. Chat testen

1. Öffnen Sie http://localhost:3000
2. Erstellen Sie einen neuen Chat
3. Das Backend wird automatisch für Chat-Completions genutzt

## 🛠️ Entwicklung

### Services stoppen
```bash
docker-compose down
```

### Logs anzeigen
```bash
# Alle Services
docker-compose logs -f

# Nur Backend
docker-compose logs -f planner-backend

# Nur Open WebUI
docker-compose logs -f open-webui
```

### Backend neu bauen
```bash
docker-compose up -d --build planner-backend
```

### Open WebUI neu bauen
```bash
docker-compose up -d --build open-webui
```

### Vollständiger Neustart
```bash
docker-compose down -v  # Löscht auch Volumes
docker-compose up -d --build
```

## 📚 Weitere Ressourcen

- [Open WebUI Dokumentation](https://docs.openwebui.com/)
- [Azure OpenAI Dokumentation](https://learn.microsoft.com/en-us/azure/ai-services/openai/)
- [FastAPI Dokumentation](https://fastapi.tiangolo.com/)

## 🔗 Admin-Interface

Das Open WebUI Admin-Interface ist verfügbar unter:
- **Hauptroute**: `/admin`
- **Analytics**: `/admin/analytics`
- **Settings**: `/admin/settings`
- **Users**: `/admin/users`
- **Functions**: `/admin/functions`
- **Evaluations**: `/admin/evaluations`

## ❓ Troubleshooting

### Backend startet nicht

```bash
# Logs prüfen
docker-compose logs planner-backend

# Azure Credentials prüfen
docker-compose exec planner-backend env | grep AZURE
```

### Open WebUI kann Backend nicht erreichen

```bash
# Netzwerk prüfen
docker network inspect agentic-ai-process_agentic-network

# Backend Health Check aus Open WebUI Container
docker-compose exec open-webui curl http://planner-backend:8000/health
```

### Model erscheint nicht in Open WebUI

1. Prüfen Sie `/v1/models` Endpoint:
   ```bash
   curl http://localhost:8000/v1/models
   ```

2. Stellen Sie sicher, dass `OPENAI_API_BASE_URL` korrekt gesetzt ist in `docker-compose.yml`
