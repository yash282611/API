import os
import time
import asyncio
import urllib.request
from fastapi import FastAPI, HTTPException, Header
import uvicorn
from pyrogram import Client, filters
from pyrogram.types import InlineKeyboardMarkup, InlineKeyboardButton
import yt_dlp

from config import *
from database import (
    generate_api_key, verify_and_track_api_key, 
    get_cached_file, set_cached_file, get_user_info, db
)

# 🔥 FIX: Added in_memory=True to prevent Session Lock issues on Railway
key_bot = Client("KeyGenBot", api_id=API_ID, api_hash=API_HASH, bot_token=KEY_BOT_TOKEN, in_memory=True)
uploader_bot = Client("UploaderBot", api_id=API_ID, api_hash=API_HASH, bot_token=UPLOADER_BOT_TOKEN, in_memory=True)

@key_bot.on_message(filters.command("start") & filters.private)
async def start_cmd(client, message):
    buttons = InlineKeyboardMarkup([
        [InlineKeyboardButton("🔑 Generate API Key", callback_data="gen_key")],
        [InlineKeyboardButton("📊 My API Info", callback_data="my_api_info")],
        [InlineKeyboardButton("⚡ Speed Test", callback_data="run_speedtest")]
    ])
    await message.reply("⚡ **Lightning Fast Music API!**\n\nअपनी API Key जनरेट करें या स्पीड चेक करें।", reply_markup=buttons)

@key_bot.on_message(filters.command(["speedtest", "ping"]) & filters.private)
async def speedtest_cmd(client, message):
    start_time = time.time()
    msg = await message.reply("🔄 **Checking API Speed...**")
    end_time = time.time()
    
    telegram_ping = round((end_time - start_time) * 1000, 2)
    
    db_start = time.time()
    await db.command("ping")
    db_end = time.time()
    api_ping = round((db_end - db_start) * 1000, 2)
    
    text = (
        "🚀 **Speed Test Results**\n\n"
        f"🤖 **Bot Latency (Telegram):** `{telegram_ping} ms`\n"
        f"⚡ **API Latency (Database):** `{api_ping} ms`\n\n"
        "🟢 **Status:** Ultra Fast"
    )
    await msg.edit_text(text)

@key_bot.on_callback_query(filters.regex("run_speedtest"))
async def speedtest_callback(client, callback_query):
    await callback_query.answer("Running Speed Test...", show_alert=False)
    await speedtest_cmd(client, callback_query.message)

@key_bot.on_callback_query(filters.regex("gen_key"))
async def gen_key_callback(client, callback_query):
    api_key, expiry_date, is_permanent = await generate_api_key(callback_query.from_user.id)
    text = f"👑 **Owner Key:** `{api_key}`" if is_permanent else f"🔑 **Key:** `{api_key}`\n⏳ **Expires:** {expiry_date.strftime('%Y-%m-%d UTC')}"
    await callback_query.answer("API Key Ready!", show_alert=False)
    await callback_query.message.edit_text(text, reply_markup=InlineKeyboardMarkup([[InlineKeyboardButton("🔙 Back", callback_data="back_start")]]))

@key_bot.on_callback_query(filters.regex("my_api_info"))
async def my_api_info_callback(client, callback_query):
    user_data = await get_user_info(callback_query.from_user.id)
    if not user_data: return await callback_query.answer("No Key Found!", show_alert=True)
    exp = "Permanent ♾️" if user_data["is_permanent"] else user_data["expiry_date"].strftime('%Y-%m-%d UTC')
    text = f"📊 **Your Analytics**\n\n🔑 **Key:** `{user_data['api_key'][:10]}...`\n📈 **Requests:** `{user_data.get('request_count', 0)}` times\n⏳ **Validity:** `{exp}`"
    await callback_query.message.edit_text(text, reply_markup=InlineKeyboardMarkup([[InlineKeyboardButton("🔙 Back", callback_data="back_start")]]))

@key_bot.on_callback_query(filters.regex("back_start"))
async def back_to_start(client, callback_query):
    await start_cmd(client, callback_query.message)


app = FastAPI(title="Turbo Music API")

@app.on_event("startup")
async def startup_event():
    # 🔥 Link से Cookies डाउनलोड करने का कोड
    if COOKIES_URL:
        try:
            print(f"📥 Downloading cookies from URL...")
            urllib.request.urlretrieve(COOKIES_URL, "cookies.txt")
            print("✅ Cookies downloaded successfully!")
        except Exception as e:
            print(f"❌ Error downloading cookies: {e}")
            
    await key_bot.start()
    await uploader_bot.start()
    print(f"🚀 API Engine Running safely on Port {PORT}")

@app.on_event("shutdown")
async def shutdown_event():
    await key_bot.stop()
    await uploader_bot.stop()

@app.get("/")
async def health_check(): 
    return {"status": "ok", "message": "Music API is Online!"}

@app.get("/speedtest")
async def api_speedtest():
    start_time = time.time()
    await db.command("ping")
    end_time = time.time()
    ping_ms = round((end_time - start_time) * 1000, 2)
    return {"status": "success", "latency_ms": ping_ms, "speed": "Lightning Fast ⚡"}

def turbo_download(query: str):
    if not os.path.exists("downloads"): os.makedirs("downloads")
    ydl_opts = {
        'format': 'bestaudio[ext=m4a]/bestaudio', 
        'cookiefile': 'cookies.txt', 
        'outtmpl': 'downloads/%(id)s.%(ext)s',
        'noplaylist': True,
        'quiet': True,
        'no_warnings': True,
        'geo_bypass': True,
        'external_downloader': 'aria2c',
        'external_downloader_args': ['-x16', '-s16', '-k1M']
    }
    with yt_dlp.YoutubeDL(ydl_opts) as ydl:
        info = ydl.extract_info(f"ytsearch1:{query}", download=True)['entries'][0]
        return ydl.prepare_filename(info), info['title'], info.get('duration', 0)

@app.get("/api/v1/download")
async def download_endpoint(query: str, api_key: str = Header(None)):
    if not api_key: raise HTTPException(status_code=403, detail="Missing API Key")
    is_valid, msg = await verify_and_track_api_key(api_key)
    if not is_valid: raise HTTPException(status_code=403, detail=msg)

    cached_file_id = await get_cached_file(query)
    if cached_file_id: return {"status": "success", "cache": True, "telegram_file_id": cached_file_id}

    try:
        file_path, title, duration = await asyncio.to_thread(turbo_download, query)
        message = await uploader_bot.send_audio(
            chat_id=CACHE_CHANNEL_ID, audio=file_path, caption=f"🎵 {title}\n⏱ {duration}s"
        )
        telegram_file_id = message.audio.file_id
        await set_cached_file(query, telegram_file_id)
        if os.path.exists(file_path): os.remove(file_path)
        return {"status": "success", "cache": False, "telegram_file_id": telegram_file_id}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

if __name__ == "__main__":
    uvicorn.run(app, host="0.0.0.0", port=PORT)
