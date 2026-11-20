from pyrogram import  Client, filters
from pyrogram.types import Message
from bot import Bot 
from config import OWNER_ID 






@Client.on_message(filters.command("rss") & filters.user(OWNER_ID))
async def setthings(client: Client, message: Message):
    if len(message.command) < 2:
        return await message.reply("Usage: /rss on | off | status")
    
    action = message.command[1].lower()

    if action == "on":
        client.rss_enabled = True
        await message.reply("RSS monitoring enabled.")
    elif action == "off":
        client.rss_enabled = False
        await message.reply("RSS monitoring disabled.")
    elif action == "status":
        status = "ON 🟢" if client.rss_enabled else "OFF 🔴"
        await message.reply(f"RSS monitoring: {status}")
    else:
        await message.reply("Usage: /rss on | off | status")
