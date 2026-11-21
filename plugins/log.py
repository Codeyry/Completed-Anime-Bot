from pyrogram import Client, filters
from config import OWNER_ID, LOG_FILE_NAME, LOGGER
from pyrogram.types import Message
import os

logger = LOGGER(__name__)


@Client.on_message(filters.command("log") & filters.user(OWNER_ID))
async def get_log(client: Client, message: Message):
    logger.info("Log file requested by owner %s", message.from_user.id)
    await message.reply_document(
        document=os.path.abspath(LOG_FILE_NAME)
    )
    logger.info("Log file sent to owner %s", message.from_user.id)
