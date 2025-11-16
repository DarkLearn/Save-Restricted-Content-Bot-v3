# User Customization Settings for Downloads

from telethon import events, Button
import re
import os
import string
import random
from shared_client import client as gf
from config import OWNER_ID
from utils.func import get_user_data_key, save_user_data, users_collection

VIDEO_EXTENSIONS = {
    'mp4', 'mkv', 'avi', 'mov', 'wmv', 'flv', 'webm',
    'mpeg', 'mpg', '3gp'
}

active_conversations = {}


@gf.on(events.NewMessage(incoming=True, pattern='/settings'))
async def settings_command(event):
    user_id = event.sender_id
    await send_settings_message(event.chat_id, user_id)


async def send_settings_message(chat_id, user_id):
    buttons = [
        [Button.inline('🎯 Set Upload Channel', b'setchat')],
        [Button.inline('✏️ Set Rename Tag', b'setrename')],
        [Button.inline('💬 Set Custom Caption', b'setcaption')],
        [Button.inline('🔄 Replace Words', b'setreplacement')],
        [Button.inline('🗑️ Delete Words', b'delete')],
        [Button.inline('🖼️ Set Thumbnail', b'setthumb')],
        [Button.inline('❌ Remove Thumbnail', b'remthumb')],
        [Button.inline('🔑 Add Session', b'addsession')],
        [Button.inline('🚪 Logout Session', b'logout')],
        [Button.inline('♻️ Reset All Settings', b'reset')],
        [Button.url('📞 Contact Support', 'https://t.me/anoncracks_bot')]
    ]
    await gf.send_message(
        chat_id, 
        "⚙️ **Customize Your Download Settings**\n\n"
        "Configure how your files will be processed and uploaded.\n\n"
        "Select an option below:",
        buttons=buttons
    )


@gf.on(events.CallbackQuery)
async def callback_query_handler(event):
    user_id = event.sender_id
    
    callback_actions = {
        b'setchat': {
            'type': 'setchat',
            'message': """🎯 **Set Upload Channel**

Send me the chat ID (with -100 prefix):

📝 **Examples:**
• Normal channel: `-1001234567890`
• Topic group: `-1001234567890/12`

⚠️ **Important:**
Your bot must be admin in that channel!

Type /cancel to abort"""
        },
        b'setrename': {
            'type': 'setrename',
            'message': """✏️ **Set Rename Tag**

Send the text you want to add to filenames.

📝 **Example:** `@MyChannel`

**Result:** `video.mp4` → `video @MyChannel.mp4`

Type /cancel to abort"""
        },
        b'setcaption': {
            'type': 'setcaption',
            'message': """💬 **Set Custom Caption**

Send the caption you want for all uploads.

📝 You can use markdown formatting.

Type /cancel to abort"""
        },
        b'setreplacement': {
            'type': 'setreplacement',
            'message': """🔄 **Replace Words**

**Format:** `'OLD' 'NEW'`

📝 **Example:** `'old-word' 'new-word'`

**Result:** All occurrences will be replaced.

Type /cancel to abort"""
        },
        b'addsession': {
            'type': 'addsession',
            'message': """🔑 **Add Pyrogram Session**

Send your Pyrogram V2 session string.

⚠️ **Keep it private!**

Type /cancel to abort"""
        },
        b'delete': {
            'type': 'deleteword',
            'message': """🗑️ **Delete Words**

Send words separated by spaces.

📝 **Example:** `spam ads unwanted`

These words will be removed from filenames.

Type /cancel to abort"""
        },
        b'setthumb': {
            'type': 'setthumb',
            'message': """🖼️ **Set Custom Thumbnail**

Send a photo to use as thumbnail for videos.

📌 Best size: 320x320 pixels

Type /cancel to abort"""
        }
    }
    
    if event.data in callback_actions:
        action = callback_actions[event.data]
        await start_conversation(event, user_id, action['type'], action['message'])
    
    elif event.data == b'logout':
        result = await users_collection.update_one(
            {'user_id': user_id},
            {'$unset': {'session_string': ''}}
        )
        if result.modified_count > 0:
            await event.respond('✅ **Session Removed**\n\nYou have been logged out successfully.')
        else:
            await event.respond('❌ **No Active Session**\n\nYou are not logged in.')
    
    elif event.data == b'reset':
        try:
            await users_collection.update_one(
                {'user_id': user_id},
                {'$unset': {
                    'delete_words': '',
                    'replacement_words': '',
                    'rename_tag': '',
                    'caption': '',
                    'chat_id': ''
                }}
            )
            thumbnail_path = f'{user_id}.jpg'
            if os.path.exists(thumbnail_path):
                os.remove(thumbnail_path)
            await event.respond(
                '✅ **Settings Reset**\n\n'
                'All customization settings have been cleared.\n'
                'Use /settings to configure again.'
            )
        except Exception as e:
            await event.respond(f'❌ **Error**\n\n{str(e)[:100]}')
    
    elif event.data == b'remthumb':
        try:
            os.remove(f'{user_id}.jpg')
            await event.respond('✅ **Thumbnail Removed**\n\nCustom thumbnail deleted successfully.')
        except FileNotFoundError:
            await event.respond('❌ **No Thumbnail Found**\n\nYou haven\'t set a thumbnail yet.')


async def start_conversation(event, user_id, conv_type, prompt_message):
    if user_id in active_conversations:
        await event.respond('⚠️ Previous conversation cancelled. Starting new one.')
    
    msg = await event.respond(prompt_message)
    active_conversations[user_id] = {'type': conv_type, 'message_id': msg.id}


