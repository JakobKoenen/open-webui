# Frontend – Agentic AI Chat

Ein minimalistisches Chat-Interface, inspiriert von den Admin-Ansichten der [Open WebUI](https://github.com/open-webui/open-webui/tree/main/src/routes/(app)/admin), um den Agentic AI Planner schnell auszuprobieren.

## Features

- Dunkles UI mit Panel-Struktur und Gesundheitsanzeige
- Persistenter Gesprächsverlauf (localStorage)
- Shift+Enter für Zeilenumbrüche, Enter zum Senden
- Health Check gegen das FastAPI-Backend
- Anzeige von Backend-Metadaten (Endpoint & Modell)

## Entwicklung starten

```bash
# Pfad anpassen
cd /Users/jakobkoenen/Desktop/Ordnerstruktur/02\ Selbständigkeit\ \&\ Gewerbe/03\ Kunden/KOENEN\ BAUANWÄLTE/Projekte/Sovereign\ AI/agentic-ai-process/frontend

# Einfache Vorschau via Python HTTP Server
python3 -m http.server 3000

# Browser öffnen
open http://localhost:3000/index.html
```

> Alternativ: Mit VS Code Live Server oder jedem anderen statischen Webserver öffnen.

## Konfiguration

Standardmäßig kommuniziert das UI mit `http://localhost:8000`. Wenn das Backend auf einer anderen URL läuft, kannst du im Browser ein globales Objekt setzen:

```html
<script>
  window.APP_CONFIG = {
    API_BASE_URL: 'http://mein-backend:8000'
  };
</script>
```

Dieses Snippet muss vor dem Laden von `app.js` eingebunden werden.

## Deployment

Für Docker-Deployments kannst du einen schlanken Container bauen:

```bash
docker build -t agentic-ai-frontend .
docker run -it --rm -p 3000:80 agentic-ai-frontend
```

Der Browser ist dann unter `http://localhost:3000` erreichbar.

## Nächste Schritte

- Streaming-Responses unterstützen
- Authentifizierung für gesicherte Backends ergänzen
- Mehrere Sessions (Tabs) verwalten

