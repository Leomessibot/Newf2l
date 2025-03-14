import os
import asyncio
import requests
import string
import random
from pyrogram import enums 
from shortzy import Shortzy
from asyncio import TimeoutError
from biisal.bot import StreamBot
from biisal.utils.database import Database
from biisal.utils.human_readable import humanbytes
from biisal.vars import Var
from urllib.parse import quote_plus
from pyrogram import filters, Client
from pyrogram.errors import FloodWait, UserNotParticipant
from pyrogram.enums import ChatMemberStatus
from pyrogram.types import Message, InlineKeyboardMarkup, InlineKeyboardButton, WebAppInfo, CallbackQuery

from biisal.utils.file_properties import get_name, get_hash, get_media_file_size
db = Database(Var.DATABASE_URL, Var.name)


def generate_random_alphanumeric(): 
    """Generate a random 8-letter alphanumeric string.""" 
    characters = string.ascii_letters + string.digits 
    random_chars = ''.join(random.choice(characters) for _ in range(8)) 
    return random_chars 

def get_shortlink(url): 
    rget = requests.get(f"https://{Var.SHORTLINK_URL}/api?api={Var.SHORTLINK_API}&url={url}&alias={generate_random_alphanumeric()}") 
    rjson = rget.json() 
    if rjson["status"] == "success" or rget.status_code == 200: 
        return rjson["shortenedUrl"] 
    else: 
        return url

MY_PASS = os.environ.get("MY_PASS", None)
pass_dict = {}
pass_db = Database(Var.DATABASE_URL, "ag_passwords")

msg_text ="""
<b>ʏᴏᴜʀ ʟɪɴᴋ ɪs ɢᴇɴᴇʀᴀᴛᴇᴅ...⚡</b>

<b>📧 ꜰɪʟᴇ ɴᴀᴍᴇ :- </b> <i>{}</i>

<b>📦 ꜰɪʟᴇ sɪᴢᴇ :- </b> <i>{}</i>

<b>⚠️ ᴛʜɪꜱ ʟɪɴᴋ ᴡɪʟʟ ᴇxᴘɪʀᴇ ᴀꜰᴛᴇʀ 𝟼 ʜᴏᴜʀꜱ</b>

<b>❇️ ʙʏ : @NxBots_TG</b>"""

