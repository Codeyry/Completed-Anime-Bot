from config import OWNER_ID
from aiohttp import web
from plugins import web_server
from pyrogram.client import Client
from pyrogram.enums import ParseMode
import sys 
import os
from datetime import datetime
import pyrogram.utils
pyrogram.utils.MIN_CHANNEL_ID = -1009147483647 # type: ignore
import aiohttp
import asyncio

from config import API_HASH, API_ID, BOT_TOKEN, WORKER, PORT, LOGGER, MONITOR_TIME, DEV_MODE, SHORT_SLEEP

logger = LOGGER(__name__)
from plugins.monitor import rss_monitor

ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__)))
if os.path.exists(os.path.join(ROOT, "config.py")):
    pass 
elif os.path.exists(os.path.join(ROOT, "sample_config.py")):
    logger.error("config.py not found! Rename <sample_config.py> to <config.py> and set your credentials.") 
    sys.exit(1) 
else:
    logger.error("Neither config.py nor sample_config.py found.")
    sys.exit(1)
        


class Bot(Client):
    def __init__(self):
        super().__init__(
            name="Bot",
            api_hash=API_HASH,
            api_id=API_ID,
            plugins={
                "root": "plugins"
            },
            workers=WORKER,
            bot_token=BOT_TOKEN
        )
        self.LOGGER = LOGGER
        self.rss_enabled = False
        logger.info("Bot client initialized (dev_mode=%s, workers=%s)", DEV_MODE, WORKER)

    async def start(self, *args, **kwargs):
        logger.info("Starting bot client")
        await super().start(*args, **kwargs)
        usr_bot_me = await self.get_me()
        self.uptime = datetime.now()
        
        try:
            self.set_parse_mode(ParseMode.HTML)
            # here is the vars 
            bot_name = usr_bot_me.first_name or "Name Not Defined!"
            bot_username = usr_bot_me.username or "Username Not Defined!"
            logger.info("Bot Running..!\n\nCreated by \nhttps://t.me/codeyry")
            logger.info("Bot Detailes: \n\n")
            logger.info("Bot Name: %s", bot_name)
            logger.info("Bot Username: %s", bot_username)
            
        except Exception as e:
            logger.exception("Error during bot startup: %s", e)
            sys.exit()

        #web-response
        app = web.AppRunner(await web_server())
        await app.setup()
        bind_address = "0.0.0.0"
        await web.TCPSite(app, bind_address, PORT).start()
        logger.info("Health web server listening on %s:%s", bind_address, PORT)

        # 👇 THIS is what actually launches your RSS loop
        self.rss_task = asyncio.create_task(self.rss_loop_run())
        if DEV_MODE and self.rss_task:
            logger.info("rss_task started")


    async def rss_loop_run(self):
        logger.info("RSS loop started")
        timeout = aiohttp.ClientTimeout(total=30)
        notified = False
        async with aiohttp.ClientSession(timeout=timeout) as session:
            while True:
                if not self.rss_enabled:
                    logger.debug("RSS monitoring disabled; waiting")
                    await asyncio.sleep(SHORT_SLEEP)
                    continue

                if not notified:
                    logger.info("RSS loop active; notifying owner")
                    await self.send_message(
                        OWNER_ID,
                        f"RSS ENABLED, WAIT ({SHORT_SLEEP / 60} MIN)"
                    )
                    notified = True

                result = await rss_monitor(session, self)
                logger.debug("RSS monitor returned %s", result)

                if result is False:
                    logger.info(f"long sleep time {MONITOR_TIME/60} min")
                    await asyncio.sleep(MONITOR_TIME)
                else:
                    logger.info(f"short sleep time {SHORT_SLEEP/60} min")
                    await asyncio.sleep(SHORT_SLEEP)
                

    

    async def stop(self, *args):
        logger.info("Stopping bot client")
        if self.rss_task:
            self.rss_task.cancel()
        await super().stop()
        logger.info("Bot stopped.")
