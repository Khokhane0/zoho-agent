import os
import json
from dotenv import load_dotenv
from openai import OpenAI
from anthropic import Anthropic

# 1. Charger les clés
load_dotenv()
openai_client = OpenAI(api_key=os.getenv("OPENAI_API_KEY"))
anthropic_client = Anthropic(api_key=os.getenv("ANTHROPIC_API_KEY"))

# 2. La même fonction d'extraction qu'avant
SYSTEM_PROMPT = """
Tu es un expert en analyse de tickets support pour une PME.

À partir du texte du ticket client, tu dois extraire les informations suivantes au format JSON :

- "categorie" : "Facturation" | "Technique" | "Commercial" | "Autre"
- "urgence" : "Haute" | "Moyenne" | "Basse"
- "sentiment" : "Positif" | "Neutre" | "Négatif"
- "resume" : résumé en moins de 10 mots
- "client_fidele" : true/false (si le client mentionne une ancienneté)
- "action_requise" : résumé de ce qu'il faut faire

Réponds UNIQUEMENT avec le JSON, sans autre texte.
"""

def extraire_ticket(texte_ticket):
    response = openai_client.chat.completions.create(
        model="gpt-4o-mini",
        messages=[
            {"role": "system", "content": SYSTEM_PROMPT},
            {"role": "user", "content": texte_ticket}
        ],
        temperature=0.2,
        response_format={"type": "json_object"}
    )
    return json.loads(response.choices[0].message.content)

# 3. NOUVEAU : Le rédacteur avec Anthropic
def rediger_reponse(analyse):
    """
    Prend le JSON d'analyse et rédige une réponse professionnelle avec Anthropic.
    """
    # Construire un prompt à partir de l'analyse
    prompt_redaction = f"""
    Tu es un expert en service client pour une PME.

    Un client a envoyé un ticket avec les caractéristiques suivantes :
    - Catégorie : {analyse['categorie']}
    - Urgence : {analyse['urgence']}
    - Sentiment : {analyse['sentiment']}
    - Résumé : {analyse['resume']}
    - Client fidèle : {'Oui' if analyse['client_fidele'] else 'Non'}
    - Action requise : {analyse['action_requise']}

    Rédige une réponse professionnelle, empathique et concise (5-7 phrases maximum).
    La réponse doit :
    1. Remercier le client
    2. Reconnaître le problème (si le client est fidèle, souligne-le)
    3. Annoncer l'action qui va être prise
    4. Donner un délai estimé
    5. Terminer par une formule de politesse

    Réponds UNIQUEMENT avec le texte de la réponse, sans préambule.
    """

    response = anthropic_client.messages.create(
        model="claude-haiku-4-5-20251001",  # Ton modèle qui fonctionne
        max_tokens=300,
        messages=[
            {"role": "user", "content": prompt_redaction}
        ]
    )
    
    return response.content[0].text

# 4. Le programme principal : Extraction + Rédaction
if __name__ == "__main__":
    # Ticket d'exemple
    ticket_test = """
    Bonjour, je suis client chez vous depuis 3 ans. 
    Ma facture du mois dernier est inexacte, vous m'avez facturé 150€ au lieu de 120€.
    Pouvez-vous corriger ça rapidement ? C'est urgent, mon comptable attend.
    """
    
    print("="*60)
    print(" TICKET ORIGINAL")
    print("="*60)
    print(ticket_test)
    
    print("\n" + "="*60)
    print(" ÉTAPE 1 : EXTRACTION (OpenAI)")
    print("="*60)
    analyse = extraire_ticket(ticket_test)
    print(json.dumps(analyse, indent=2, ensure_ascii=False))
    
    print("\n" + "="*60)
    print(" ÉTAPE 2 : RÉDACTION (Anthropic)")
    print("="*60)
    reponse = rediger_reponse(analyse)
    print(reponse)
    
    print("\n" + "="*60)
    print(" AGENT TERMINÉ")
    print("="*60)
    
    input("\nAppuie sur Entrée pour quitter...")