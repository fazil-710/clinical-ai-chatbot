import os
from collections import deque

from dotenv import load_dotenv
from groq import Groq

load_dotenv()

API_KEY = os.getenv("GROQ_API_KEY")
MAX_HISTORY_MESSAGES = int(os.getenv("MAX_HISTORY_MESSAGES", "30"))

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

if not API_KEY:
    raise RuntimeError("Missing GROQ_API_KEY in environment variables.")

client = Groq(api_key=API_KEY)
conversation_history = deque(maxlen=MAX_HISTORY_MESSAGES)

def chat(user_message):
    conversation_history.append({
        "role": "user",
        "content": user_message
    })

    response = client.chat.completions.create(
        model="llama-3.3-70b-versatile",
        messages=[
            {"role": "system", "content": SYSTEM_PROMPT}
        ] + list(conversation_history),
        max_tokens=300,
        temperature=0.7
    )

    bot_reply = response.choices[0].message.content

    conversation_history.append({
        "role": "assistant",
        "content": bot_reply
    })

    return bot_reply

def main():
    print("=" * 50)
    print("  Healthy  Clinic  is running for you!")
    print("  Type 'quit' to stop.")
    print("=" * 50)
    print()

    while True:
        user_input = input("You: ").strip()

        if not user_input:
            continue

        if user_input.lower() in ["quit", "exit", "bye"]:
            print("Bot: Goodbye! Have a great day.")
            break

        reply = chat(user_input)
        print(f"Bot: {reply}")
        print()

if __name__ == "__main__":
    main()