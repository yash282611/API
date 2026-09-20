import os
from dotenv import load_dotenv

load_dotenv()

API_ID = int(os.getenv("API_ID", 0))
API_HASH = os.getenv("API_HASH", "")
KEY_BOT_TOKEN = os.getenv("KEY_BOT_TOKEN", "")
UPLOADER_BOT_TOKEN = os.getenv("UPLOADER_BOT_TOKEN", "")
MONGO_URI = os.getenv("MONGO_URI", "")
CACHE_CHANNEL_ID = int(os.getenv("CACHE_CHANNEL_ID", 0))
OWNER_ID = int(os.getenv("OWNER_ID", 0))
NORMAL_USER_EXPIRY_DAYS = 7
PORT = int(os.getenv("PORT", 8000))