@StreamBot.on_message((filters.private) & (filters.document | filters.video | filters.audio | filters.photo) , group=4)
async def private_receive_handler(c: Client, m: Message):
    if not await db.is_user_exist(m.from_user.id):
        await db.add_user(m.from_user.id)
        await c.send_message(
            Var.NEW_USER_LOG,
            f"#𝐍𝐞𝐰𝐔𝐬𝐞𝐫\n\n**᚛› 𝐍𝐚𝐦𝐞 - [{m.from_user.first_name}](tg://user?id={m.from_user.id})**"
        )
    if Var.UPDATES_CHANNEL != "None":
        try:
            user = await c.get_chat_member(Var.UPDATES_CHANNEL, m.chat.id)
            if user.status == "kicked":
                await c.send_message(
                    chat_id=m.chat.id,
                    text="You are banned!\n\n  Contact Developer [LeoTG](https://telegram.me/LeoTGx_7) he will help you.",
                    disable_web_page_preview=True
                )
                return 
        except UserNotParticipant:
            await c.send_photo(
                chat_id=m.chat.id,
                photo="https://graph.org/file/a8095ab3c9202607e78ad.jpg",
                caption="""<b>ᴊᴏɪɴ ᴏᴜʀ ᴜᴘᴅᴀᴛᴇs ᴄʜᴀɴɴᴇʟ ᴛᴏ ᴜꜱᴇ ᴍᴇ</b>""",
                reply_markup=InlineKeyboardMarkup(
                    [
                        [
                            InlineKeyboardButton("ᴊᴏɪɴ ɴᴏᴡ 🚩", url=f"https://telegram.me/{Var.UPDATES_CHANNEL}")
                        ]
                    ]
                ),
            )
            return
        except Exception as e:
            await m.reply_text(e)
            await c.send_message(
                chat_id=m.chat.id,
                text="sᴏᴍᴇᴛʜɪɴɢ ᴡᴇɴᴛ ᴡʀᴏɴɢ. ᴄᴏɴᴛᴀᴄᴛ ᴍʏ [ʙᴏss](https://t.me/NxBots_TG)",
                disable_web_page_preview=True
            )
            return
    ban_chk = await db.is_banned(int(m.from_user.id))
    if ban_chk == True:
        return await m.reply(Var.BAN_ALERT)

    try:  # This is the outer try block
        log_msg = await m.copy(chat_id=Var.BIN_CHANNEL)
        stream_link = f"{Var.URL}watch/{str(log_msg.id)}?hash={get_hash(log_msg)}"
        online_link = f"{Var.URL}{str(log_msg.id)}?hash={get_hash(log_msg)}"
        try:  # This is the inner try block
            if Var.SHORTLINK:
                stream = get_shortlink(stream_link)
                download = get_shortlink(online_link)
            else:
                stream = stream_link
                download = online_link
        except Exception as e:
            print(f"An error occurred: {e}")

        a = await log_msg.reply_text(
            text=f"ʀᴇǫᴜᴇꜱᴛᴇᴅ ʙʏ : [{m.from_user.first_name}](tg://user?id={m.from_user.id})\nUꜱᴇʀ ɪᴅ : {m.from_user.id}\nStream ʟɪɴᴋ : {stream_link}",
            disable_web_page_preview=True, quote=True
        )
        k = await m.reply_text(
            text=msg_text.format(get_name(log_msg), humanbytes(get_media_file_size(m))),
            quote=True,
            reply_markup=InlineKeyboardMarkup([
                [InlineKeyboardButton("• ꜱᴛʀᴇᴀᴍ •", url=stream),
                 InlineKeyboardButton("• ᴅᴏᴡɴʟᴏᴀᴅ •", url=download)],
                [InlineKeyboardButton('🧿 ᴡᴀᴛᴄʜ ᴏɴ ᴛᴇʟᴇɢʀᴀᴍ 🖥', web_app=WebAppInfo(url=stream))]
            ])
        )

        # Wait for 6 hours (21600 seconds)
        await asyncio.sleep(21600)  # Sleep for 6 hours

        # After 6 hours, delete `log_msg`, `a`, and `k`
        try:
            await log_msg.delete()
            await a.delete()
            await k.delete()
        except Exception as e:
            print(f"Error during deletion: {e}")

    except FloodWait as e:
        print(f"Sleeping for {str(e.x)}s")
        await asyncio.sleep(e.x)
        await c.send_message(chat_id=Var.BIN_CHANNEL, text=f"Gᴏᴛ FʟᴏᴏᴅWᴀɪᴛ ᴏғ {str(e.x)}s from [{m.from_user.first_name}](tg://user?id={m.from_user.id})\n\n**𝚄𝚜𝚎𝚛 𝙸𝙳 :** `{str(m.from_user.id)}`", disable_web_page_preview=True)

@StreamBot.on_callback_query(filters.regex("view_channels"))
async def view_channels_callback(client, callback_query: CallbackQuery):
    user_id = callback_query.from_user.id

    channels = await db.channels.find({'user_id': user_id}).to_list(length=5)

    if channels:
        
        buttons = [
            [InlineKeyboardButton(f"📱 {channel['title']}", callback_data=f"channel_settings_{channel['channel_id']}")]
            for channel in channels
        ]
        
        if len(channels) < 5:
            buttons.append([InlineKeyboardButton("➕ Add New Channel", callback_data="add_channel")])

        await callback_query.message.edit_text(
            "📋 **Your Channels**:\n\nClick a channel to view settings.",
            reply_markup=InlineKeyboardMarkup(buttons)
        )
    else:
        buttons = [
            [InlineKeyboardButton("No channel added yet.", callback_data="none")],
            [InlineKeyboardButton("➕ Add New Channel", callback_data="add_channel")]
        ]
        
        await callback_query.message.edit_text(
            "📋 **Your Channels**:\n\nYou haven't added any channel yet. Please add a channel.",
            reply_markup=InlineKeyboardMarkup(buttons)
        )


