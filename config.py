"""
Bot konfiguratsiyasi
"""
import os

# .env fayldan yoki muhit o'zgaruvchisidan yuklash
try:
    from dotenv import load_dotenv
    load_dotenv()
except ImportError:
    load_dotenv = None

BOT_TOKEN = os.getenv("BOT_TOKEN", "YOUR_BOT_TOKEN_HERE")
ADMIN_ID = os.getenv("ADMIN_ID", "")
