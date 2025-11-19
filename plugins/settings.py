# User Customization Settings for Downloads

from telethon import events, Button
import re
import os
import string
import random
from shared_client import client as gf
from utils.func import get_user_data_key, save_user_data, users_collection, get_user_data


VIDEO_EXTENSIONS = {
    'mp4', 'mkv', 'avi', 'mov', 'wmv', 'flv', 'webm',
    'mpeg', 'mpg', '3gp', 'ts'
}

active_conversations = {}


@gf.on(events.NewMessage(incoming=True, pattern='/settings'))
async def settings_command(event):
    user_id = event.sender_id
    await send_settings_message(event.chat_id, user_id)


async def send_settings_message(chat_id, user_id, edit_event=None):
    """
    Send or edit settings message
    edit_event: If provided, edits that message instead of sending new one
    """
    # FETCH current user settings
    user_data = await get_user_data(user_id)
    
    # Check what's configured
    has_chat = user_data and user_data.get('chat_id')
    has_rename = user_data and user_data.get('rename_tag')
    has_caption = user_data and user_data.get('caption')
    has_replacement = user_data and user_data.get('replacement_words')
    has_delete = user_data and user_data.get('delete_words')
    has_thumb = os.path.exists(f'{user_id}.jpg')
    has_session = user_data and user_data.get('session_string')
    
    # BUILD status message
    status_lines = ["📊 **CURRENT SETTINGS:**\n"]
    
    if has_rename:
        status_lines.append(f"• Rename Tag: `{user_data.get('rename_tag')}` ✓")
    else:
        status_lines.append("• Rename Tag: Not set")
    
    if has_chat:
        status_lines.append(f"• Upload Chat: `{user_data.get('chat_id')}` ✓")
    else:
        status_lines.append("• Upload Chat: Not set")
    
    if has_caption:
        caption_preview = user_data.get('caption')[:30] + "..." if len(user_data.get('caption', '')) > 30 else user_data.get('caption', '')
        status_lines.append(f"• Caption: `{caption_preview}` ✓")
    else:
        status_lines.append("• Caption: Not set")
    
    if has_delete:
        delete_count = len(user_data.get('delete_words', []))
        status_lines.append(f"• Delete Words: {delete_count} words ✓")
    else:
        status_lines.append("• Delete Words: Not set")
    
    if has_replacement:
        replace_count = len(user_data.get('replacement_words', {}))
        status_lines.append(f"• Replacements: {replace_count} rules ✓")
    else:
        status_lines.append("• Replacements: Not set")
    
    if has_thumb:
        status_lines.append("• Thumbnail: Set ✓")
    else:
        status_lines.append("• Thumbnail: Not set")
    
    if has_session:
        status_lines.append("• Session: Active ✓")
    else:
        status_lines.append("• Session: Not logged in")
    
    status_text = "\n".join(status_lines)
    
    # CREATE buttons with tick marks
    buttons = []
    buttons.append([Button.inline(f'🎯 Set Upload Channel{"  ✓" if has_chat else ""}', b'setchat')])
    buttons.append([Button.inline(f'✏️ Set Rename Tag{"  ✓" if has_rename else ""}', b'setrename')])
    buttons.append([Button.inline(f'💬 Set Custom Caption{"  ✓" if has_caption else ""}', b'setcaption')])
    buttons.append([Button.inline(f'🔄 Replace Words{"  ✓" if has_replacement else ""}', b'setreplacement')])
    buttons.append([Button.inline(f'🗑️ Delete Words{"  ✓" if has_delete else ""}', b'delete')])
    buttons.append([Button.inline(f'🖼️ Set Thumbnail{"  ✓" if has_thumb else ""}', b'setthumb')])
    
    if has_thumb:
        buttons.append([Button.inline('❌ Remove Thumbnail', b'remthumb')])
    
    buttons.append([Button.inline(f'🔑 Add Session{"  ✓" if has_session else ""}', b'addsession')])
    
    if has_session:
        buttons.append([Button.inline('🚪 Logout Session', b'logout')])
    
    buttons.append([Button.inline('📋 View All Settings', b'viewall')])
    buttons.append([Button.inline('♻️ Reset All Settings', b'reset')])
    buttons.append([Button.url('📞 Contact Support', 'https://t.me/anoncracks_bot')])
    
    message_text = (
        "⚙️ **Customize Your Download Settings**\n\n"
        f"{status_text}\n\n"
        "Select an option below to modify:"
    )
    
    # FIXED: Edit existing message or send new one
    if edit_event:
        await edit_event.edit(message_text, buttons=buttons)
    else:
        # Send thumbnail preview if exists
        if has_thumb:
            try:
                await gf.send_file(
                    chat_id,
                    f'{user_id}.jpg',
                    caption=message_text,
                    buttons=buttons
                )
                return
            except:
                pass  # Fallback to text message
        
        await gf.send_message(chat_id, message_text, buttons=buttons)


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
    
    elif event.data == b'viewall':
        # FIXED: Send as message instead of alert (no character limit)
        user_data = await get_user_data(user_id)
        
        view_text = "📋 **ALL SETTINGS DETAILS**\n\n"
        
        # Rename tag
        rename_tag = user_data.get('rename_tag', '') if user_data else ''
        view_text += f"**Rename Tag:**\n`{rename_tag if rename_tag else 'Not set'}`\n\n"
        
        # Chat ID
        chat_id = user_data.get('chat_id', '') if user_data else ''
        view_text += f"**Upload Chat:**\n`{chat_id if chat_id else 'Not set'}`\n\n"
        
        # Caption
        caption = user_data.get('caption', '') if user_data else ''
        view_text += f"**Custom Caption:**\n{caption if caption else 'Not set'}\n\n"
        
        # Delete words
        delete_words = user_data.get('delete_words', []) if user_data else []
        if delete_words:
            view_text += f"**Delete Words:**\n{', '.join(delete_words)}\n\n"
        else:
            view_text += "**Delete Words:**\nNot set\n\n"
        
        # Replacement words
        replacements = user_data.get('replacement_words', {}) if user_data else {}
        if replacements:
            view_text += "**Replacement Rules:**\n"
            for old, new in replacements.items():
                view_text += f"  • '{old}' → '{new}'\n"
            view_text += "\n"
        else:
            view_text += "**Replacement Rules:**\nNot set\n\n"
        
        # Thumbnail
        has_thumb = os.path.exists(f'{user_id}.jpg')
        view_text += f"**Thumbnail:**\n{'Set ✓' if has_thumb else 'Not set'}\n\n"
        
        # Session
        has_session = user_data.get('session_string') if user_data else False
        view_text += f"**Session:**\n{'Active ✓' if has_session else 'Not logged in'}"
        
        # Send as message, not alert
        await event.respond(view_text)
    
    elif event.data == b'logout':
        result = await users_collection.update_one(
            {'user_id': user_id},
            {'$unset': {'session_string': ''}}
        )
        if result.modified_count > 0:
            await event.answer('✅ Session Removed', alert=False)
            # FIXED: Edit same message instead of sending new one
            await send_settings_message(None, user_id, edit_event=event)
        else:
            await event.answer('❌ No Active Session', alert=True)
    
    elif event.data == b'reset':
        # Confirmation dialog
        confirm_buttons = [
            [Button.inline('✅ Yes, Reset All', b'reset_confirm')],
            [Button.inline('❌ Cancel', b'reset_cancel')]
        ]
        await event.edit(
            '⚠️ **Confirm Reset**\n\n'
            'This will delete ALL your settings:\n'
            '• Rename tag\n'
            '• Upload chat\n'
            '• Caption\n'
            '• Delete words\n'
            '• Replacements\n'
            '• Thumbnail\n\n'
            'Are you sure?',
            buttons=confirm_buttons
        )
    
    elif event.data == b'reset_confirm':
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
            
            await event.answer('✅ All Settings Reset', alert=False)
            # FIXED: Edit same message
            await send_settings_message(None, user_id, edit_event=event)
        except Exception as e:
            await event.answer(f'❌ Error: {str(e)[:50]}', alert=True)
    
    elif event.data == b'reset_cancel':
        await event.answer('✅ Cancelled', alert=False)
        # FIXED: Edit same message
        await send_settings_message(None, user_id, edit_event=event)
    
    elif event.data == b'remthumb':
        try:
            os.remove(f'{user_id}.jpg')
            await event.answer('✅ Thumbnail Removed', alert=False)
            # FIXED: Edit same message
            await send_settings_message(None, user_id, edit_event=event)
        except FileNotFoundError:
            await event.answer('❌ No Thumbnail Found', alert=True)


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


