from shared_client import app
from pyrogram import filters
from pyrogram.errors import UserNotParticipant
from pyrogram.types import BotCommand, InlineKeyboardButton, InlineKeyboardMarkup
from config import LOG_GROUP, OWNER_ID, FORCE_SUB


async def subscribe(app, message):
    if FORCE_SUB:
        try:
            user = await app.get_chat_member(FORCE_SUB, message.from_user.id)
            if str(user.status) == "ChatMemberStatus.BANNED":
                await message.reply_text("You are Banned. Contact Support")
                return 1
        except UserNotParticipant:
            link = await app.export_chat_invite_link(FORCE_SUB)
            caption = f"Join our channel to use the bot"
            await message.reply_photo(
                photo="https://telegra.ph/file/d8f9c8e8f7e6f5e4e3e2e1.jpg",
                caption=caption,
                reply_markup=InlineKeyboardMarkup([[InlineKeyboardButton("Join Now", url=f"{link}")]])
            )
            return 1
        except Exception as ggn:
            await message.reply_text(f"Something Went Wrong. Contact admins with following message {ggn}")
            return 1


@app.on_message(filters.command("start") & filters.private)
async def start_command(client, message):
    join = await subscribe(client, message)
    if join == 1:
        return
    
    user = message.from_user.mention
    
    welcome_text = (
        f"Hello {user}\n\n"
        "I am a Telegram content extraction bot\n\n"
        "Available Commands:\n"
        "- /help - View all commands\n"
        "- /login - Login for private channels\n"
        "- /batch - Bulk extraction\n"
        "- /plan - Check premium plans\n\n"
        "Use /help to get started"
    )
    
    buttons = InlineKeyboardMarkup([
        [InlineKeyboardButton("Help", callback_data="show_help"),
         InlineKeyboardButton("Plans", callback_data="see_plan")],
        [InlineKeyboardButton("Contact", url="https://t.me/anoncracks_bot")]
    ])
    
    await message.reply_photo(
        photo="https://telegra.ph/file/4e8d9c7b6a5f4e3d2c1b0.jpg",
        caption=welcome_text,
        reply_markup=buttons
    )


@app.on_callback_query(filters.regex("show_help"))
async def show_help_callback(client, callback_query):
    await callback_query.message.delete()
    await send_or_edit_help_page(client, callback_query.message, 0)
    await callback_query.answer()


@app.on_message(filters.command("set"))
async def set(_, message):
    if message.from_user.id not in OWNER_ID:
        await message.reply("You are not authorized to use this command.")
        return
     
    await app.set_bot_commands([
        BotCommand("start", "Start the bot"),
        BotCommand("batch", "Extract in bulk"),
        BotCommand("login", "Get into the bot"),
        BotCommand("setbot", "Add your bot for handling files"),
        BotCommand("logout", "Get out of the bot"),
        BotCommand("dl", "Download videos from sites"),
        BotCommand("status", "Refresh Payment status"),
        BotCommand("transfer", "Gift premium to others"),
        BotCommand("add", "Add user to premium"),
        BotCommand("rem", "Remove from premium"),
        BotCommand("rembot", "Remove your custom bot"),
        BotCommand("settings", "Personalize things"),
        BotCommand("plan", "Check premium plans"),
        BotCommand("help", "View help menu"),
        BotCommand("cancel", "Cancel process"),
        BotCommand("stop", "Cancel batch process")
    ])
 
    await message.reply("Commands configured successfully")


help_pages = [
    (
        "Bot Commands Overview (1/2):\n\n"
        "1. /add userID\n"
        "Add user to premium (Owner only)\n\n"
        "2. /rem userID\n"
        "Remove user from premium (Owner only)\n\n"
        "3. /transfer userID\n"
        "Transfer premium (Premium members only)\n\n"
        "4. /get\n"
        "Get all user IDs (Owner only)\n\n"
        "5. /lock\n"
        "Lock channel from extraction (Owner only)\n\n"
        "6. /dl link\n"
        "Download videos from supported sites\n\n"
        "7. /login\n"
        "Log into the bot for private channel access\n\n"
        "8. /batch\n"
        "Bulk extraction for posts (After login)\n\n"
    ),
    (
        "Bot Commands Overview (2/2):\n\n"
        "9. /logout\n"
        "Logout from the bot\n\n"
        "10. /stats\n"
        "Get bot stats\n\n"
        "11. /plan\n"
        "Check premium plans\n\n"
        "12. /speedtest\n"
        "Test the server speed\n\n"
        "13. /cancel\n"
        "Cancel ongoing batch process\n\n"
        "14. /myplan\n"
        "Get details about your plans\n\n"
        "15. /session\n"
        "Generate Pyrogram V2 session\n\n"
        "16. /settings\n"
        "Configure bot settings\n\n"
    )
]


async def send_or_edit_help_page(_, message, page_number):
    if page_number < 0 or page_number >= len(help_pages):
        return
 
    prev_button = InlineKeyboardButton("Previous", callback_data=f"help_prev_{page_number}")
    next_button = InlineKeyboardButton("Next", callback_data=f"help_next_{page_number}")
 
    buttons = []
    if page_number > 0:
        buttons.append(prev_button)
    if page_number < len(help_pages) - 1:
        buttons.append(next_button)
 
    keyboard = InlineKeyboardMarkup([buttons])
 
    try:
        await message.delete()
    except:
        pass
 
    await message.reply(
        help_pages[page_number],
        reply_markup=keyboard
    )


@app.on_message(filters.command("help"))
async def help(client, message):
    join = await subscribe(client, message)
    if join == 1:
        return
     
    await send_or_edit_help_page(client, message, 0)


@app.on_callback_query(filters.regex(r"help_(prev|next)_(\d+)"))
async def on_help_navigation(client, callback_query):
    action, page_number = callback_query.data.split("_")[1], int(callback_query.data.split("_")[2])
 
    if action == "prev":
        page_number -= 1
    elif action == "next":
        page_number += 1

    await send_or_edit_help_page(client, callback_query.message, page_number)
    await callback_query.answer()


@app.on_message(filters.command("plan") & filters.private)
async def plan(client, message):
    plan_text = (
        "Premium Price:\n\n"
        "Starting from $2 or 200 INR via Amazon Gift Card\n\n"
        "Download Limit: Up to 100,000 files per batch\n"
        "Batch Modes: /bulk and /batch available\n\n"
    )
     
    buttons = InlineKeyboardMarkup([
        [InlineKeyboardButton("Contact Now", url="https://t.me/anoncracks_bot")]
    ])
    await message.reply_text(plan_text, reply_markup=buttons)


@app.on_callback_query(filters.regex("see_plan"))
async def see_plan(client, callback_query):
    plan_text = (
        "Premium Price:\n\n"
        "Starting from $2 or 200 INR via Amazon Gift Card\n\n"
        "Download Limit: Up to 100,000 files per batch\n"
        "Batch Modes: /bulk and /batch available\n\n"
    )
     
    buttons = InlineKeyboardMarkup([
        [InlineKeyboardButton("Contact Now", url="https://t.me/anoncracks_bot")]
    ])
    await callback_query.message.edit_text(plan_text, reply_markup=buttons)
    await callback_query.answer()
