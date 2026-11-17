import base64
from pyrogram import Client
from pyrogram.types import Message, InlineKeyboardMarkup, InlineKeyboardButton
from config import BOT_USERNAME,DB_CHANNEL_ID, LOGGER

logger = LOGGER(__name__)


def encode(text: str) -> str:
  return base64.urlsafe_b64encode(text.encode()).decode()


async def link_gen_batch(first_file, last_file):
  try:
    encoded = encode(f"get-{first_file.id * abs(DB_CHANNEL_ID)-{last_file.id * abs(DB_CHANNEL_ID)}}")
    start_link = f"https://t.me/{BOT_USERNAME}?start={encoded}"
    buttons = InlineKeyboardMarkup([[InlineKeyboardButton("• ᴅᴏᴡɴʟᴏᴀᴅ ‹› ᴡᴀᴛᴄʜ •", url=start_link)]])
    return buttons, start_link
  except Exception as e:
    logger.error(f"Link Generation Failed! {e}")
    return None