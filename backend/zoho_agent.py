import os
import re
import json
import time
import threading
from datetime import datetime
from dotenv import load_dotenv
from langchain_openai import ChatOpenAI
from langchain_anthropic import ChatAnthropic
from zoho_tools import lister_tickets_func, lire_ticket_func, repondre_ticket_func, get_valid_access_token

load_dotenv()

# ==========================================
# CONFIGURATION
# ==========================================
TICKET_FILE = "tickets_traites.txt"
DATA_FILE = "tickets_data.json"
INTERVALLE = 30
agent_running = False
agent_thread = None
stop_requested = False
tickets_traites_count = 0

# ==========================================
# MODÈLES IA
# ==========================================
openai_llm = ChatOpenAI(
    model="gpt-4o-mini",
    temperature=0.2,
    api_key=os.getenv("OPENAI_API_KEY")
)

anthropic_llm = ChatAnthropic(
    model="claude-haiku-4-5-20251001",
    max_tokens=300,
    api_key=os.getenv("ANTHROPIC_API_KEY")
)

# ==========================================
# GESTION DU FICHIER JSON
# ==========================================
def charger_donnees_json():
    if os.path.exists(DATA_FILE):
        try:
            with open(DATA_FILE, "r", encoding="utf-8") as f:
                return json.load(f)
        except:
            return {"tickets": [], "total_traites": 0}
    return {"tickets": [], "total_traites": 0}

def sauvegarder_donnees_json(donnees):
    with open(DATA_FILE, "w", encoding="utf-8") as f:
        json.dump(donnees, f, ensure_ascii=False, indent=2)

def ajouter_ticket_data(ticket_id: str, sujet: str, message_client: str, reponse_agent: str, analyse: dict):
    donnees = charger_donnees_json()
    nouveau_ticket = {
        "id": ticket_id,
        "sujet": sujet,
        "message_client": message_client,
        "reponse_agent": reponse_agent,
        "analyse": analyse,
        "date_traitement": datetime.now().isoformat()
    }
    donnees["tickets"].append(nouveau_ticket)
    donnees["total_traites"] = len(donnees["tickets"])
    sauvegarder_donnees_json(donnees)
    print(f" Données sauvegardées pour le ticket #{ticket_id}")

def get_tickets_data():
    return charger_donnees_json()

def get_total_traites():
    donnees = charger_donnees_json()
    return donnees.get("total_traites", 0)

# ==========================================
# FONCTIONS UTILITAIRES
# ==========================================
def nettoyer_texte(html_text: str) -> str:
    text = re.sub(r'<[^>]+>', ' ', html_text)
    text = re.sub(r'\s+', ' ', text).strip()
    return text

def charger_tickets_traites():
    if os.path.exists(TICKET_FILE):
        with open(TICKET_FILE, "r") as f:
            return set(line.strip() for line in f.readlines())
    return set()

def sauvegarder_ticket_traite(ticket_id):
    with open(TICKET_FILE, "a") as f:
        f.write(f"{ticket_id}\n")

# ==========================================
# ANALYSE INTELLIGENTE
# ==========================================
def analyser_ticket_intelligent(texte_ticket: str) -> dict:
    print(" Analyse du ticket...")
    texte_propre = nettoyer_texte(texte_ticket)
    
    system_prompt = """
    Analyse ce ticket support. Réponds UNIQUEMENT en JSON avec ces champs :
    {
        "categorie": "Facturation|Technique|Commercial|Autre",
        "sous_categorie": "Détail précis",
        "urgence": "Critique|Haute|Moyenne|Basse",
        "sentiment": "Très négatif|Négatif|Neutre|Positif",
        "resume": "Résumé en 5-8 mots",
        "action_requise": "Action claire à entreprendre"
    }
    """
    
    try:
        response = openai_llm.invoke([
            {"role": "system", "content": system_prompt},
            {"role": "user", "content": texte_propre[:1500]}
        ])
        contenu = response.content
        if "```json" in contenu:
            contenu = contenu.split("```json")[1].split("```")[0]
        elif "```" in contenu:
            contenu = contenu.split("```")[1].split("```")[0]
        return json.loads(contenu)
    except Exception as e:
        print(f" Erreur d'analyse : {e}")
        return {
            "categorie": "Autre",
            "sous_categorie": "À déterminer",
            "urgence": "Moyenne",
            "sentiment": "Neutre",
            "resume": texte_propre[:50] + "...",
            "action_requise": "Analyser et répondre"
        }

# ==========================================
# RÉDACTION CONCISE
# ==========================================
def rediger_reponse_concise(analyse: dict, ticket_original: str) -> str:
    print(" Rédaction de la réponse...")
    texte_propre = nettoyer_texte(ticket_original)
    
    prompt = f"""
    Rédige une réponse professionnelle et CONCISE (maximum 4 phrases) pour ce client.

    Contexte :
    - Catégorie : {analyse.get('categorie', 'Non spécifiée')}
    - Urgence : {analyse.get('urgence', 'Moyenne')}
    - Action : {analyse.get('action_requise', 'Non spécifiée')}

    Message client :
    {texte_propre[:300]}

    Règles :
    - 4 phrases maximum
    - Remercie, reconnais le problème, donne une action, conclue
    - Ton professionnel et rassurant
    """
    
    try:
        response = anthropic_llm.invoke([{"role": "user", "content": prompt}])
        return response.content
    except Exception as e:
        print(f" Erreur : {e}")
        return "Nous avons bien reçu votre demande. Notre équipe va l'examiner et revenir vers vous rapidement."

