import os
import json
from dotenv import load_dotenv
from langchain_openai import ChatOpenAI
from langchain_anthropic import ChatAnthropic
from langchain.agents import create_agent
from langchain.tools import tool
from langchain_core.messages import HumanMessage, SystemMessage

load_dotenv()

# 2. Initialiser les modèles
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

# 3. Définir les outils avec le décorateur @tool
@tool
def extraire_ticket(texte_ticket: str) -> str:
    """Extrait les informations d'un ticket client et retourne un JSON structuré"""
    print(" L'agent appelle l'outil 'extraction'...")
    
    system_prompt = """
    Extrais les informations du ticket au format JSON :
    - categorie : "Facturation" | "Technique" | "Commercial" | "Autre"
    - urgence : "Haute" | "Moyenne" | "Basse"
    - sentiment : "Positif" | "Neutre" | "Négatif"
    - resume : résumé en moins de 10 mots
    - client_fidele : true/false
    - action_requise : résumé de l'action
    
    Réponds UNIQUEMENT avec le JSON.
    """
    
    try:
        response = openai_llm.invoke([
            {"role": "system", "content": system_prompt},
            {"role": "user", "content": texte_ticket}
        ])
        
        resultat = json.loads(response.content)
        print(f" Extraction réussie : {resultat.get('categorie', 'Inconnu')}")
        return json.dumps(resultat, ensure_ascii=False)
    except Exception as e:
        print(f" Erreur d'extraction : {e}")
        return json.dumps({
            "categorie": "Inconnu",
            "urgence": "Moyenne",
            "sentiment": "Neutre",
            "resume": "Erreur d'extraction",
            "client_fidele": False,
            "action_requise": "À déterminer"
        })

@tool
def rediger_reponse(analyse_json: str) -> str:
    """Rédige une réponse professionnelle à partir d'un JSON d'analyse"""
    print(" L'agent appelle l'outil 'rédaction'...")
    
    try:
        analyse = json.loads(analyse_json)
    except:
        analyse = {"categorie": "Inconnu", "urgence": "Moyenne", "sentiment": "Neutre", "action_requise": "À déterminer"}
    
    prompt = f"""
    Rédige une réponse professionnelle pour un ticket client avec ces caractéristiques :
    - Catégorie : {analyse.get('categorie', 'Inconnue')}
    - Urgence : {analyse.get('urgence', 'Moyenne')}
    - Sentiment : {analyse.get('sentiment', 'Neutre')}
    - Action requise : {analyse.get('action_requise', 'À déterminer')}
    
    La réponse doit :
    1. Être empathique et professionnelle
    2. Reconnaître le problème
    3. Expliquer l'action qui va être prise
    4. Donner un délai
    5. Terminer par une formule de politesse
    
    Maximum 5-7 phrases.
    """
    
    response = anthropic_llm.invoke([{"role": "user", "content": prompt}])
    print(" Rédaction terminée")
    return response.content

# 4. Créer l'agent avec la nouvelle API
tools = [extraire_ticket, rediger_reponse]

# Créer l'agent avec un système prompt
agent = create_agent(
    model=openai_llm,
    tools=tools,
    system_prompt="""Tu es un agent autonome spécialisé dans le traitement des tickets clients.
    
    Règle importante : Pour traiter un ticket, tu dois :
    1. D'abord, utiliser extraire_ticket pour analyser le ticket
    2. Ensuite, utiliser rediger_reponse pour générer une réponse
    3. Terminer en présentant le résultat final
    
    Si tu as besoin d'information supplémentaire, n'hésite pas à demander.
    """
)

# 5. Lancer l'agent
if __name__ == "__main__":
    ticket_test = """
    Bonjour, je suis client chez vous depuis 3 ans. 
    Ma facture du mois dernier est inexacte, vous m'avez facturé 150€ au lieu de 120€.
    Pouvez-vous corriger ça rapidement ? C'est urgent, mon comptable attend.
    """
    
    print("="*60)
    print(" AGENT AUTONOME - TRAITEMENT DE TICKET")
    print("="*60)
    print("\n Ticket reçu :")
    print(ticket_test)
    print("\n" + "="*60)
    
    try:
        # La nouvelle API utilise 'invoke' avec des messages
        resultat = agent.invoke({
            "messages": [
                HumanMessage(content=f"Traite ce ticket client : {ticket_test}")
            ]
        })
        
        print("\n" + "="*60)
        print(" RÉSULTAT FINAL")
        print("="*60)
        
        # Récupérer le dernier message de l'agent
        dernier_message = resultat["messages"][-1]
        print(dernier_message.content)
        
    except Exception as e:
        print(f" L'agent a rencontré une erreur : {e}")
        import traceback
        traceback.print_exc()
    
    input("\nAppuie sur Entrée pour quitter...")