# main file to run the bot
from bot import Bot 
from config import LOGGER

logger = LOGGER(__name__)


logger.info("Launching bot")
Bot().run() #bot run
