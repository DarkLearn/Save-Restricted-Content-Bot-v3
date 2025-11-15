from shared_client import app
from pyrogram import filters
from pyrogram.errors import UserNotParticipant
from pyrogram.types import BotCommand, InlineKeyboardButton, InlineKeyboardMarkup
from config import LOG_GROUP, OWNER_ID, FORCE_SUB

# Store the invite link globally (generated only once)
INVITE_LINK = None

async def get_invite_link():
    """Get or create invite link - only called once"""
    global INVITE_LINK
    if INVITE_LINK is None:
        INVITE_LINK = await app.export_chat_invite_link(FORCE_SUB)
    return INVITE_LINK

async def subscribe(app, message):
    if FORCE_SUB:
        try:
            user = await app.get_chat_member(FORCE_SUB, message.from_user.id)
            if str(user.status) == "ChatMemberStatus.BANNED":
                await message.reply_text("❌ You are Banned. Contact Support")
                return 1
        except UserNotParticipant:
            link = await get_invite_link()
            caption = "🔒 **Access Required**\n\nPlease join our channel to use the bot"
            await message.reply_text(
                caption,
                reply_markup=InlineKeyboardMarkup([[InlineKeyboardButton("🔓 Join Channel", url=link)]])
            )
            return 1
        except Exception as ggn:
            await message.reply_text(f"⚠️ Something went wrong:\n`{ggn}`")
            return 1

@app.on_message(filters.command("start") & filters.private)
async def start_command(client, message):
    join = await subscribe(client, message)
    if join == 1:
        return
    
    user = message.from_user.mention
    
    if message.text and len(message.text.split()) > 1:
        param = message.text.split()[1]
        if param == "verified":
            verify_text = (
                f"✅ **Welcome Back** {user}!\n\n"
                "🎉 Thank you for joining our channel\n"
                "🚀 You now have **full access** to all features\n\n"
                "Send any Telegram link to get started!"
            )
            await message.reply_text(verify_text)
            return
    
    welcome_text = (
        f"👋 **Welcome** {user}!\n\n"
        "\n"
        " **Your Ultimate Telegram**\n"
        "**Content Extraction Tool**\n"
        "\n\n"
        "✨ **What I Can Do:**\n"
        "• **Break restrictions** on public channels\n"
        "• **Access private** channels after login\n"
        "• **Bulk download** thousands of files\n"
        "• **Extract** photos, videos, documents\n"
        "• **Lightning fast** processing ⚡\n\n"
        "🔥 **Quick Start:**\n"
        "Just send me any Telegram link!\n\n"
        "Need help? Type /help anytime 💬"
    )
    
    buttons = InlineKeyboardMarkup([
        [InlineKeyboardButton("📞 Contact Admin", url="https://t.me/anoncracks_bot")]
    ])
    
    photo_url = "https://telegra.ph/file/d9b2d6f8c3b5a4e7f6e8d.jpg"
    
    try:
        await message.reply_photo(
            photo=photo_url,
            caption=welcome_text,
            reply_markup=buttons
        )
    except:
        await message.reply_text(text=welcome_text, reply_markup=buttons)

@app.on_message(filters.command("set"))
async def set(_, message):
    if message.from_user.id not in OWNER_ID:
        await message.reply("❌ You are not authorized to use this command.")
        return
    await app.set_bot_commands([
        BotCommand("start", "Start the bot"),
        BotCommand("help", "View all commands"),
        BotCommand("login", "Login for private channels"),
        BotCommand("logout", "Logout from bot"),
        BotCommand("batch", "Bulk extraction"),
        BotCommand("plan", "View premium plans"),
        BotCommand("myplan", "Check your plan details"),
        BotCommand("settings", "Configure settings"),
        BotCommand("setbot", "Add custom file bot"),
        BotCommand("rembot", "Remove custom bot"),
        BotCommand("session", "Generate session string"),
        BotCommand("cancel", "Cancel process"),
        BotCommand("stop", "Stop batch"),
        BotCommand("add", "Add user to premium"),
        BotCommand("rem", "Remove from premium"),
        BotCommand("ban", "Ban user from bot"),
        BotCommand("unban", "Unban user"),
        BotCommand("get", "Get all users"),
        BotCommand("stats", "Bot statistics"),
        BotCommand("lock", "Lock channel"),
        BotCommand("broadcast", "Send message to all users"),
        BotCommand("restart", "Restart the bot")
    ])
    await message.reply("✅ Commands configured successfully")

