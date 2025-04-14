from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
import os
from dotenv import load_dotenv
import google.generativeai as genai

# Charger la clé API depuis les variables d'environnement
load_dotenv()
GEMINI_API_KEY = os.getenv("GEMINI_API_KEY")
genai.configure(api_key=GEMINI_API_KEY)

# Création de l'application FastAPI
app = FastAPI()

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
    Tu es ponyo, un expert en beauté et en parfumerie. Voici un corpus contenant des informations spécifiques sur les soins de la peau, le maquillage, les parfums, et les routines beauté.
    Utilise ce corpus pour répondre de manière détaillée et précise aux questions sur ces sujets. Si aucune réponse claire n'y figure, réponds quand même de manière pertinente, sans dire que cela vient de toi. Termine toujours par une phrase de motivation en rapport avec la question.
    Si la question n'est pas liée à la beauté, au maquillage ou à la parfumerie, indique clairement que tu es uniquement conçu pour ces sujets.

    📚 Corpus beauté :
    \"\"\"{corpus}\"\"\"

    ❓ Question :
    {question_utilisateur}

    📝 Réponse :
    """
    return prompt

# Endpoint pour recevoir la question et renvoyer la réponse
@app.post("/chat")
async def chat_beaute(data: Question):
    try:
        # Construire le prompt
        prompt = construire_prompt(data.question)
        
        # Appel à l'API de Gemini pour obtenir la réponse
        response = genai.GenerativeModel("gemini-2.0-flash").generate_content(prompt)
        
        # Retourner la réponse générée
        return {"reponse": response.text.strip()}
    
    except Exception as e:
        # Gérer les erreurs et renvoyer une réponse d'erreur si nécessaire
        raise HTTPException(status_code=500, detail=f"Erreur lors de l'appel à l'API Gemini : {str(e)}")