@StreamBot.on_callback_query(filters.regex(r"channel_settings_(\-?\d+)"))
async def channel_settings_callback(client, callback_query: CallbackQuery):
    user_id = callback_query.from_user.id
    channel_id = int(callback_query.data.split("_")[-1])  # Extract channel ID

    
    channel = await db.channels.find_one({'user_id': user_id, 'channel_id': channel_id})

    if not channel:
        await callback_query.message.edit_text("❌ Channel not found!")
        return

    settings_buttons = [
        [InlineKeyboardButton("✨️ Set Caption ✨️", callback_data=f"settings_caption_{channel_id}"),
         InlineKeyboardButton("❌ Remove Channel", callback_data=f"remove_channel_{channel_id}")],
        [InlineKeyboardButton("🪩 Shortener Settings 🪩", callback_data=f"set_shortener_{channel_id}")],
        [InlineKeyboardButton("🔙 Back to Channels", callback_data="view_channels")]
    ]

    await callback_query.message.edit_text(
        f"<b>🔧 Settings for {channel['title']}:\n\nChoose an option:</b>",
        reply_markup=InlineKeyboardMarkup(settings_buttons)
    )

@StreamBot.on_callback_query(filters.regex(r"remove_channel_(\-?\d+)"))
async def remove_channel_callback(client, callback_query: CallbackQuery):
    user_id = callback_query.from_user.id
    channel_id = int(callback_query.data.split("_")[-1])  

    
    result = await db.channels.delete_one({'user_id': user_id, 'channel_id': channel_id})

    if result.deleted_count > 0:
        await callback_query.message.edit_text(
            "✅ Channel removed successfully!",
            reply_markup=InlineKeyboardMarkup([[InlineKeyboardButton("🔙 Back", callback_data="view_channels")]])
        )
    else:
        await callback_query.message.edit_text("❌ Failed to remove channel.")

@StreamBot.on_callback_query(filters.regex("set_custom_caption_(\-?\d+)"))
async def set_custom_caption(client, callback_query: CallbackQuery):
    user_id = callback_query.from_user.id
    channel_id = int(callback_query.data.split("_")[-1])  # Extract channel ID

    # Fetch channel from database
    channel = await db.channels.find_one({'user_id': user_id, 'channel_id': channel_id})

    if not channel:
        await callback_query.message.edit_text("❌ Channel not found!")
        return

    msg = await callback_query.message.edit_text(
        "📝 **Send me the new custom caption format.**\n\n"
        "You can use these Format:\n"
        "- `{file_name}` → File name\n"
        "- `{previouscaption}` → Previous caption\n"
        "- `{file_size}` → File size\n"
        "- `{watch_link}` → Streaming link\n"
        "- `{download_link}` → Download link\n\n"
        "🚫 Type /cancel to stop."
    )

    try:
        response = await client.listen(callback_query.from_user.id, timeout=1000)

        if response.text == "/cancel":
            await msg.delete()
            await response.reply_text(
                "🚫 Process cancelled.", 
                reply_markup=InlineKeyboardMarkup([[InlineKeyboardButton("🔙 Back", callback_data="view_channels")]])
            )
            return

        # Update caption in database
        await db.channels.update_one({'user_id': user_id, 'channel_id': channel_id}, {'$set': {'custom_caption': response.text}})
        
        await msg.delete()
        await response.delete()

        await response.reply_text(
            f"<b>✅ Custom caption updated successfully!</b>",
            reply_markup=InlineKeyboardMarkup([[InlineKeyboardButton("🔙 Back", callback_data="view_channels")]])
        )       

    except asyncio.TimeoutError:
        await msg.edit_text("⏳ **Time expired!** Click 'Set Custom Caption' again.")


