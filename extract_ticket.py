import os
import json
from dotenv import load_dotenv
from openai import OpenAI

# 1. Charger les clés
load_dotenv()
client = OpenAI(api_key=os.getenv("OPENAI_API_KEY"))

# 2. Définir le prompt
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

# 3. La fonction principale
def extraire_ticket(texte_ticket):
    """
    Prend un ticket en texte brut et retourne un JSON structuré.
    """
    try:
        response = client.chat.completions.create(
            model="gpt-4o-mini",
            messages=[
                {"role": "system", "content": SYSTEM_PROMPT},
                {"role": "user", "content": texte_ticket}
            ],
            temperature=0.2,
            response_format={"type": "json_object"}
        )
        
        resultat_json = response.choices[0].message.content
        return json.loads(resultat_json)
    
    except Exception as e:
        print(f" Erreur lors de l'extraction : {e}")
        return None

# 4. Tester avec un exemple
if __name__ == "__main__":
    # Ticket fictif
    ticket_test = """
    Bonjour, je suis client chez vous depuis 3 ans. 
    Ma facture du mois dernier est inexacte, vous m'avez facturé 150€ au lieu de 120€.
    Pouvez-vous corriger ça rapidement ? C'est urgent, mon comptable attend.
    """
    
    print(" Ticket original :")
    print(ticket_test)
    print("\n" + "="*50 + "\n")
    
    resultat = extraire_ticket(ticket_test)
    
    if resultat:
        print(" Extraction réussie !")
        print(json.dumps(resultat, indent=2, ensure_ascii=False))
    else:
        print(" L'extraction a échoué.")
    
    # Pour garder la console ouverte sur Windows
    input("\nAppuie sur Entrée pour quitter...")