# zoho_tools.py
import os
import json
import requests
from dotenv import load_dotenv
from langchain.tools import tool

load_dotenv()

# ==========================================
# CONFIGURATION ZOHO
# ==========================================
ZOHO_CLIENT_ID = os.getenv("ZOHO_CLIENT_ID")
ZOHO_CLIENT_SECRET = os.getenv("ZOHO_CLIENT_SECRET")
ZOHO_REFRESH_TOKEN = os.getenv("ZOHO_REFRESH_TOKEN")
ZOHO_ACCESS_TOKEN = os.getenv("ZOHO_ACCESS_TOKEN")
ZOHO_BASE_URL = "https://desk.zohocloud.ca/api/v1"
ZOHO_AUTH_URL = "https://accounts.zohocloud.ca/oauth/v2/token"

# Fichier pour sauvegarder le nouveau token
TOKEN_FILE = "access_token.txt"

# ==========================================
# FONCTION POUR RAFRAÎCHIR LE TOKEN
# ==========================================
def get_valid_access_token():
    """
    Récupère un Access Token valide.
    - Utilise le token existant s'il est valide
    - Sinon, utilise le Refresh Token pour en obtenir un nouveau
    """
    global ZOHO_ACCESS_TOKEN
    
    # Vérifier si le token actuel est valide en faisant un test
    test_url = f"{ZOHO_BASE_URL}/tickets?limit=1"
    headers = {"Authorization": f"Zoho-oauthtoken {ZOHO_ACCESS_TOKEN}"}
    
    try:
        response = requests.get(test_url, headers=headers)
        if response.status_code == 200:
            # Le token est valide
            return ZOHO_ACCESS_TOKEN
    except:
        pass
    
    # Le token est invalide, on le rafraîchit
    print(" Rafraîchissement du token...")
    
    data = {
        "refresh_token": ZOHO_REFRESH_TOKEN,
        "client_id": ZOHO_CLIENT_ID,
        "client_secret": ZOHO_CLIENT_SECRET,
        "grant_type": "refresh_token"
    }
    
    try:
        response = requests.post(ZOHO_AUTH_URL, data=data)
        tokens = response.json()
        
        if "access_token" in tokens:
            ZOHO_ACCESS_TOKEN = tokens["access_token"]
            
            # Mettre à jour la variable d'environnement
            os.environ["ZOHO_ACCESS_TOKEN"] = ZOHO_ACCESS_TOKEN
            
            # Sauvegarder dans .env
            with open(".env", "r") as f:
                lines = f.readlines()
            
            with open(".env", "w") as f:
                for line in lines:
                    if line.startswith("ZOHO_ACCESS_TOKEN="):
                        f.write(f"ZOHO_ACCESS_TOKEN={ZOHO_ACCESS_TOKEN}\n")
                    else:
                        f.write(line)
            
            print(" Token rafraîchi avec succès !")
            return ZOHO_ACCESS_TOKEN
        else:
            print(f" Erreur lors du rafraîchissement : {tokens}")
            return None
    except Exception as e:
        print(f" Erreur de connexion : {e}")
        return None

# ==========================================
# FONCTIONS ZOHO AVEC RAFRAÎCHISSEMENT AUTO
# ==========================================

def get_headers():
    """Retourne les headers avec un token valide."""
    token = get_valid_access_token()
    if token:
        return {"Authorization": f"Zoho-oauthtoken {token}"}
    else:
        return None

def lister_tickets_func(limit: int = 5) -> str:
    """Liste les tickets récents de Zoho Desk."""
    print(f" Récupération des {limit} derniers tickets...")
    
    headers = get_headers()
    if not headers:
        return " Impossible d'obtenir un token valide."
    
    url = f"{ZOHO_BASE_URL}/tickets?limit={limit}"
    
    try:
        response = requests.get(url, headers=headers)
        data = response.json()
        
        if response.status_code == 200:
            tickets = data.get("data", [])
            if not tickets:
                return " Aucun ticket trouvé."
            
            resultat = f" {len(tickets)} derniers tickets :\n"
            for ticket in tickets:
                subject = ticket.get('subject', 'Sans sujet')
                status = ticket.get('status', 'N/A')
                ticket_id = ticket.get('id', 'N/A')
                created_time = ticket.get('createdTime', 'N/A')
                resultat += f"  - #{ticket_id} : {subject} ({status}) - {created_time[:10] if created_time else 'N/A'}\n"
            return resultat
        else:
            return f" Erreur {response.status_code} : {data.get('message', 'Inconnue')}"
    
    except Exception as e:
        return f" Erreur de connexion : {e}"

def lire_ticket_func(ticket_id: str) -> str:
    """Lit un ticket spécifique depuis Zoho Desk."""
    print(f" Lecture du ticket #{ticket_id}...")
    
    headers = get_headers()
    if not headers:
        return " Impossible d'obtenir un token valide."
    
    url = f"{ZOHO_BASE_URL}/tickets/{ticket_id}"
    
    try:
        response = requests.get(url, headers=headers)
        ticket = response.json()
        
        if response.status_code == 200:
            return f"""
 Ticket #{ticket['id']}
 Sujet : {ticket.get('subject', 'Sans sujet')}
 Description : {ticket.get('description', 'Pas de description')}
 Statut : {ticket.get('status', 'Inconnu')}
 Priorité : {ticket.get('priority', 'Moyenne')}
 Client : {ticket.get('contact', {}).get('name', 'Inconnu')}
 Créé le : {ticket.get('createdTime', 'N/A')}
"""
        else:
            return f" Erreur {response.status_code} : {ticket.get('message', 'Inconnue')}"
    
    except Exception as e:
        return f" Erreur de connexion : {e}"

def repondre_ticket_func(ticket_id: str, reponse: str) -> str:
    """Poste une réponse publique sur un ticket Zoho Desk."""
    print(f" Envoi de la réponse au ticket #{ticket_id}...")
    
    headers = get_headers()
    if not headers:
        return " Impossible d'obtenir un token valide."
    
    headers["Content-Type"] = "application/json"
    
    # URLs possibles pour les réponses
    urls = [
        f"{ZOHO_BASE_URL}/tickets/{ticket_id}/messages",
        f"{ZOHO_BASE_URL}/tickets/{ticket_id}/replies",
        f"{ZOHO_BASE_URL}/tickets/{ticket_id}/comments",
        f"{ZOHO_BASE_URL}/tickets/{ticket_id}/notes",
    ]
    
    data = {
        "content": reponse,
        "isPublic": True
    }
    
    for url in urls:
        try:
            response = requests.post(url, headers=headers, json=data)
            if response.status_code in [200, 201]:
                return f" Réponse postée sur le ticket #{ticket_id}"
            elif response.status_code == 404:
                continue
            else:
                error = response.json()
                return f" Erreur {response.status_code} : {error.get('message', 'Inconnue')}"
        except:
            continue
    
    return " Aucune URL de réponse n'a fonctionné."

# ==========================================
# EXPORTER LES FONCTIONS AVEC @tool
# ==========================================

lister_tickets = tool(lister_tickets_func)
lire_ticket = tool(lire_ticket_func)
repondre_ticket = tool(repondre_ticket_func)

# ==========================================
# TEST
# ==========================================
if __name__ == "__main__":
    print(" Test des outils Zoho Desk (avec rafraîchissement auto)")
    print("=" * 40)
    
    print("\n1. Liste des tickets :")
    print(lister_tickets_func())
    
    input("\nAppuie sur Entrée pour quitter...")