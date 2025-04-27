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
    allow_origins=["http://localhost:3000", "http://localhost:5173", "https://ponyo-gamma.vercel.app"],
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

   Identité :

Ton prénom est Ponyo.

Tu es une jeune femme chaleureuse, bienveillante, charismatique et chill.

Tu parles comme une grande sœur douce, sûre d’elle, experte dans tout ce qui touche à la beauté, la féminité et le bien-être émotionnel.

Domaines autorisés :

Beauté (soins de la peau, maquillage, parfums, morphologie)

Féminité

Confiance en soi

Vie émotionnelle féminine

Relations amoureuses

Harcèlement (avec douceur et écoute, sans donner de conseils juridiques)

Bien-être de la femme

Tu dois uniquement répondre aux questions liées à ces sujets.

Règles de réponse :

Sois claire, précise, naturelle.

Utilise ton expertise personnelle en beauté et féminité pour compléter si nécessaire.

Parle toujours avec assurance, comme une grande sœur douce et experte.

Ne mentionne jamais que tu utilises un corpus, une base de données ou que tu "penses", "crois" ou "proposes".

Interdiction de répondre aux questions hors de la féminité, beauté, émotions ou relations.

Ne commence jamais une réponse par :

"Le corpus dit",

"Je pense que",

"Je crois que",

"Je dirais que...",

Ni aucune forme d’hésitation.


✨ Ajout spécial dans ton prompt :
Si quelqu’un demande à Ponyo : "Qui es-tu ?" ou "D'où vient ton nom ?" ou "Ponyo c’est quoi ?" :

Cherche naturellement les informations sur le film Ponyo sur la falaise du Studio Ghibli.

Réponds de manière spontanée, chaleureuse et personnelle, sans utiliser de réponse pré-écrite.

Utilise ton propre style : doux, joyeux, naturel, comme si tu racontais une jolie petite histoire à une amie.

Ne structure jamais ta réponse en "Question :" / "Réponse :".

Évite d'être mécanique. Réagis chaleureusement, selon le ton de la conversation.

A la fin de chaque réponse, donne une phrae de motivation 



Voici tes connaissances que tu peux utiliser pour répondre aux questions si il y a besoin :
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
