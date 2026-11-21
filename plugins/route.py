#(©)Codexbotz
#rymme

from aiohttp import web
from config import LOGGER

logger = LOGGER(__name__)

routes = web.RouteTableDef()

@routes.get("/", allow_head=True)
async def root_route_handler(request):
    logger.debug("Root health route requested from %s", request.remote)
    return web.json_response("OnlyNoco")