@StreamBot.on_callback_query(filters.regex("add_channel"))
async def add_channel_callback(client, callback_query: CallbackQuery):
    user_id = callback_query.from_user.id  # Get user ID
    
    
    channel_count = await db.channels.count_documents({'user_id': user_id})
    
    if channel_count >= 5:
        await callback_query.answer("🚫 You can only add up to 5 channels.", show_alert=True)
        return

    msg = await callback_query.message.edit_text(
        "<b>📢 Forward a message from your channel within 60 seconds.</b>\n"
        "<b>This will allow me to generate links in that channel.</b>\n\n"
        "🚫 Type /cancel to stop.",
        parse_mode=enums.ParseMode.HTML
    )

    try:
        response = await client.listen(callback_query.from_user.id, timeout=1000)

        if response.text == "/cancel":
            await msg.delete()
            await response.reply_text(
                "🚫 Process cancelled.", 
                reply_markup=InlineKeyboardMarkup([[InlineKeyboardButton("🔙 Back", callback_data="view_channels")]])
            )
            return

        if not response.forward_from_chat:
            await response.reply_text("❌ This is not a forwarded message from a channel. Try again.")
            return

        channel_id = response.forward_from_chat.id
        channel_title = response.forward_from_chat.title

        # Check if bot is an admin in the channel
        try:
            bot_member = await client.get_chat_member(channel_id, "me")

            if bot_member.status not in [ChatMemberStatus.ADMINISTRATOR, ChatMemberStatus.OWNER]:
                await response.reply_text(
                    f"❌ I am **not an admin** in **{channel_title}**.\n"
                    "Please **add me as an admin** and try again."
                )
                return
        except Exception as e:
            await response.reply_text(f"❌ Error checking admin status: {str(e)}")
            return

        await db.channels.insert_one({'user_id': user_id, 'title': channel_title, 'channel_id': channel_id})

        await msg.delete()
        await response.delete()

        await response.reply_text(
            f"<b>✅ {channel_title}** has been added!</b>",
            reply_markup=InlineKeyboardMarkup([[InlineKeyboardButton("🔙 Back", callback_data="view_channels")]])
        )       

    except asyncio.TimeoutError:
        await msg.edit_text("⏳ Time expired! Please click 'Add New Channel' again.")

@StreamBot.on_callback_query(filters.regex(r"settings_caption_(\-?\d+)"))
async def set_custom_caption(client, callback_query: CallbackQuery):
    user_id = callback_query.from_user.id
    channel_id = int(callback_query.data.split("_")[-1])

    channel = await db.channels.find_one({'user_id': user_id, 'channel_id': channel_id})

    if not channel:
        await callback_query.message.edit_text("❌ Channel not found!")
        return

    current_caption = channel.get("custom_caption", "No caption set yet.")

    buttons = [
        [InlineKeyboardButton("✨️ Add Caption ✨️", callback_data=f"set_custom_caption_{channel_id}")],
        [InlineKeyboardButton("🚫 Remove Caption 🚫", callback_data=f"delete_caption_{channel_id}")],
        [InlineKeyboardButton("🔙 Back", callback_data=f"channel_settings_{channel_id}")]
    ]

    await callback_query.message.edit_text(
        f"<b>📂 Current Caption:</b>\n\n<code>{current_caption}</code>\n\nChoose an option:",
        reply_markup=InlineKeyboardMarkup(buttons),
        parse_mode=enums.ParseMode.HTML
    )

