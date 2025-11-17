from telethon import TelegramClient
from config import API_ID, API_HASH, BOT_TOKEN, STRING
from pyrogram import Client
import sys


# Telethon client (for restricted content)
client = TelegramClient("telethonbot", API_ID, API_HASH)


# Pyrogram client (main bot) - WITH PLUGINS ✅
app = Client(
    "pyrogrambot", 
    api_id=API_ID, 
    api_hash=API_HASH, 
    bot_token=BOT_TOKEN,
    plugins=dict(root="plugins")  # ✅ YE LINE ADD KARO - YE MISSING THI
)


# Userbot client (optional - for premium features)
userbot = Client("4gbbot", api_id=API_ID, api_hash=API_HASH, session_string=STRING)



async def start_client():
    # Start Telethon bot
    if not client.is_connected():
        await client.start(bot_token=BOT_TOKEN)
        print("✅ Telethon started...")
    
    # Start Userbot (optional)
    if STRING:
        try:
            await userbot.start()
            print("✅ Userbot started...")
        except Exception as e:
            print(f"⚠️ String session error: {e}")
            print("Note: If not using STRING features, remove STRING from .env")
            sys.exit(1)
    
    # Start Pyrogram bot
    await app.start()
    print("✅ Pyrogram started with plugins loaded...")  # ✅ Updated message
    
    return client, app, userbot
