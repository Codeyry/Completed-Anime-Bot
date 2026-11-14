"""Configuration template for GitHub releases.

Set the required credentials in the deployment environment. Do not commit
real tokens, API credentials, database URLs, or account IDs here.
"""

import os
import logging
from logging.handlers import RotatingFileHandler


DEV_MODE = os.environ.get("DEV_MODE", "false").lower() == "true"

# Required credentials and account settings
BOT_TOKEN = os.environ["BOT_TOKEN"]
API_ID = int(os.environ["API_ID"])
API_HASH = os.environ["API_HASH"]
OWNER_ID = int(os.environ["OWNER_ID"])
DB_CHANNEL_ID = int(os.environ["DB_CHANNEL_ID"])
DB_URL = os.environ["DB_URL"]
DB_NAME = os.environ.get("DB_NAME", "Animeyry")

# Optional runtime settings
WORKER = int(os.environ.get("WORKER", "4"))
PORT = int(os.environ.get("PORT", "8080"))
DOWNLOAD_DIR = os.environ.get("DOWNLOAD_DIR", "./downloads")
MONITOR_TIME = int(os.environ.get("MONITOR_TIME", "3600"))
RSS_URL = os.environ.get("RSS_URL", "https://subsplease.org/rss/?r=720")
BROADCAST_DELETE_TIME = int(os.environ.get("BROADCAST_DELETE_TIMED", "1800"))

START_PIC = os.environ.get("START_PIC", "https://envs.sh/bjb.mp4 https://envs.sh/bjP.mp4 https://envs.sh/bjw.mp4 https://envs.sh/bj0.mp4 https://envs.sh/bjS.mp4 https://envs.sh/bjW.mp4 https://envs.sh/bjB.mp4 https://envs.sh/bjI.mp4 https://envs.sh/bjn.mp4 https://envs.sh/bjT.mp4 https://envs.sh/bjZ.mp4 https://envs.sh/bjL.mp4 https://envs.sh/bj5.mp4 https://envs.sh/bjY.mp4 https://envs.sh/bjC.mp4").split(" ")
START_MSG = os.environ.get(
    "START_MSG",
    "<blockquote>Hello {mention}</blockquote>\n\n"
    "<b>I watch all that I am permitted to see. "
    "With the right access, I let anyone join private channels instantly. "
    "Add me as admin, and you can rely on me.</b>",
)
ABOUT_MSG = """
<b>›› ᴀʙᴏᴜᴛ ᴍᴇ:</b>
◧ ᴏᴡɴᴇʀ: <a href='https://t.me/OnlyNoco'>ᴏɴʟʏɴᴏᴄᴏ</a>
◧ ᴘᴏʀᴛғᴏʟɪᴏ: <a href='https://onlynoco.vercel.app'>ᴄʟɪᴄᴋ ʜᴇʀᴇ</a>
◧ ʀᴇᴘᴏ: <a href='https://github.com/OnlyNoco/Auto-Request-Accept-Bot'>ɢɪᴛʜᴜʙ</a>
◧ ʟɪʙs ~ <a href='https://github.com/Mayuri-Chan/pyrofork'>ᴘʏʀᴏғᴏʀᴋ</a> • <a href='https://www.python.org/'>ᴘʏᴛʜᴏɴ</a> • <a href='https://www.mongodb.com/'>ᴍᴏɴɢᴏᴅʙ</a>

◧ ᴏᴜʀ sᴇʀᴠɪᴄᴇs ~
⊡ <a href='https://t.me/+O7PeEMZOAoMzYzVl'>ʜᴇɴᴛᴀɪ ᴄʀɪsᴘ</a>
⊡ <a href='https://t.me/HeavenlySubs'>ʙᴀᴛᴛʟᴇ ᴛʜʀᴏᴜɢʜ ᴛʜᴇ ʜᴇᴀᴠᴇɴs</a>
⊡ <a href='https://t.me/CrispAnime'>ᴄʀɪsᴘ ᴀɴɪᴍᴇ</a>
"""
CMD_MSG = os.environ.get(
    "CMD_MSG",
    "<blockquote>/start - to check bot alive or dead!\n"
    "/help - to get help from bot usuages\n"
    "/report - to report issue to admin\n"
    "Send or Forward anything i will broadcast it to all users.",
)

# LOGGER SETUP
LOG_FILE_NAME = "onlynoco.txt"
logging.basicConfig(
    level=logging.INFO,
    format="[%(asctime)s - %(levelname)s] - %(name)s - %(message)s",
    datefmt='%d-%b-%y %H:%M:%S',
    handlers=[
        RotatingFileHandler(
            LOG_FILE_NAME,
            maxBytes=50000000,
            backupCount=10
        ),
        logging.StreamHandler()
    ]
)
logging.getLogger("pyrogram").setLevel(logging.WARNING)

def LOGGER(name: str) -> logging.Logger:
    return logging.getLogger(name)
loggiing = "LTEwMDIxOTcyNzk1NDI="