@StreamBot.on_callback_query(filters.regex(r"delete_caption_(\-?\d+)"))
async def delete_caption(client, callback_query: CallbackQuery):
    user_id = callback_query.from_user.id
    channel_id = int(callback_query.data.split("_")[-1])

    channel = await db.channels.find_one({'user_id': user_id, 'channel_id': channel_id})

    if not channel or "custom_caption" not in channel:
        # No caption exists, show a message instead
        await callback_query.answer("⚠️ Add a caption first 😏!", show_alert=True)
        return

    # Remove the caption from the database
    await db.channels.update_one(
        {'user_id': user_id, 'channel_id': channel_id},
        {"$unset": {"custom_caption": ""}}  
    )

    await callback_query.message.edit_text(
        "✅ Caption removed successfully!",
        reply_markup=InlineKeyboardMarkup([[InlineKeyboardButton("🔙 Back", callback_data=f"channel_settings_{channel_id}")]])
    )

@StreamBot.on_callback_query(filters.regex(r"set_shortener_(\-?\d+)"))
async def set_shortener_callback(client, callback_query: CallbackQuery):
    user_id = callback_query.from_user.id
    channel_id = int(callback_query.data.split("_")[-1])  # Extract channel ID

    channel = await db.channels.find_one({'user_id': user_id, 'channel_id': channel_id})

    if not channel:
        return await callback_query.message.edit_text("❌ Channel not found!")

    shortener_status = "✅️ Enabled" if channel.get("shortener_enabled", False) else "❌️ Disabled"

    shortener_buttons = [
        [InlineKeyboardButton(f"🔗 Shortener : {shortener_status}", callback_data=f"onoff_shortener_{channel_id}")],
        [InlineKeyboardButton("🪩 Set Shortener 🪩", callback_data=f"add_shortener_{channel_id}"),
         InlineKeyboardButton("❌ Remove Shortener", callback_data=f"remove_shortener_{channel_id}")],
        [InlineKeyboardButton("🔙 Back to Settings", callback_data=f"channel_settings_{channel_id}")]
    ]

    await callback_query.message.edit_text(
        f"<b>🔗 Shortener Settings for {channel['title']}</b>\n\n"
        f"Shortener Status: {shortener_status}\n\n"
        "Choose an option below:",
        parse_mode=enums.ParseMode.HTML,
        reply_markup=InlineKeyboardMarkup(shortener_buttons)
    )

@StreamBot.on_callback_query(filters.regex(r"remove_shortener_(\-?\d+)"))
async def remove_shortener(client, callback_query: CallbackQuery):
    channel_id = int(callback_query.data.split("_")[-1])
    channel = await db.channels.find_one({'channel_id': channel_id})

    if not channel or not channel.get("shortlink_url") or not channel.get("shortlink_api"):
        return await callback_query.answer("❌ Add a shortener first 😏!", show_alert=True)


    await db.channels.update_one(
        {'channel_id': channel_id},
        {'$unset': {'shortlink_url': "", 'shortlink_api': "", 'shortener_enabled': ""}}
    )

    await callback_query.message.edit_text(
        "✅ Shortener removed successfully!",
        reply_markup=InlineKeyboardMarkup([[InlineKeyboardButton("🔙 Back", callback_data=f"set_shortener_{channel_id}")]])
    )

@StreamBot.on_callback_query(filters.regex(r"onoff_shortener_(\-?\d+)"))
async def onoff_shortener(client, callback_query: CallbackQuery):
    channel_id = int(callback_query.data.split("_")[-1])
    channel = await db.channels.find_one({'channel_id': channel_id})

    if not channel or not channel.get("shortlink_url") or not channel.get("shortlink_api"):
        return await callback_query.answer("❌ Add a shortener first!", show_alert=True)

    new_status = not channel.get("shortener_enabled", False)

    await db.channels.update_one(
        {'channel_id': channel_id},
        {'$set': {'shortener_enabled': new_status}}
    )

    shortener_status = "✅️ Enabled" if new_status else "❌️ Disabled"

    caption = (
        f"<b>🔗 Shortener Settings for {channel['title']}</b>\n\n"
        f"Shortener Status: {shortener_status}\n\n"
        "Choose an option below:"
    )

    
    buttons = [
        [InlineKeyboardButton(f"🔗 Shortener : {shortener_status}", callback_data=f"onoff_shortener_{channel_id}")],
        [InlineKeyboardButton("🪩 Set Shortener 🪩", callback_data=f"add_shortener_{channel_id}"),
         InlineKeyboardButton("❌ Remove Shortener", callback_data=f"remove_shortener_{channel_id}")],
        [InlineKeyboardButton("🔙 Back to Settings", callback_data=f"channel_settings_{channel_id}")]
    ]
    await callback_query.message.edit_text(
        caption,
        parse_mode=enums.ParseMode.HTML,
        reply_markup=InlineKeyboardMarkup(buttons)
    )

    await callback_query.answer(f"Shortener is now {shortener_status}!", show_alert=True)


