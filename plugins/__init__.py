#(©)Codexbotz
#@iryme

from aiohttp import web
from .route import routes
from config import LOGGER

logger = LOGGER(__name__)

async def web_server():
    logger.debug("Creating web application with %d routes", len(routes))
    web_app = web.Application(client_max_size=30000000)
    web_app.add_routes(routes)
    return web_app
