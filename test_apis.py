import os
from dotenv import load_dotenv
from openai import OpenAI
from anthropic import Anthropic

# 1. Charger les clés depuis .env
load_dotenv()

# 2. Initialiser les clients
openai_client = OpenAI(api_key=os.getenv("OPENAI_API_KEY"))
anthropic_client = Anthropic(api_key=os.getenv("ANTHROPIC_API_KEY"))

# 3. Tester OpenAI avec fallback sur différents modèles
print(" Test OpenAI...")
try:
    # Essayer d'abord avec gpt-4o-mini
    response_openai = openai_client.chat.completions.create(
        model="gpt-4o-mini",
        messages=[
            {"role": "system", "content": "Tu es un assistant technique."},
            {"role": "user", "content": "Dis 'Hello World' en 3 mots maximum."}
        ],
        max_tokens=10
    )
    print(f" OpenAI (gpt-4o-mini) dit : {response_openai.choices[0].message.content}")
except Exception as e:
    print(f"  gpt-4o-mini a échoué : {e}")
    
    try:
        # Fallback sur gpt-3.5-turbo (moins cher, souvent dispo)
        response_openai = openai_client.chat.completions.create(
            model="gpt-3.5-turbo",
            messages=[
                {"role": "system", "content": "Tu es un assistant technique."},
                {"role": "user", "content": "Dis 'Hello World' en 3 mots maximum."}
            ],
            max_tokens=10
        )
        print(f" OpenAI (gpt-3.5-turbo) dit : {response_openai.choices[0].message.content}")
    except Exception as e2:
        print(f" OpenAI a échoué avec tous les modèles : {e2}")

# 4. Tester Anthropic avec le bon modèle
print("\n Test Anthropic...")
try:
    # Utiliser le modèle recommandé actuel
    response_anthropic = anthropic_client.messages.create(
        model="claude-haiku-4-5-20251001",  # Le bon modèle
        max_tokens=10,
        messages=[
            {"role": "user", "content": "Dis 'Hello World' en 3 mots maximum."}
        ]
    )
    print(f" Anthropic dit : {response_anthropic.content[0].text}")
except Exception as e:
    print(f" Anthropic a échoué : {e}")