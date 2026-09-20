import os
from dotenv import load_dotenv

load_dotenv()

API_ID = int(os.getenv("API_ID", 37044974))
API_HASH = os.getenv("API_HASH", "67fe7b82eecda7de0d8149c4bb43d1bb")
KEY_BOT_TOKEN = os.getenv("KEY_BOT_TOKEN", "8661876027:AAH9y-5YIwU0wQ06MwEVMnGRWWMwgjkIcC4")
UPLOADER_BOT_TOKEN = os.getenv("UPLOADER_BOT_TOKEN", "8797731102:AAF9L502jJLfXRists603IZErhAv9OJ-O9Y")
MONGO_URI = os.getenv("MONGO_URI", "mongodb+srv://yash987987987977_db_user:ol9opOsfRmrabK5C@cluster0.5reqygm.mongodb.net/?retryWrites=true&w=majority")
CACHE_CHANNEL_ID = int(os.getenv("CACHE_CHANNEL_ID", -1004489070540))
OWNER_ID = int(os.getenv("OWNER_ID", 8203857803))
NORMAL_USER_EXPIRY_DAYS = 7
PORT = int(os.getenv("PORT", 8000))

# नया वेरिएबल लिंक से कुकीज़ उठाने के लिए
COOKIES_URL = os.getenv("COOKIES_URL", "https://batbin.me/raw/deejay")
