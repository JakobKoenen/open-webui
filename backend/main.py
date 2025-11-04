"""
Agentic AI Backend - Planner Agent
FastAPI Backend für Azure OpenAI Integration
"""

from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel, Field
from typing import Optional, List
import os
import openai
from dotenv import load_dotenv
import httpx

# Environment variables laden
load_dotenv()

app = FastAPI(
    title="Agentic AI Planner",
    description="Backend für Agentic AI Planner Step mit Azure OpenAI",
    version="1.0.0"
)

# CORS Middleware für Open WebUI Integration
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # In Produktion einschränken
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Azure OpenAI Konfiguration
AZURE_OPENAI_ENDPOINT = os.getenv("AZURE_OPENAI_ENDPOINT")
AZURE_OPENAI_API_KEY = os.getenv("AZURE_OPENAI_API_KEY")
AZURE_OPENAI_DEPLOYMENT_NAME = os.getenv("AZURE_OPENAI_DEPLOYMENT_NAME", "gpt-4")
AZURE_OPENAI_API_VERSION = os.getenv("AZURE_OPENAI_API_VERSION", "2024-02-15-preview")

# OpenAI Client mit Azure Konfiguration
if AZURE_OPENAI_ENDPOINT and AZURE_OPENAI_API_KEY:
    client = openai.AzureOpenAI(
        api_key=AZURE_OPENAI_API_KEY,
        api_version=AZURE_OPENAI_API_VERSION,
        azure_endpoint=AZURE_OPENAI_ENDPOINT
    )
else:
    client = None


# Request Models
class ChatMessage(BaseModel):
    role: str = Field(description="Role: user, assistant, or system")
    content: str = Field(description="Message content")


class PlannerRequest(BaseModel):
    message: str = Field(description="User input message")
    conversation_history: Optional[List[ChatMessage]] = Field(
        default=[], 
        description="Previous conversation messages"
    )


class PlannerResponse(BaseModel):
    result: str = Field(description="Planner step result")
    status: str = Field(description="Processing status")


# Request/Response Models für API Calls
class APICallRequest(BaseModel):
    """Request für API Call"""
    url: str = Field(description="URL der API")
    method: str = Field(default="GET", description="HTTP Method (GET, POST, PUT, DELETE)")
    headers: Optional[dict] = Field(default=None, description="HTTP Headers")
    body: Optional[dict] = Field(default=None, description="Request Body (für POST/PUT)")


class APICallResponse(BaseModel):
    """Response für API Call"""
    status_code: int = Field(description="HTTP Status Code")
    response_data: dict = Field(description="Response Daten")
    success: bool = Field(description="Ob der Call erfolgreich war")


# System Prompt für Agentic AI Planner
PLANNER_SYSTEM_PROMPT = """
# Rolle
Du bist der Planner Agent im Sovereign-AI-System.
Deine Aufgabe ist es, eine komplexe juristische Nutzeranfrage in strukturierte Teilschritte zu zerlegen und zu bestimmen, welche Vektor-Datenbanken und welche spezialisierten Agents dafür aktiviert werden sollen.
Deine Planung ist der erste Schritt einer mehrstufigen AI-Pipeline (Planner → Retriever → Researcher → Validator → Summarizer).

# Tools
Dir stehen folgende Tools zur Verfügung:
- Vektor-Datenbanken (Retrieval):


# Guardrails
	•	Führe keine eigene inhaltliche Auslegung durch, plane nur die Schritte.
	•	Wähle nur relevante Datenbanken, um Kosten zu optimieren.
	•	Jeder Step muss klar begründet und benannt werden.
	•	Wenn die Anfrage mehrdeutig ist, plane Rückfragen („clarification needed“).
	•	Gib ausschließlich validen JSON-Output aus. Keine zusätzliche Erklärung, kein Markdown.
 
 - Bei Fragen, die allgemein Formuliert sind und sowohl in einen Baurechtlichen Kontext als auch einen nicht-baurechtlichen Kontext passen, setze inbound auf true und formuliere den Prompt so, dass er für das Baurecht gilt.

# Output Format (PFLICHT)

{
    "meta":{
        "domain": "string (z. B. 'Baurecht', 'Vertragsrecht', 'Architektenhonorar')",
         "inbound":"boolean (Ist diese Frage innerhalb des Themengebiets des Agents? Ja/Nein)",
    "inbound_reason":"string (Begründung für inbound)",
    
    }
   
    
    "prompt": "string (Nutzeranfrage in zusammengefasster Form)",
   
    "steps":[
        {
            "step": "string",
            "description": "string"
        },
        {
            "step": "string",
            "description": "string"
        }
    ]
    
    "tools": [
        {
            "tool": "string (welches Tool soll benutzt werden)",
            "search_query": "string (Welche Suchanfrage soll für das Tool benutzt werden)",
        },
        {
            "tool": "string (welches Tool soll benutzt werden)",
            "search_query": "string (Welche Suchanfrage soll für das Tool benutzt werden)",
        }
    ]
    
    "agent":"string (welcher Agent soll benutzt werden)"
}

"""


