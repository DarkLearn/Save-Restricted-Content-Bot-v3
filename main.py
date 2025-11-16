import asyncio
from shared_client import start_client
from pyrogram import idle

async def main():
    await start_client()
    await idle()

if __name__ == "__main__":
    try:
        print("🚀 Starting bot...")
        asyncio.run(main())
    except KeyboardInterrupt:
        print("\n⏹️ Bot stopped")
    except Exception as e:
        print(f"❌ Error: {e}")