@gf.on(events.NewMessage(func=lambda e: e.message.text and not e.message.text.startswith('/')))
async def handle_conversation_input(event):
    user_id = event.sender_id
    if user_id not in active_conversations:
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
        
        if not (chat_id.startswith('-100') or (chat_id.lstrip('-').replace('/', '').isdigit())):
            await event.respond(
                '❌ **Invalid Chat ID Format**\n\n'
                'Please use:\n'
                '• `-1001234567890` (channel)\n'
                '• `-1001234567890/12` (topic)'
            )
            return
        
        await save_user_data(user_id, 'chat_id', chat_id)
        await event.respond(
            '✅ **Upload Channel Set**\n\n'
            f'Files will now be uploaded to: `{chat_id}`\n\n'
            '💡 Use /settings to see updated status'
        )
    except Exception as e:
        await event.respond(f'❌ **Error**\n\n{str(e)[:100]}')


async def handle_setrename(event, user_id):
    rename_tag = event.text.strip()
    
    dangerous_chars = ['/', '\\', '..', '\0']
    for char in dangerous_chars:
        rename_tag = rename_tag.replace(char, '')
    
    await save_user_data(user_id, 'rename_tag', rename_tag)
    await event.respond(
        '✅ **Rename Tag Set**\n\n'
        f'Tag: `{rename_tag}`\n\n'
        f'**Example:** `video.mp4` → `video {rename_tag}.mp4`\n\n'
        '💡 Use /settings to see updated status'
    )


