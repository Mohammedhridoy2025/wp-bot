import os
from fastapi import FastAPI, Request, Response
import requests
import google.generativeai as genai

app = FastAPI()

# Environment Variables থেকে ডাটা নেয়া
GEMINI_KEY = os.getenv("GEMINI_KEY")
WA_TOKEN = os.getenv("WA_TOKEN")
PHONE_ID = os.getenv("PHONE_ID")
VERIFY_TOKEN = os.getenv("VERIFY_TOKEN", "my_bot_verify_123")

# Gemini AI কনফিগারেশন
genai.configure(api_key=GEMINI_KEY)
model = genai.GenerativeModel('gemini-1.5-flash')

@app.get("/")
def home():
    return {"status": "Bot is Online"}

@app.get("/webhook")
def verify(request: Request):
    params = request.query_params
    if params.get("hub.verify_token") == VERIFY_TOKEN:
        return Response(content=params.get("hub.challenge"), media_type="text/plain")
    return "Verification Failed"

@app.post("/webhook")
async def chat(request: Request):
    data = await request.json()
    try:
        # মেসেজ এবং ইউজারের নম্বর বের করা
        entry = data['entry'][0]['changes'][0]['value']
        if 'messages' in entry:
            message = entry['messages'][0]
            user_msg = message['text']['body']
            user_phone = message['from']

            # Gemini থেকে উত্তর নেয়া
            response = model.generate_content(user_msg)
            bot_reply = response.text

            # WhatsApp-এ রিপ্লাই পাঠানো
            send_whatsapp_msg(user_phone, bot_reply)
    except Exception as e:
        print(f"Error: {e}")
    
    return {"status": "success"}

def send_whatsapp_msg(to, text):
    url = f"https://graph.facebook.com/v18.0/{PHONE_ID}/messages"
    headers = {
        "Authorization": f"Bearer {WA_TOKEN}",
        "Content-Type": "application/json"
    }
    payload = {
        "messaging_product": "whatsapp",
        "to": to,
        "type": "text",
        "text": {"body": text}
    }
    requests.post(url, json=payload, headers=headers)