@gf.on(events.NewMessage(pattern='/cancel'))
async def cancel_conversation(event):
    user_id = event.sender_id
    if user_id in active_conversations:
        await event.respond('✅ **Operation Cancelled**\n\nNo changes were made.')
        del active_conversations[user_id]


@gf.on(events.NewMessage())
async def handle_conversation_input(event):
    user_id = event.sender_id
    if user_id not in active_conversations or event.message.text.startswith('/'):
        return
        
    conv_type = active_conversations[user_id]['type']
    
    handlers = {
        'setchat': handle_setchat,
        'setrename': handle_setrename,
        'setcaption': handle_setcaption,
        'setreplacement': handle_setreplacement,
        'addsession': handle_addsession,
        'deleteword': handle_deleteword,
        'setthumb': handle_setthumb
    }
    
    if conv_type in handlers:
        await handlers[conv_type](event, user_id)
    
    if user_id in active_conversations:
        del active_conversations[user_id]


async def handle_setchat(event, user_id):
    try:
        chat_id = event.text.strip()
        await save_user_data(user_id, 'chat_id', chat_id)
        await event.respond(
            '✅ **Upload Channel Set**\n\n'
            f'Files will now be uploaded to: `{chat_id}`'
        )
    except Exception as e:
        await event.respond(f'❌ **Error**\n\n{str(e)[:100]}')


async def handle_setrename(event, user_id):
    rename_tag = event.text.strip()
    await save_user_data(user_id, 'rename_tag', rename_tag)
    await event.respond(
        '✅ **Rename Tag Set**\n\n'
        f'Tag: `{rename_tag}`\n\n'
        '**Example:** `video.mp4` → `video {rename_tag}.mp4`'
    )


async def handle_setcaption(event, user_id):
    caption = event.text
    await save_user_data(user_id, 'caption', caption)
    await event.respond('✅ **Caption Saved**\n\nYour custom caption has been set.')


async def handle_setreplacement(event, user_id):
    match = re.match("'(.+)' '(.+)'", event.text)
    if not match:
        await event.respond(
            "❌ **Invalid Format**\n\n"
            "**Correct format:** `'OLD' 'NEW'`\n"
            "**Example:** `'old-word' 'new-word'`"
        )
    else:
        word, replace_word = match.groups()
        delete_words = await get_user_data_key(user_id, 'delete_words', [])
        if word in delete_words:
            await event.respond(
                f"❌ **Conflict Detected**\n\n"
                f"The word `{word}` is in your delete list.\n"
                f"Remove it from delete list first."
            )
        else:
            replacements = await get_user_data_key(user_id, 'replacement_words', {})
            replacements[word] = replace_word
            await save_user_data(user_id, 'replacement_words', replacements)
            await event.respond(
                f"✅ **Replacement Saved**\n\n"
                f"`{word}` → `{replace_word}`\n\n"
                f"All occurrences will be replaced."
            )


async def handle_addsession(event, user_id):
    session_string = event.text.strip()
    await save_user_data(user_id, 'session_string', session_string)
    await event.respond(
        '✅ **Session Added**\n\n'
        'Your Pyrogram session has been saved securely.\n'
        'You can now access private channels.'
    )


async def handle_deleteword(event, user_id):
    words_to_delete = event.message.text.split()
    delete_words = await get_user_data_key(user_id, 'delete_words', [])
    delete_words = list(set(delete_words + words_to_delete))
    await save_user_data(user_id, 'delete_words', delete_words)
    await event.respond(
        f"✅ **Words Added to Delete List**\n\n"
        f"Words: `{', '.join(words_to_delete)}`\n\n"
        f"These will be removed from filenames."
    )


async def handle_setthumb(event, user_id):
    if event.photo:
        temp_path = await event.download_media()
        try:
            thumb_path = f'{user_id}.jpg'
            if os.path.exists(thumb_path):
                os.remove(thumb_path)
            os.rename(temp_path, thumb_path)
            await event.respond('✅ **Thumbnail Saved**\n\nYour custom thumbnail is now active.')
        except Exception as e:
            await event.respond(f'❌ **Error**\n\n{str(e)[:100]}')
    else:
        await event.respond('❌ **Invalid Input**\n\nPlease send a photo.')


def generate_random_name(length=7):
    characters = string.ascii_letters + string.digits
    return ''.join(random.choice(characters) for _ in range(length))


async def rename_file(file, sender, edit):
    try:
        delete_words = await get_user_data_key(sender, 'delete_words', [])
        custom_rename_tag = await get_user_data_key(sender, 'rename_tag', '')
        replacements = await get_user_data_key(sender, 'replacement_words', {})
        
        last_dot_index = str(file).rfind('.')
        if last_dot_index != -1 and last_dot_index != 0:
            ggn_ext = str(file)[last_dot_index + 1:]
            if ggn_ext.isalpha() and len(ggn_ext) <= 9:
                if ggn_ext.lower() in VIDEO_EXTENSIONS:
                    original_file_name = str(file)[:last_dot_index]
                    file_extension = 'mp4'
                else:
                    original_file_name = str(file)[:last_dot_index]
                    file_extension = ggn_ext
            else:
                original_file_name = str(file)[:last_dot_index]
                file_extension = 'mp4'
        else:
            original_file_name = str(file)
            file_extension = 'mp4'
        
        for word in delete_words:
            original_file_name = original_file_name.replace(word, '')
        
        for word, replace_word in replacements.items():
            original_file_name = original_file_name.replace(word, replace_word)
        
        new_file_name = f'{original_file_name} {custom_rename_tag}.{file_extension}'
        
        os.rename(file, new_file_name)
        return new_file_name
    except Exception as e:
        print(f"Rename error: {e}")
        return file
