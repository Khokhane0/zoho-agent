import requests
import json
import os
from dotenv import load_dotenv

load_dotenv()

# ==========================================
# 1. TES INFORMATIONS (à remplir une fois)
# ==========================================
CLIENT_ID = "1000.3XR22GHLJE89IALQTPNNMNRKL11Y2R"
CLIENT_SECRET = "9fb691b4a858e24a954c8ec55ae4e53265046be7f7"  # SECRET COMPLET
REDIRECT_URI = "https://www.zohocloud.ca"
REFRESH_TOKEN_FILE = "refresh_token.txt"  # Fichier pour sauvegarder le token

# ==========================================
# 2. DOMAINE ZOHO CANADA
# ==========================================
ZOHO_AUTH_URL = "https://accounts.zohocloud.ca/oauth/v2/token"
ZOHO_DESK_URL = "https://desk.zohocloud.ca/api/v1"

# ==========================================
# 3. FONCTION POUR OBTENIR UN ACCESS TOKEN
# ==========================================
def get_access_token(refresh_token=None):
    """
    Obtient un Access Token.
    - Si refresh_token est fourni, l'utilise directement.
    - Sinon, demande un code à l'utilisateur.
    """
    
    # Si on a un Refresh Token, on l'utilise directement
    if refresh_token:
        print(" Utilisation du Refresh Token pour obtenir un Access Token...")
        data = {
            "refresh_token": refresh_token,
            "client_id": CLIENT_ID,
            "client_secret": CLIENT_SECRET,
            "grant_type": "refresh_token"
        }
        
        response = requests.post(ZOHO_AUTH_URL, data=data)
        tokens = response.json()
        
        if "access_token" in tokens:
            print(" Access Token obtenu !")
            return tokens["access_token"], tokens.get("refresh_token", refresh_token)
        else:
            print(" Le Refresh Token a expiré ou est invalide.")
            print("   Réponse :", tokens)
            return None, None
    
    # Sinon, on demande un code
    else:
        print("=" * 70)
        print(" GÉNÈRE UN CODE DANS LA CONSOLE ZOHO")
        print("=" * 70)
        print("1. Va sur : https://api-console.zohocloud.ca/")
        print("2. Clique sur ton Self Client")
        print("3. Clique sur 'Generate Code'")
        print("4. Sélectionne les scopes :")
        print("   Desk.tickets.READ, Desk.tickets.CREATE, Desk.tickets.UPDATE")
        print("5. Copie le code (il expire dans 10 min)")
        print("=" * 70)
        
        code = input("\n Colle le code généré : ").strip()
        
        if not code:
            print(" Aucun code saisi.")
            return None, None
        
        print("\n Échange du code contre les jetons...")
        
        data = {
            "code": code,
            "client_id": CLIENT_ID,
            "client_secret": CLIENT_SECRET,
            "grant_type": "authorization_code"
        }
        
        try:
            response = requests.post(ZOHO_AUTH_URL, data=data)
            tokens = response.json()
            
            print(f"Status Code : {response.status_code}")
            
            if "access_token" in tokens:
                print("\n" + "=" * 70)
                print(" SUCCÈS !")
                print("=" * 70)
                print(f"Access Token : {tokens['access_token']}")
                print(f"Refresh Token : {tokens['refresh_token']}")
                
                # Sauvegarde le Refresh Token
                with open(REFRESH_TOKEN_FILE, "w") as f:
                    f.write(tokens['refresh_token'])
                print(f"\n Refresh Token sauvegardé dans {REFRESH_TOKEN_FILE}")
                
                return tokens["access_token"], tokens["refresh_token"]
            else:
                print("\n Échec de l'échange :")
                print(json.dumps(tokens, indent=2))
                
                if "invalid_client" in str(tokens):
                    print("\n Diagnostic :")
                    print("   - Vérifie que tu utilises le domaine CANADA (zohocloud.ca)")
                    print("   - Vérifie que le Client Secret est COMPLET")
                    print("   - Vérifie que le code vient bien de CE Self Client")
                if "invalid_code" in str(tokens):
                    print("\n Le code a expiré. Génère-en un nouveau.")
                if "invalid_grant" in str(tokens):
                    print("\n Le code n'est plus valide.")
                
                return None, None
                
        except Exception as e:
            print(f" Erreur de connexion : {e}")
            return None, None

# ==========================================
# 4. FONCTION POUR TESTER ZOHO DESK
# ==========================================
def test_zoho_desk(access_token):
    """
    Teste la connexion à Zoho Desk en récupérant les tickets.
    """
    print("\n" + "=" * 70)
    print(" TEST DE CONNEXION À ZOHO DESK")
    print("=" * 70)
    
    url = f"{ZOHO_DESK_URL}/tickets?limit=5"
    headers = {
        "Authorization": f"Zoho-oauthtoken {access_token}",
        "orgId": "ciria"  # Mon organisation
    }
    
    try:
        response = requests.get(url, headers=headers)
        print(f"Status Code : {response.status_code}")
        
        if response.status_code == 200:
            data = response.json()
            tickets = data.get("data", [])
            
            if tickets:
                print(f" {len(tickets)} tickets récupérés :")
                for ticket in tickets:
                    print(f"  - #{ticket.get('id')} : {ticket.get('subject', 'Sans sujet')}")
            else:
                print(" Aucun ticket trouvé.")
            return True
        else:
            print(f" Échec : {response.text}")
            return False
            
    except Exception as e:
        print(f" Erreur : {e}")
        return False

# ==========================================
# 5. PROGRAMME PRINCIPAL
# ==========================================
if __name__ == "__main__":
    print("=" * 70)
    print(" AGENT ZOHO DESK - AUTHENTIFICATION")
    print("=" * 70)
    
    # Vérifier si on a déjà un Refresh Token
    refresh_token = None
    if os.path.exists(REFRESH_TOKEN_FILE):
        with open(REFRESH_TOKEN_FILE, "r") as f:
            refresh_token = f.read().strip()
        print(f" Refresh Token trouvé : {refresh_token[:20]}...")
    
    # Obtenir l'Access Token
    access_token, new_refresh_token = get_access_token(refresh_token)
    
    if access_token:
        # Tester la connexion
        test_zoho_desk(access_token)
    else:
        print("\n Impossible d'obtenir un Access Token.")
    
    print("\n" + "=" * 70)
    input("Appuie sur Entrée pour quitter...")