@StreamBot.on_callback_query(filters.regex(r"add_shortener_(\-?\d+)"))
async def shortlink_settings(client, callback_query: CallbackQuery):
    user_id = callback_query.from_user.id
    channel_id = int(callback_query.data.split("_")[-1])

    # Ask for shortlink domain
    msg = await callback_query.message.edit_text(
        "<b>🔗 Send me your shortlink site domain (without 'https://')</b>",
        parse_mode=enums.ParseMode.HTML
    )

    try:
        url_response = await client.listen(user_id, timeout=60)
        if url_response.text.lower() == "/cancel":
            await msg.delete()
            return await url_response.reply_text(
                "🚫 Process cancelled.",
                reply_markup=InlineKeyboardMarkup([[InlineKeyboardButton("🔙 Back", callback_data=f"set_shortener_{channel_id}")]])
            )
        
        shortlink_url = url_response.text.strip()
        await url_response.delete()
        
        # Ask for API key
        msg2 = await client.send_message(
            user_id,
            "<b>🔑 Now send your API key</b>",
            parse_mode=enums.ParseMode.HTML
        )
        
        api_response = await client.listen(user_id, timeout=60)
        if api_response.text.lower() == "/cancel":
            await msg2.delete()
            return await api_response.reply_text(
                "🚫 Process cancelled.",
                reply_markup=InlineKeyboardMarkup([[InlineKeyboardButton("🔙 Back", callback_data=f"set_shortener_{channel_id}")]])
            )
        
        api_key = api_response.text.strip()
        await api_response.delete()
        
        # Validate API with a test conversion
        try:
            shortzy = Shortzy(api_key=api_key, base_site=shortlink_url)
            test_link = "https://t.me/NxBots_TG"
            await shortzy.convert(test_link)
        except Exception as e:
            return await client.send_message(
                user_id,
                f"❌ Error in converting link:\n\n<code>{e}</code>\n\nTry again by selecting settings.",
                parse_mode=enums.ParseMode.HTML,
                reply_markup=InlineKeyboardMarkup([[InlineKeyboardButton("🔙 Back", callback_data=f"set_shortener_{channel_id}")]])
            )

        # Save data to the database
        await db.channels.update_one(
            {'user_id': user_id, 'channel_id': channel_id},
            {"$set": {"shortlink_url": shortlink_url, "shortlink_api": api_key}}
        )

        # Confirm with the user
        await client.send_message(
            user_id,
            f"<b>✅ Shortened URL settings saved!**\n\nShortlink: {shortlink_url}</b>",
            parse_mode=enums.ParseMode.HTML,
            reply_markup=InlineKeyboardMarkup([[InlineKeyboardButton("🔙 Back", callback_data=f"set_shortener_{channel_id}")]])
        )

    except asyncio.TimeoutError:
        await msg.delete()
        await callback_query.message.edit_text(
            "⏳ **Time expired!** Please try again by selecting settings.",
            reply_markup=InlineKeyboardMarkup([[InlineKeyboardButton("🔙 Back", callback_data=f"set_shortener_{channel_id}")]])
        )


