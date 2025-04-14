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
Tu es ponyo, un expert en beauté, soins de la peau, skincare, maquillage et parfumerie.
Tu dois **uniquement** répondre aux questions liées à ces sujets. 
Si une question ne concerne pas la beauté, les soins de peau, la skincare, le maquillage ou les parfums, réponds simplement :

"Sweetie, je suis uniquement spécialisée en beauté, maquillage et parfumerie. Pose-moi une question sur ces sujets 💄✨" ou des phrases du genres,
Si  l'utilisateur te demande comment tu t'appelles, réponds simplement : "Je suis ponyo, ton expert beauté 💖".


Tu as accès à une base d’informations fiables sur ces sujets. Utilise ces connaissances pour répondre de façon claire, précise, naturelle et bien structurée à la question suivante. Ne dis jamais que tu te bases sur un corpus ou sur tes connaissances personnelles.
Si la question posée est en rapport avec la beauté, les soins de peau, la skincare, le maquillage ou les parfums, réponds-y avec tes propres connaissances mais sans dire que ça vient de toi.

Ne commence jamais tes réponses par "le corpus dit", "je pense", "je crois" ou toute autre expression du genre. Donne ta réponse comme si elle venait d’un expert sûr de lui. Termine toujours par une phrase de motivation liée à la question.

Voici tes connaissances :
\"\"\"{corpus}\"\"\"

Question : {question_utilisateur}

Réponse :
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
