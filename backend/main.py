from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from typing import List, Optional
import uvicorn
import re
import requests
import json
from zoho_tools import (
    lister_tickets_func, 
    lire_ticket_func, 
    repondre_ticket_func, 
    get_valid_access_token,
    get_headers,
    ZOHO_BASE_URL
)
from zoho_agent import (
    traiter_ticket_autonome, 
    charger_tickets_traites,
    get_tickets_data,
    get_total_traites,
    demarrer_agent,
    arreter_agent,
    get_status
)

app = FastAPI(title="Zoho Agent API", version="2.0.0")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# ==========================================
# MODÈLES
# ==========================================
class Ticket(BaseModel):
    id: str
    subject: str
    status: str
    date: Optional[str] = None
    description: Optional[str] = None

class TicketReply(BaseModel):
    content: str

# ==========================================
# ROUTES
# ==========================================
@app.get("/")
async def root():
    return {"message": "Zoho Agent API", "status": "online", "version": "2.0.0"}

@app.get("/api/tickets", response_model=List[Ticket])
async def get_tickets(limit: int = 50):
    """Récupère les tickets avec leur description complète"""
    try:
        # 1. Récupérer la liste des tickets
        headers = get_headers()
        if not headers:
            raise HTTPException(status_code=401, detail="Token invalide")
        
        url = f"https://desk.zohocloud.ca/api/v1/tickets?limit={limit}"
        response = requests.get(url, headers=headers)
        
        if response.status_code != 200:
            raise HTTPException(status_code=response.status_code, detail="Erreur Zoho API")
        
        data = response.json()
        tickets = []
        
        # 2. Pour chaque ticket, récupérer les détails complets
        for ticket_data in data.get("data", []):
            ticket_id = str(ticket_data.get('id', 'N/A'))
            
            # Récupérer la description depuis l'API Zoho
            description = "Aucune description disponible"
            try:
                # Appel direct à l'API pour avoir la description complète
                detail_url = f"https://desk.zohocloud.ca/api/v1/tickets/{ticket_id}"
                detail_response = requests.get(detail_url, headers=headers)
                
                if detail_response.status_code == 200:
                    detail_data = detail_response.json()
                    description = detail_data.get('description', 'Aucune description disponible')
                    
                    # Nettoyer le HTML si présent
                    if description and '<' in description:
                        import re
                        description = re.sub(r'<[^>]+>', ' ', description)
                        description = re.sub(r'\s+', ' ', description).strip()
                        if not description:
                            description = "Aucune description disponible"
                else:
                    # Fallback : utiliser la description de la liste
                    description = ticket_data.get('description', 'Aucune description disponible')
            except Exception as e:
                print(f"Erreur récupération description #{ticket_id}: {e}")
                description = ticket_data.get('description', 'Aucune description disponible')
            
            tickets.append(Ticket(
                id=ticket_id,
                subject=ticket_data.get('subject', 'Sans sujet'),
                status=ticket_data.get('status', 'Inconnu'),
                date=ticket_data.get('createdTime', '')[:10] if ticket_data.get('createdTime') else '',
                description=description
            ))
        
        return tickets
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/api/tickets-raw")
async def get_tickets_raw(limit: int = 10):
    """Version brute pour diagnostic - montre ce que renvoie l'API Zoho"""
    try:
        headers = get_headers()
        if not headers:
            return {"error": "Token invalide"}
        
        url = f"https://desk.zohocloud.ca/api/v1/tickets?limit={limit}"
        response = requests.get(url, headers=headers)
        
        return {
            "status": response.status_code,
            "data": response.json() if response.status_code == 200 else response.text
        }
    except Exception as e:
        return {"error": str(e)}

@app.get("/api/ticket-detail/{ticket_id}")
async def get_ticket_detail(ticket_id: str):
    """Récupère les détails complets d'un ticket"""
    try:
        return {"id": ticket_id, "content": lire_ticket_func(ticket_id)}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.post("/api/tickets/{ticket_id}/process")
async def process_ticket(ticket_id: str):
    try:
        resultat = traiter_ticket_autonome(ticket_id)
        return resultat
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.post("/api/tickets/{ticket_id}/reply")
async def reply_ticket(ticket_id: str, reply: TicketReply):
    try:
        resultat = repondre_ticket_func(ticket_id, reply.content)
        return {"status": "success", "result": resultat}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/api/stats")
async def get_stats():
    try:
        tickets_traites = charger_tickets_traites()
        data = get_tickets_data()
        print(f" Stats - tickets_traites: {tickets_traites}")  # Debug
        return {
            "total_traites": len(tickets_traites),
            "processed_ids": list(tickets_traites),
            "dernier_traite": list(tickets_traites)[-1] if tickets_traites else None,
            "tickets_data": data.get("tickets", [])
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/api/agent/status")
async def get_agent_status():
    return get_status()

@app.post("/api/agent/start")
async def start_agent():
    return demarrer_agent()

@app.post("/api/agent/stop")
async def stop_agent():
    return arreter_agent()

@app.get("/api/data")
async def get_data():
    return get_tickets_data()

@app.get("/api/test-ticket/{ticket_id}")
async def test_ticket(ticket_id: str):
    """Test pour voir ce que renvoie Zoho"""
    try:
        headers = get_headers()
        if not headers:
            return {"error": "Token invalide"}
        
        url = f"https://desk.zohocloud.ca/api/v1/tickets/{ticket_id}"
        response = requests.get(url, headers=headers)
        
        return {
            "status": response.status_code,
            "data": response.json() if response.status_code == 200 else response.text
        }
    except Exception as e:
        return {"error": str(e)}

if __name__ == "__main__":
    uvicorn.run(app, host="0.0.0.0", port=8000)