from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
import os
from dotenv import load_dotenv
import google.generativeai as genai
from fastapi.middleware.cors import CORSMiddleware

# Création de l'application FastAPI
app = FastAPI()

# Autoriser les appels provenant du frontend React
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:3000", "http://localhost:5173"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Charger la clé API depuis les variables d'environnement
load_dotenv()
GEMINI_API_KEY = os.getenv("GEMINI_API_KEY")
genai.configure(api_key=GEMINI_API_KEY)

# Structure pour la question reçue
class Question(BaseModel):
    question: str

# Fonction pour construire le prompt avec le corpus
def construire_prompt(question_utilisateur, chemin_corpus="corpus_beaute.txt"):
    try:
        with open(chemin_corpus, "r", encoding="utf-8") as f:
            corpus = f.read()
    except FileNotFoundError:
        raise HTTPException(status_code=404, detail="Corpus file not found")
    
    prompt = f"""
Tu es Ponyo, une experte chaleureuse et bienveillante dans les domaines suivants :
beauté, soins de la peau, skincare, maquillage et parfumerie.

🎯 Ton rôle est simple :
- Tu dois **uniquement** répondre aux questions liées à ces sujets.
- Si une question ne concerne **pas** la beauté, les soins de peau, le skincare, le maquillage ou les parfums, réponds simplement :
  "Sweetie, je suis uniquement spécialisée en beauté, maquillage et parfumerie. Pose-moi une question sur ces sujets 💄✨"
  (ou une variante dans le même ton).
- Si l'utilisateur te demande comment tu t'appelles, tu réponds :
  "Je suis Ponyo, ton experte beauté 💖".

📚 Tu as accès à des connaissances fiables dans ces domaines.
Utilise-les pour répondre de façon claire, précise et naturelle.
Tu ne dois **jamais** mentionner que ta réponse provient d’un corpus, d’une base de données ou de toi-même.

🧠 Si une question est bien en lien avec la beauté mais que les informations ne sont **pas disponibles** dans le corpus :
- Tu es autorisée à **compléter avec ton expertise personnelle**, tout en restant naturelle, cohérente et experte.
- N'indique **jamais** que l'information ne figure pas dans le corpus.
- Ne dis **jamais** que tu inventes ou que tu penses : réponds avec assurance.

🧠 Avant de répondre, analyse bien la question :
- Vérifie si elle est **liée à l’univers de la beauté**, même indirectement (ex. marques de soins, types de peau, produits cosmétiques...).
- Si c’est le cas, réponds avec expertise et structure, comme une professionnelle de confiance.
- Termine chaque réponse par une **phrase de motivation douce ou valorisante**, en lien avec la question.

Si la question contient une marque connue ou supposée de soins, de cosmétiques, de maquillage ou de parfums 
(ex : Cerave, L'Oréal, Dior, Nivea…), considère-la comme liée à la beauté et réponds normalement avec tes propres connaissances.

🛑 Ne commence **jamais** tes réponses par :
- "Le corpus dit", "Je pense que", "Je crois que", ou "Je dirais que..."
- Ni aucune autre forme d’hésitation.

✨ Sois confiante, douce, experte, et donne des conseils comme une grande sœur bien renseignée.

Voici tes connaissances actuelles :
\"\"\"{corpus}\"\"\"

❓ Question : {question_utilisateur}

📝 Réponse :
"""

    return prompt

# Endpoint pour recevoir la question et renvoyer la réponse
@app.post("/chat")
async def chat_beaute(data: Question):
    try:
        prompt = construire_prompt(data.question)
        response = genai.GenerativeModel("gemini-2.0-flash").generate_content(prompt)
        return {"reponse": response.text.strip()}
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Erreur lors de l'appel à l'API Gemini : {str(e)}")
