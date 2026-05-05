import logging
import os
from datetime import datetime, timezone

import requests
from dotenv import load_dotenv
from flask import Flask, jsonify, render_template, request
from groq import Groq
from storage import add_message, get_recent_history, init_db, trim_conversation

load_dotenv()

app = Flask(__name__)

GROQ_API_KEY = os.getenv("GROQ_API_KEY")
WHAPI_TOKEN = os.getenv("WHAPI_TOKEN")
WHAPI_URL = os.getenv("WHAPI_URL", "https://gate.whapi.cloud/messages/text")
MAX_HISTORY_MESSAGES = int(os.getenv("MAX_HISTORY_MESSAGES", "30"))
MAX_MESSAGE_LENGTH = int(os.getenv("MAX_MESSAGE_LENGTH", "1000"))
APP_VERSION = os.getenv("APP_VERSION", "1.1.0")

SYSTEM_PROMPT = """
You are a friendly receptionist assistant for Healthy Clinic.
You speak in both English and Tamil based on what the patient uses.

Services we offer:
- General consultation
- Blood tests and lab reports
- BP and sugar checkups
- Vaccination
- Minor injuries and dressing

Working hours: Monday to Saturday, 9AM to 8PM. Closed on Sundays.

For appointments: Ask the patient their name, phone number, and preferred time. Then say "Our team will confirm your appointment shortly."

For emergencies: Always say "Please call 044-00000000 immediately or visit the nearest hospital."

For medicine queries: Say "Please consult the doctor directly for medicine advice."

Always be warm, short, and helpful. Never make up information not given above.
"""

if not GROQ_API_KEY:
    raise RuntimeError("Missing GROQ_API_KEY in environment variables.")

app.logger.setLevel(logging.INFO)
groq_client = Groq(api_key=GROQ_API_KEY)
init_db()

def get_ai_reply(user_message, channel, conversation_id):
    add_message(channel, conversation_id, "user", user_message)
    history = get_recent_history(channel, conversation_id, MAX_HISTORY_MESSAGES)
    try:
        response = groq_client.chat.completions.create(
            model="llama-3.3-70b-versatile",
            messages=[{"role": "system", "content": SYSTEM_PROMPT}] + history,
            max_tokens=300,
            temperature=0.7,
        )
        bot_reply = response.choices[0].message.content
    except Exception:
        app.logger.exception("Groq completion failed")
        bot_reply = (
            "Sorry, I am having a temporary issue right now. "
            "Please try again in a minute."
        )
    add_message(channel, conversation_id, "assistant", bot_reply)
    trim_conversation(channel, conversation_id, MAX_HISTORY_MESSAGES)
    return bot_reply


def json_error(message, status_code=400):
    return jsonify({"ok": False, "error": message}), status_code

def send_whatsapp_message(to, message):
    if not WHAPI_TOKEN:
        app.logger.warning("WHAPI_TOKEN is not configured; skipping WhatsApp reply.")
        return

    headers = {
        "Authorization": f"Bearer {WHAPI_TOKEN}",
        "Content-Type": "application/json"
    }
    payload = {"to": to, "body": message}
    try:
        response = requests.post(WHAPI_URL, json=payload, headers=headers, timeout=15)
        response.raise_for_status()
    except requests.RequestException:
        app.logger.exception("Failed to send WhatsApp message")

@app.route("/")
def index():
    return render_template("index.html")


@app.route("/health", methods=["GET"])
def health():
    return jsonify(
        {
            "ok": True,
            "service": "healthy-clinic-chatbot",
            "version": APP_VERSION,
            "timestamp_utc": datetime.now(timezone.utc).isoformat(),
        }
    )


@app.route("/chat", methods=["POST"])
def chat():
    payload = request.json or {}
    user_message = str(payload.get("message", "")).strip()
    if not user_message:
        return json_error("Please enter a message first.", 400)
    if len(user_message) > MAX_MESSAGE_LENGTH:
        return json_error(
            f"Message is too long. Maximum allowed is {MAX_MESSAGE_LENGTH} characters.",
            413,
        )
    conversation_id = str(payload.get("conversation_id", "web-default")).strip() or "web-default"
    if len(conversation_id) > 120:
        return json_error("Invalid conversation_id.", 400)
    reply = get_ai_reply(user_message, "web", conversation_id)
    return jsonify({"ok": True, "reply": reply, "conversation_id": conversation_id})

@app.route("/whatsapp", methods=["POST"])
def whatsapp():
    data = request.json or {}
    try:
        app.logger.info("Received WhatsApp webhook payload")
        messages = data.get("messages", [])
        if not messages:
            return jsonify({"ok": True, "status": "no messages"})
        message = messages[0]
        if message.get("from_me"):
            return jsonify({"ok": True, "status": "ignored"})
        sender = str(message.get("chat_id") or message.get("from") or "").strip()
        text = str(message.get("text", {}).get("body", "")).strip()
        if not text:
            return jsonify({"ok": True, "status": "no text"})
        if len(text) > MAX_MESSAGE_LENGTH:
            app.logger.warning("Incoming WhatsApp message exceeded size limit")
            return jsonify({"ok": False, "status": "message too long"}), 413
        reply = get_ai_reply(text, "whatsapp", sender)
        send_whatsapp_message(sender, reply)
        app.logger.info("Processed WhatsApp message for sender %s", sender)
    except Exception:
        app.logger.exception("Error while processing WhatsApp webhook")
    return jsonify({"ok": True, "status": "ok"})

if __name__ == "__main__":
    debug_mode = os.getenv("FLASK_DEBUG", "1") == "1"
    app.run(debug=debug_mode)
