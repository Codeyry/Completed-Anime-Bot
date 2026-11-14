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

from config import API_HASH, API_ID, BOT_TOKEN, WORKER, PORT, LOGGER, MONITOR_TIME, DEV_MODE
from plugins.monitor import rss_monitor

ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__)))
if os.path.exists(os.path.join(ROOT, "config.py")):
    pass 
elif os.path.exists(os.path.join(ROOT, "sample_config.py")):
    LOGGER(__name__).error("config.py not found! Rename <sample_config.py> to <config.py> and set your credentials.") 
    sys.exit(1) 
else:
    LOGGER(__name__).error("Neither config.py nor sample_config.py found.")
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

    async def start(self, *args, **kwargs):
        await super().start(*args, **kwargs)
        usr_bot_me = await self.get_me()
        self.uptime = datetime.now()
        
        try:
            self.set_parse_mode(ParseMode.HTML)
            # here is the vars 
            bot_name = usr_bot_me.first_name or "Name Not Defined!"
            bot_username = usr_bot_me.username or "Username Not Defined!"
            self.LOGGER(__name__).info(f"Bot Running..!\n\nCreated by \nhttps://t.me/codeyry")
            self.LOGGER(__name__).info("Bot Detailes: \n\n")
            self.LOGGER(__name__).info(f"Bot Name: {bot_name}")
            self.LOGGER(__name__).info(f"Bot Username: {bot_username}")
            
        except Exception as e:
            self.LOGGER(__name__).warning(f"Error during bot startup: {e}")
            sys.exit()

        #web-response
        app = web.AppRunner(await web_server())
        await app.setup()
        bind_address = "0.0.0.0"
        await web.TCPSite(app, bind_address, PORT).start()

        # 👇 THIS is what actually launches your RSS loop
        self.rss_task = asyncio.create_task(self.rss_loop_run())
        if DEV_MODE and self.rss_task:
            self.LOGGER(__name__).info("rss_task started")


    async def rss_loop_run(self):
        timeout = aiohttp.ClientTimeout(total=30)
        async with aiohttp.ClientSession(timeout=timeout) as session:
            while True:
                await rss_monitor(session, self)
                await asyncio.sleep(MONITOR_TIME)


        
    

    async def stop(self, *args):
        if self.rss_task:
            self.rss_task.cancel()
        await super().stop()
        self.LOGGER(__name__).info("Bot stopped.")