# ==========================================
# TRAITEMENT AUTONOME
# ==========================================
def traiter_ticket_autonome(ticket_id: str) -> dict:
    global tickets_traites_count
    
    print(f"\n{'='*60}")
    print(f" TRAITEMENT AUTONOME DU TICKET #{ticket_id}")
    print(f" {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    print('='*60)
    
    ticket_info = lire_ticket_func(ticket_id)
    
    sujet_match = re.search(r' Sujet : (.+?)(?=\n|$)', ticket_info)
    sujet = sujet_match.group(1).strip() if sujet_match else "Sans sujet"
    
    desc_match = re.search(r' Description : (.+?)(?=\n|$)', ticket_info, re.DOTALL)
    message_client = desc_match.group(1).strip() if desc_match else "Pas de description"
    
    print(f" Sujet : {sujet}")
    print(f" Message : {message_client[:100]}...")
    
    analyse = analyser_ticket_intelligent(ticket_info)
    print(f" {analyse.get('categorie', 'Inconnu')} |  {analyse.get('urgence', 'Inconnue')} |  {analyse.get('sentiment', 'Inconnu')}")
    
    reponse = rediger_reponse_concise(analyse, ticket_info)
    print(f" Réponse générée : {reponse[:100]}...")
    
    print(" Postage automatique...")
    resultat = repondre_ticket_func(ticket_id, reponse)
    print(f" {resultat}")
    
    ajouter_ticket_data(ticket_id, sujet, message_client, reponse, analyse)
    sauvegarder_ticket_traite(ticket_id)
    tickets_traites_count += 1
    
    return {
        "ticket_id": ticket_id,
        "sujet": sujet,
        "message_client": message_client,
        "analyse": analyse,
        "reponse": reponse,
        "resultat": resultat,
        "traite_a": datetime.now().isoformat()
    }

# ==========================================
# BOUCLE AUTONOME AVEC ARRÊT RAPIDE
# ==========================================
def boucle_autonome():
    global agent_running, tickets_traites_count, stop_requested
    
    print("="*60)
    print(" AGENT ZOHO AUTONOME - DÉMARRAGE")
    print("="*60)
    print(f" Vérification toutes les {INTERVALLE} secondes")
    print("="*60)
    
    tickets_traites = charger_tickets_traites()
    tickets_traites_count = len(tickets_traites)
    print(f" {tickets_traites_count} tickets déjà traités")
    
    # Boucle avec vérification rapide de l'arrêt
    while agent_running and not stop_requested:
        try:
            print(f"\n {datetime.now().strftime('%H:%M:%S')} - Recherche de nouveaux tickets...")
            
            resultat = lister_tickets_func(limit=10)
            ids_tickets = re.findall(r'#(\d+)', resultat)
            
            if ids_tickets:
                nouveaux_tickets = [id for id in ids_tickets if id not in tickets_traites]
                if nouveaux_tickets:
                    print(f" {len(nouveaux_tickets)} nouveaux tickets trouvés !")
                    for ticket_id in nouveaux_tickets:
                        if not agent_running or stop_requested:
                            print(" Arrêt demandé pendant le traitement")
                            return
                        try:
                            traiter_ticket_autonome(ticket_id)
                            tickets_traites.add(ticket_id)
                            tickets_traites_count += 1
                            print(f" Ticket #{ticket_id} traité avec succès")
                        except Exception as e:
                            print(f" Erreur sur #{ticket_id} : {e}")
                else:
                    print(" Aucun nouveau ticket")
            else:
                print(" Aucun ticket trouvé")
            
            # Attente avec vérification toutes les 2 secondes
            for _ in range(INTERVALLE // 2):
                if not agent_running or stop_requested:
                    print(" Arrêt demandé pendant l'attente")
                    return
                time.sleep(2)
            
        except Exception as e:
            print(f" Erreur dans la boucle : {e}")
            time.sleep(5)
    
    print(" Boucle autonome arrêtée")

# ==========================================
# DÉMARRAGE / ARRÊT RAPIDE
# ==========================================
def demarrer_agent():
    global agent_running, agent_thread, stop_requested, tickets_traites_count
    
    if agent_running:
        return {"status": "already_running", "message": "Agent déjà en cours"}
    
    # Réinitialiser les flags
    stop_requested = False
    agent_running = True
    
    # Démarrer le thread
    agent_thread = threading.Thread(target=boucle_autonome, daemon=True)
    agent_thread.start()
    
    return {"status": "started", "message": "Agent démarré"}

def arreter_agent():
    global agent_running, stop_requested, agent_thread
    
    if not agent_running:
        return {"status": "already_stopped", "message": "Agent déjà arrêté"}
    
    print(" Arrêt de l'agent en cours...")
    stop_requested = True
    agent_running = False
    
    # Attendre que le thread se termine (timeout plus court)
    if agent_thread and agent_thread.is_alive():
        agent_thread.join(timeout=2)
    
    print(" Agent arrêté")
    return {"status": "stopped", "message": "Agent arrêté"}

def get_status():
    global agent_running, tickets_traites_count
    return {
        "running": agent_running,
        "interval": INTERVALLE,
        "tickets_traites": tickets_traites_count
    }