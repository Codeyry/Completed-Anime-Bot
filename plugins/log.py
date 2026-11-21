from pyrogram import Client, filters
from config import OWNER_ID, LOG_FILE_NAME
from pyrogram.types import Message
import os


@Client.on_message(filters.command("log") & filters.user(OWNER_ID))
async def get_log(client: Client, message: Message):

    await message.reply_document(
        document=os.path.abspath(LOG_FILE_NAME)
    )