async def handle_setcaption(event, user_id):
    caption = event.text
    await save_user_data(user_id, 'caption', caption)
    await event.respond(
        '✅ **Caption Saved**\n\n'
        'Your custom caption has been set.\n\n'
        '💡 Use /settings to see updated status'
    )


async def handle_setreplacement(event, user_id):
    match = re.match(r"'(.*?)'\s+'(.*?)'", event.text)
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
                f"All occurrences will be replaced.\n\n"
                '💡 Use /settings to see all replacements'
            )


async def handle_addsession(event, user_id):
    session_string = event.text.strip()
    await save_user_data(user_id, 'session_string', session_string)
    await event.respond(
        '✅ **Session Added**\n\n'
        'Your Pyrogram session has been saved securely.\n'
        'You can now access private channels.\n\n'
        '💡 Use /settings to see updated status'
    )


async def handle_deleteword(event, user_id):
    words_to_delete = event.message.text.split()
    delete_words = await get_user_data_key(user_id, 'delete_words', [])
    delete_words = list(set(delete_words + words_to_delete))
    await save_user_data(user_id, 'delete_words', delete_words)
    await event.respond(
        f"✅ **Words Added to Delete List**\n\n"
        f"Words: `{', '.join(words_to_delete)}`\n\n"
        f"These will be removed from filenames.\n\n"
        '💡 Use /settings to see all delete words'
    )


async def handle_setthumb(event, user_id):
    is_photo = event.photo or (event.document and 'image' in (event.document.mime_type or ''))
    
    if is_photo:
        temp_path = await event.download_media()
        try:
            thumb_path = f'{user_id}.jpg'
            if os.path.exists(thumb_path):
                os.remove(thumb_path)
            os.rename(temp_path, thumb_path)
            await event.respond(
                '✅ **Thumbnail Saved**\n\n'
                'Your custom thumbnail is now active.\n\n'
                '💡 Use /settings to see preview'
            )
        except Exception as e:
            await event.respond(f'❌ **Error**\n\n{str(e)[:100]}')
    else:
        await event.respond('❌ **Invalid Input**\n\nPlease send a photo.')


async def rename_file(file, sender, edit):
    try:
        delete_words = await get_user_data_key(sender, 'delete_words', [])
        custom_rename_tag = await get_user_data_key(sender, 'rename_tag', '')
        replacements = await get_user_data_key(sender, 'replacement_words', {})
        
        last_dot_index = str(file).rfind('.')
        if last_dot_index != -1 and last_dot_index != 0:
            ggn_ext = str(file)[last_dot_index + 1:]
            if ggn_ext.isalpha() and len(ggn_ext) <= 9:
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
        
        original_file_name = ' '.join(original_file_name.split())
        
        for word, replace_word in replacements.items():
            original_file_name = original_file_name.replace(word, replace_word)
        
        if custom_rename_tag:
            new_file_name = f'{original_file_name} {custom_rename_tag}.{file_extension}'
        else:
            new_file_name = f'{original_file_name}.{file_extension}'
        
        os.rename(file, new_file_name)
        return new_file_name
    except Exception as e:
        print(f"Rename error: {e}")
        return file
