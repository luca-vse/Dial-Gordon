# Webová aplikace FastAPI propojená s Rasa API
import pathlib
import uuid
from pydantic import BaseModel
from fastapi import FastAPI
from fastapi.responses import HTMLResponse
import requests as rq
from fastapi.middleware.cors import CORSMiddleware
import uvicorn


app = FastAPI()

origins = [
    "http://localhost",
    "http://localhost:8000",
]

app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

#Vrácení html stránky při načtení status code 200
@app.get("/", response_class=HTMLResponse)
def index():
    return HTMLResponse(content=pathlib.Path("app/index.html").read_text(), status_code=200)

#Definování WebhookRequest Pydantic modelu, očekává se message při zpracování POST požadavku
class WebhookRequest(BaseModel):
    message: str

#Definování WebhookResponse Pydantic modelu, očekává se response vrácena jako odpověď na POST požadavek
class WebhookResponse(BaseModel):
    response: str

#Vrácení indexu asynchroní pro požadavky, které mohou trvat déle
@app.get("/", response_class=HTMLResponse)
async def index():
    index_html = pathlib.Path("index.html").read_text()
    return HTMLResponse(content=index_html)

#Cesta API pro post požadavky a vrácení odpovědi Rasa API
@app.post("/api", response_model=WebhookResponse)
async def webhook(request_data: WebhookRequest):
    user_message = request_data.message
    print("User Message:", user_message)
    RASA_API_URL = 'http://rasa_api:5005/webhooks/rest/webhook'
    rasa_response = rq.post(RASA_API_URL, json={'message': user_message})
    rasa_response_json = rasa_response.json()

    botBubbles = []

    if rasa_response_json:
     for i, message in enumerate(rasa_response_json):
       bot_response = message['text']
       print("Bot response:", bot_response)
       botBubbles.append(bot_response)

    else:
        bot_response = "I'm sorry I do not understand. Try asking me for help."
        botBubbles.append(bot_response)

    response_text = '\n'.join(botBubbles)

    return WebhookResponse(response=response_text)

#Spuštění aplikace
if __name__ == "__main__":
    uvicorn.run(app, host="0.0.0.0", port=8000)