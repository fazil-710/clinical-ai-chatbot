import os
import time
from pyngrok import conf, ngrok

auth_token = os.getenv("NGROK_AUTHTOKEN")
if not auth_token:
    raise RuntimeError("Missing NGROK_AUTHTOKEN in environment variables.")

conf.get_default().auth_token = auth_token
url = ngrok.connect(5000)
print("=" * 50)
print(f"  PUBLIC URL: {url}")
print(f"  WhatsApp webhook: {url}/whatsapp")
print("=" * 50)
print("  Keep this running! Press Ctrl+C to stop.")
print()

try:
    while True:
        time.sleep(1)
except KeyboardInterrupt:
    print("Tunnel closed.")
    ngrok.kill()
