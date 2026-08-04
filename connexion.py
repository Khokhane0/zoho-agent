# test_all_endpoints.py
import requests
import json

ACCESS_TOKEN = "1000.af74ad4aab71cdbb77831725eff8b1f4.e7798bc661772b390dca13dcf3ac0365"
ORG_ID = "ciria"  # Ton organisation

# ==========================================
# 1. Test de l'URL de base avec orgId
# ==========================================
def test_endpoint(url, headers=None, description=""):
    if headers is None:
        headers = {"Authorization": f"Zoho-oauthtoken {ACCESS_TOKEN}"}
    
    print(f"\n🧪 {description}")
    print(f"URL : {url}")
    
    try:
        response = requests.get(url, headers=headers)
        print(f"Status : {response.status_code}")
        
        if response.status_code == 200:
            try:
                data = response.json()
                print(f"✅ Succès !")
                if data.get("data"):
                    print(f"   {len(data['data'])} éléments trouvés")
                else:
                    print(f"   Réponse : {json.dumps(data, indent=2)[:200]}...")
            except:
                print(f"   Réponse (texte) : {response.text[:200]}")
        else:
            print(f"❌ Échec : {response.text[:200]}")
    except Exception as e:
        print(f"❌ Erreur : {e}")

# ==========================================
# 2. Toutes les combinaisons
# ==========================================
print("=" * 70)
print("🔍 TEST DE TOUTES LES URLS POSSIBLES")
print("=" * 70)

# Test 1 : URL de base + orgId en paramètre
test_endpoint(
    f"https://desk.zohocloud.ca/api/v1/tickets?limit=5&orgId={ORG_ID}",
    description="Test 1 : /api/v1/tickets avec orgId en paramètre"
)

# Test 2 : URL de base + orgId dans le header
headers2 = {
    "Authorization": f"Zoho-oauthtoken {ACCESS_TOKEN}",
    "orgId": ORG_ID
}
test_endpoint(
    "https://desk.zohocloud.ca/api/v1/tickets?limit=5",
    headers=headers2,
    description="Test 2 : /api/v1/tickets avec orgId dans le header"
)

# Test 3 : URL avec l'organisation dans le chemin
test_endpoint(
    f"https://desk.zohocloud.ca/api/v1/{ORG_ID}/tickets?limit=5",
    description="Test 3 : /api/v1/{org}/tickets"
)

# Test 4 : URL alternative (sans v1)
test_endpoint(
    f"https://desk.zohocloud.ca/api/tickets?limit=5&orgId={ORG_ID}",
    description="Test 4 : /api/tickets (sans v1)"
)

# Test 5 : URL avec l'organisation dans le chemin (sans v1)
test_endpoint(
    f"https://desk.zohocloud.ca/api/{ORG_ID}/tickets?limit=5",
    description="Test 5 : /api/{org}/tickets"
)

# Test 6 : URL de l'agent (comme dans le navigateur)
test_endpoint(
    f"https://desk.zohocloud.ca/agent/{ORG_ID}/api/v1/tickets?limit=5",
    description="Test 6 : /agent/{org}/api/v1/tickets"
)

# Test 7 : Récupérer les contacts (pour vérifier si l'API fonctionne)
test_endpoint(
    f"https://desk.zohocloud.ca/api/v1/contacts?limit=5&orgId={ORG_ID}",
    description="Test 7 : /api/v1/contacts (pour vérifier)"
)

# Test 8 : Récupérer les départements
test_endpoint(
    f"https://desk.zohocloud.ca/api/v1/departments?orgId={ORG_ID}",
    description="Test 8 : /api/v1/departments"
)

# Test 9 : Vérifier si l'orgId est dans les paramètres de l'URL
test_endpoint(
    f"https://desk.zohocloud.ca/api/v1/tickets?limit=5&organization_id={ORG_ID}",
    description="Test 9 : avec organization_id (pluriel)"
)

# Test 10 : Vérifier si l'orgId est nécessairement dans l'URL
test_endpoint(
    "https://desk.zohocloud.ca/api/v1/tickets?limit=5",
    description="Test 10 : sans orgId (simple)"
)

print("\n" + "=" * 70)
print("✅ TESTS TERMINÉS")
print("=" * 70)
input("\nAppuie sur Entrée pour quitter...")