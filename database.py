import secrets
from datetime import datetime, timedelta
from motor.motor_asyncio import AsyncIOMotorClient
from config import MONGO_URI, OWNER_ID, NORMAL_USER_EXPIRY_DAYS

client = AsyncIOMotorClient(MONGO_URI)
db = client['RailwayMusicAPI']
users_col = db['api_keys']
cache_col = db['audio_cache']

users_col.create_index("api_key", unique=True)
users_col.create_index("user_id", unique=True)
cache_col.create_index("query", unique=True)

async def generate_api_key(user_id: int):
    existing = await users_col.find_one({"user_id": user_id})
    if existing: return existing["api_key"], existing.get("expiry_date"), existing.get("is_permanent")

    new_key = f"MKEY-{secrets.token_hex(12).upper()}"
    is_permanent = (user_id == OWNER_ID)
    expiry_date = None if is_permanent else datetime.utcnow() + timedelta(days=NORMAL_USER_EXPIRY_DAYS)

    await users_col.insert_one({
        "user_id": user_id, "api_key": new_key, "is_permanent": is_permanent,
        "expiry_date": expiry_date, "request_count": 0, "created_at": datetime.utcnow()
    })
    return new_key, expiry_date, is_permanent

async def get_user_info(user_id: int):
    return await users_col.find_one({"user_id": user_id})

async def verify_and_track_api_key(api_key: str):
    user = await users_col.find_one({"api_key": api_key})
    if not user: return False, "Invalid API Key"
    if not user["is_permanent"] and datetime.utcnow() > user["expiry_date"]: return False, "API Key Expired"
    
    await users_col.update_one({"api_key": api_key}, {"$inc": {"request_count": 1}})
    return True, "Valid"

async def get_cached_file(query: str):
    data = await cache_col.find_one({"query": query.lower()})
    return data["file_id"] if data else None

async def set_cached_file(query: str, file_id: str):
    await cache_col.update_one({"query": query.lower()}, {"$set": {"file_id": file_id}}, upsert=True)