@app.on_message(filters.command("help") & filters.private)
async def help_command(client, message):
    join = await subscribe(client, message)
    if join == 1:
        return
    
    user_id = message.from_user.id
    
    if user_id in OWNER_ID:
        help_text = (
            "📚 All Commands:\n\n"
            "👤 User Commands:\n"
            "/start - Start the bot\n"
            "/help - View all commands\n"
            "/login - Login for private channels\n"
            "/logout - Logout from bot\n"
            "/batch - Bulk extraction\n"
            "/plan - View premium plans\n"
            "/myplan - Check your plan\n"
            "/pay - Buy premium\n"
            "/settings - Configure settings\n"
            "/setbot - Add custom file bot\n"
            "/rembot - Remove custom bot\n"
            "/session - Generate session string\n"
            "/cancel - Cancel process\n"
            "/status - View status\n"
            "/stop - Stop batch\n\n"
            "👑 Owner Commands:\n"
            "/add userID - Add to premium\n"
            "/rem userID - Remove from premium\n"
            "/ban userID - Ban user\n"
            "/unban userID - Unban user\n"
            "/get - Get all users list\n"
            "/stats - Bot statistics\n"
            "/lock channelID - Lock channel\n"
            "/broadcast - Send message to all\n"
            "/restart - Restart the bot"
        )
    else:
        help_text = (
            "📚 Available Commands:\n\n"
            "/start - Start the bot\n"
            "/help - View all commands\n"
            "/login - Login for private channels\n"
            "/logout - Logout from bot\n"
            "/batch - Bulk extraction\n"
            "/plan - View premium plans\n"
            "/myplan - Check your plan details\n"
            "/pay - Buy premium\n"
            "/settings - Configure settings\n"
            "/setbot - Add custom file bot\n"
            "/rembot - Remove custom bot\n"
            "/session - Generate session string\n"
            "/cancel - Cancel process\n"
            "/status - View status\n"
            "/stop - Stop batch\n\n"
            "💡 Pro Tip:\n"
            "Just forward any message or send a Telegram link!"
        )
    
    buttons = InlineKeyboardMarkup([
        [InlineKeyboardButton("📞 Contact Admin", url="https://t.me/anoncracks_bot")]
    ])
    await message.reply_text(help_text, reply_markup=buttons)

@app.on_message(filters.command("plan") & filters.private)
async def plan(client, message):
    join = await subscribe(client, message)
    if join == 1:
        return
    
    plan_text = (
        "💎 Premium Plans:\n\n"
        "✨ Premium Features:\n"
        "• Download up to 100,000 files per batch\n"
        "• Access to /batch and /bulk modes\n"
        "• Priority support & faster processing\n"
        "• Custom file bot support\n"
        "• No rate limits\n\n"
        "📞 Contact admin to upgrade now!"
    )
    buttons = InlineKeyboardMarkup([
        [InlineKeyboardButton("📞 Contact Admin", url="https://t.me/anoncracks_bot")]
    ])
    await message.reply_text(plan_text, reply_markup=buttons)

@app.on_message(filters.command(["batch", "login", "logout", "pay", "plan", "myplan", "setbot", "rembot", "myplan", "session"]) & filters.private)
async def force_sub_check(client, message):
    join = await subscribe(client, message)
    if join == 1:
        return