@StreamBot.on_callback_query(filters.regex(r"remove_channel_(\-?\d+)"))
async def remove_channel_callback(client, callback_query: CallbackQuery):
    user_id = callback_query.from_user.id
    channel_id = int(callback_query.data.split("_")[-1])  

    
    result = await db.channels.delete_one({'user_id': user_id, 'channel_id': channel_id})

    if result.deleted_count > 0:
        await callback_query.message.edit_text(
            "✅ Channel removed successfully!",
            reply_markup=InlineKeyboardMarkup([[InlineKeyboardButton("🔙 Back", callback_data="view_channels")]])
        )
    else:
        await callback_query.message.edit_text("❌ Failed to remove channel.")

@StreamBot.on_message(
    filters.channel   
    & (filters.document | filters.video | filters.photo)  
    & ~filters.forwarded,  
    group=-1
)
async def channel_receive_handler(bot, broadcast):
    channel = await db.channels.find_one({'channel_id': int(broadcast.chat.id)})

    if not channel:
        return  

    if int(broadcast.chat.id) in Var.BAN_CHNL:
        print("🚫 Banned channel detected. Ignoring request.")
        return

    ban_chk = await db.is_banned(int(broadcast.chat.id))
    if (int(broadcast.chat.id) in Var.BANNED_CHANNELS) or (ban_chk is True):
        await bot.leave_chat(broadcast.chat.id)
        return

    try:
        # Forward message to BIN_CHANNEL for logging
        log_msg = await broadcast.forward(chat_id=Var.BIN_CHANNEL)
        stream_link = f"{Var.URL}watch/{str(log_msg.id)}?hash={get_hash(log_msg)}"
        download_link = f"{Var.URL}{str(log_msg.id)}?hash={get_hash(log_msg)}"

        # Fetch shortlink settings from DB (if set)
        shortlink_domain = channel.get("shortlink_url")
        shortlink_api = channel.get("shortlink_api")

        if shortlink_domain and shortlink_api:
            try:
                stream_link = await get_shortlink(stream_link, shortlink_domain, shortlink_api)
                download_link = await get_shortlink(download_link, shortlink_domain, shortlink_api)
            except Exception as e:
                print(f"⚠️ URL Shortener Error: {e}")

        # Get custom caption from DB, use default if not set
        custom_caption = channel.get("custom_caption", "**{previous_caption}**")

        # Extract file details
        file_name = broadcast.document.file_name if broadcast.document else "Unknown File"
        file_size = f"{broadcast.document.file_size / 1024 / 1024:.2f} MB" if broadcast.document else "Unknown Size"
        previous_caption = broadcast.caption if broadcast.caption else file_name

        # Format caption with actual values
        formatted_caption = custom_caption.format(
            file_name=file_name,
            previouscaption=previous_caption,
            file_size=file_size,
            watch_link=stream_link,
            download_link=download_link
        )

        # **Edit the message in the channel to include the caption & buttons**
        await bot.edit_message_caption(
            chat_id=broadcast.chat.id,
            message_id=broadcast.id,
            caption=formatted_caption,
            reply_markup=InlineKeyboardMarkup([
                [InlineKeyboardButton("🎬 Watch", url=stream_link),
                 InlineKeyboardButton("⬇️ Download", url=download_link)]
            ])
        )

    except FloodWait as w:
        print(f"Sleeping for {str(w.x)}s")
        await asyncio.sleep(w.x)
        await bot.send_message(chat_id=Var.BIN_CHANNEL,
                               text=f"⚠️ FloodWait: {str(w.x)}s from {broadcast.chat.title}\n**CHANNEL ID:** `{str(broadcast.chat.id)}`",
                               disable_web_page_preview=True)

    except Exception as e:
        await bot.send_message(chat_id=Var.BIN_CHANNEL, text=f"❌ **#ERROR:** `{e}`", disable_web_page_preview=True)
        print(f"❌ Error: {e}")


async def get_shortlink(original_url, shortlink_domain, shortlink_api):
    """Converts a given URL using the shortlink API."""
    shortzy = Shortzy(api_key=shortlink_api, base_site=shortlink_domain)
    short_url = await shortzy.convert(original_url)
    return short_url
