# Healthy Clinic Chatbot

Professional chatbot starter for web chat and WhatsApp webhook support, powered by Flask + Groq.

## Features

- Web chat UI for clinic support conversations
- WhatsApp webhook endpoint (`/whatsapp`)
- Safe configuration through environment variables
- Basic reliability improvements (timeouts, error handling, bounded history)
- Persistent chat history with SQLite (`chat_history.db`)
- Health endpoint for deployment checks (`/health`)
- Input validation and consistent JSON API responses

## Quick Start

1. Create and activate a virtual environment:

   - Windows PowerShell:
     - `python -m venv .venv`
     - `.\.venv\Scripts\Activate.ps1`

2. Install dependencies:

   - `pip install -r requirements.txt`

3. Create your environment file:

   - `copy .env.example .env`
   - Fill real values in `.env`

4. Run the website:

   - `python app.py`
   - Open `http://127.0.0.1:5000`

## Run Automated Tests

- `pytest -q`

## Optional: ngrok for public webhook URL

- Run `python start_ngrok.py`
- Use `<public_url>/whatsapp` in your WhatsApp provider webhook settings

## API Endpoints

- `GET /health`: service status and version
- `POST /chat`: accepts `message` and `conversation_id`, returns assistant reply
- `POST /whatsapp`: webhook endpoint for WhatsApp provider events

## Environment Variables

- `GROQ_API_KEY`: Groq API key (required)
- `WHAPI_TOKEN`: WhatsApp API token (optional for website chat, required for WhatsApp reply)
- `WHAPI_URL`: WhatsApp send-message endpoint
- `NGROK_AUTHTOKEN`: ngrok auth token (required for `start_ngrok.py`)
- `MAX_HISTORY_MESSAGES`: max conversation messages to keep in memory
- `MAX_MESSAGE_LENGTH`: max accepted characters per user message
- `FLASK_DEBUG`: `1` for debug mode, `0` for off
- `DATABASE_PATH`: SQLite database file path
- `APP_VERSION`: app version returned by the health endpoint

## Production Notes

- Never commit `.env` with real keys
- Use a production WSGI server (for example Gunicorn on Linux) instead of Flask development server
- Add HTTPS and proper reverse proxy when deploying publicly

## Features
- AI chatbot using API
- Chat history storage
- Web interface

## Tech Stack
- Python
- Flask
- HTML/CSS

## How to Run
pip install -r requirements.txt
python app.py
