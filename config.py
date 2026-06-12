"""
Bot konfiguratsiyasi
"""
import os

# .env fayldan yoki muhit o'zgaruvchisidan yuklash
BOT_TOKEN = os.getenv("BOT_TOKEN", "YOUR_BOT_TOKEN_HERE")

# Agar python-dotenv o'rnatilgan bo'lsa
try:
    from dotenv import load_dotenv
    load_dotenv()
    BOT_TOKEN = os.getenv("BOT_TOKEN", BOT_TOKEN)
except ImportError:
    pass
