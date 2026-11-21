import base64
from pyrogram import Client
from pyrogram.types import Message, InlineKeyboardMarkup, InlineKeyboardButton
from config import BOT_USERNAME,DB_CHANNEL_ID, LOGGER, DEV_MODE

logger = LOGGER(__name__)


def encode(text: str) -> str:
  return base64.urlsafe_b64encode(text.encode()).decode()


async def decode(base64_string):
    logger.debug("Decoding start payload")
    base64_string = base64_string.strip("=") # links generated before this commit will be having = sign, hence striping them to handle padding errors.
    base64_bytes = (base64_string + "=" * (-len(base64_string) % 4)).encode("ascii")
    string_bytes = base64.urlsafe_b64decode(base64_bytes)
    string = string_bytes.decode("ascii")
    logger.debug("Start payload decoded")
    return string


async def link_gen_batch(first_file, last_file):
  try:
    logger.debug("Generating batch link for files %s through %s", first_file.id, last_file.id)
    encoded = encode(f"get-{first_file.id * abs(DB_CHANNEL_ID)}-{last_file.id * abs(DB_CHANNEL_ID)}")
    start_link = f"https://t.me/{BOT_USERNAME}?start={encoded}"
    buttons = InlineKeyboardMarkup([[InlineKeyboardButton("• ᴅᴏᴡɴʟᴏᴀᴅ ‹› ᴡᴀᴛᴄʜ •", url=start_link)]])
    logger.info("Batch download link generated")
    return buttons
  except Exception as e:
    logger.exception("Link generation failed: %s", e)
    return None