@app.get("/health")
async def health_check():
    """Health Check Endpoint"""
    if not client:
        return {
            "status": "error",
            "message": "Azure OpenAI not configured",
            "configured": False
        }
    return {
        "status": "healthy",
        "configured": True,
        "model": AZURE_OPENAI_DEPLOYMENT_NAME
    }


@app.post("/api/v1/planner", response_model=PlannerResponse)
async def planner_step(request: PlannerRequest):
    """
    Agentic AI Planner Step
    
    Verarbeitet Benutzeranfragen und erstellt strukturierte Pläne
    """
    if not client:
        raise HTTPException(
            status_code=500,
            detail="Azure OpenAI not configured. Please check environment variables."
        )
    
    try:
        # Konversationsverlauf aufbauen
        messages = []
        
        # System Prompt hinzufügen
        messages.append({
            "role": "system",
            "content": PLANNER_SYSTEM_PROMPT
        })
        
        # Konversationsverlauf hinzufügen
        for msg in request.conversation_history:
            messages.append({
                "role": msg.role,
                "content": msg.content
            })
        
        # Aktuelle Benutzernachricht hinzufügen
        messages.append({
            "role": "user",
            "content": request.message
        })
        
        # Azure OpenAI API aufrufen
        response = client.chat.completions.create(
            model=AZURE_OPENAI_DEPLOYMENT_NAME,
            messages=messages,
            temperature=0.7,
            max_tokens=2000
        )
        
        # Antwort extrahieren
        result = response.choices[0].message.content
        
        return PlannerResponse(
            result=result,
            status="success"
        )
        
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"Error processing request: {str(e)}"
        )


@app.post("/api/v1/chat")
async def chat_endpoint(request: PlannerRequest):
    """
    Chat Endpoint - Redirect zu Planner Step
    Für einfache Chat-Integration
    """
    return await planner_step(request)


@app.post("/api/v1/api-call", response_model=APICallResponse)
async def api_call(request: APICallRequest):
    """
    Allgemeiner API Call Endpoint
    
    Führt einen HTTP Request zu einer externen API aus.
    
    Beispiel Request:
    {
        "url": "https://api.example.com/data",
        "method": "GET",
        "headers": {
            "Authorization": "Bearer token123"
        }
    }
    """
    async with httpx.AsyncClient() as client:
        try:
            # HTTP Request basierend auf Method
            if request.method.upper() == "GET":
                response = await client.get(
                    request.url,
                    headers=request.headers or {}
                )
            elif request.method.upper() == "POST":
                response = await client.post(
                    request.url,
                    headers=request.headers or {},
                    json=request.body
                )
            elif request.method.upper() == "PUT":
                response = await client.put(
                    request.url,
                    headers=request.headers or {},
                    json=request.body
                )
            elif request.method.upper() == "DELETE":
                response = await client.delete(
                    request.url,
                    headers=request.headers or {}
                )
            else:
                raise HTTPException(
                    status_code=400,
                    detail=f"Unsupported HTTP method: {request.method}"
                )
            
            # Response verarbeiten
            try:
                response_data = response.json()
            except:
                response_data = {"text": response.text}
            
            return APICallResponse(
                status_code=response.status_code,
                response_data=response_data,
                success=200 <= response.status_code < 300
            )
            
        except httpx.RequestError as e:
            raise HTTPException(
                status_code=500,
                detail=f"Request error: {str(e)}"
            )
        except Exception as e:
            raise HTTPException(
                status_code=500,
                detail=f"Error making API call: {str(e)}"
            )


# OpenAI-kompatibler Endpoint für Open WebUI
class OpenAIMessage(BaseModel):
    role: str
    content: str


class OpenAIRequest(BaseModel):
    model: str
    messages: List[OpenAIMessage]
    temperature: Optional[float] = 0.7
    max_tokens: Optional[int] = 2000
    stream: Optional[bool] = False


@app.post("/v1/chat/completions")
async def openai_chat_completions(request: OpenAIRequest):
    """
    OpenAI-kompatibler Chat Completions Endpoint
    Für Open WebUI Integration
    """
    if not client:
        raise HTTPException(
            status_code=500,
            detail="Azure OpenAI not configured. Please check environment variables."
        )
    
    try:
        # Messages vorbereiten mit System Prompt
        messages = []
        
        # Prüfen ob bereits ein System Prompt vorhanden ist
        has_system = any(msg.role == "system" for msg in request.messages)
        
        # System Prompt hinzufügen falls nicht vorhanden
        if not has_system:
            messages.append({
                "role": "system",
                "content": PLANNER_SYSTEM_PROMPT
            })
        
        # Alle Messages hinzufügen
        for msg in request.messages:
            messages.append({
                "role": msg.role,
                "content": msg.content
            })
        
        # Azure OpenAI API aufrufen
        response = client.chat.completions.create(
            model=AZURE_OPENAI_DEPLOYMENT_NAME,
            messages=messages,
            temperature=request.temperature,
            max_tokens=request.max_tokens
        )
        
        # OpenAI-kompatible Response
        return {
            "id": f"chatcmpl-{response.id}",
            "object": "chat.completion",
            "created": response.created,
            "model": AZURE_OPENAI_DEPLOYMENT_NAME,
            "choices": [
                {
                    "index": 0,
                    "message": {
                        "role": response.choices[0].message.role,
                        "content": response.choices[0].message.content
                    },
                    "finish_reason": response.choices[0].finish_reason
                }
            ],
            "usage": {
                "prompt_tokens": response.usage.prompt_tokens,
                "completion_tokens": response.usage.completion_tokens,
                "total_tokens": response.usage.total_tokens
            }
        }
        
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"Error processing request: {str(e)}"
        )


@app.get("/v1/models")
async def list_models():
    """
    OpenAI-kompatibler Models Endpoint
    Listet verfügbare Modelle für Open WebUI
    """
    if not client:
        return {
            "object": "list",
            "data": []
        }
    
    # Modell-Name aus Environment Variable
    model_name = AZURE_OPENAI_DEPLOYMENT_NAME
    
    return {
        "object": "list",
        "data": [
            {
                "id": model_name,
                "object": "model",
                "created": 1677610602,
                "owned_by": "agentic-ai-planner",
                "permission": [],
                "root": model_name,
                "parent": None
            }
        ]
    }


@app.get("/")
async def root():
    """Root Endpoint mit API Informationen"""
    return {
        "name": "Agentic AI Planner Backend",
        "version": "1.0.0",
        "endpoints": {
            "health": "/health",
            "planner": "/api/v1/planner",
            "chat": "/api/v1/chat",
            "api_call": "/api/v1/api-call",
            "openai_compatible": "/v1/chat/completions",
            "models": "/v1/models"
        },
        "configured": client is not None
    }


if __name__ == "__main__":
    import uvicorn
    port = int(os.getenv("BACKEND_PORT", "8000"))
    uvicorn.run(app, host="0.0.0.0", port=port)

