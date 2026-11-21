import aiohttp
from config import LOGGER, DEV_MODE

logger = LOGGER(__name__)

async def get_cover_and_anime_id(anime_name: str) -> dict | None:
    logger.info("Looking up anime metadata for %s", anime_name)
    query = '''
    query ($search: String!) {
        Media(search: $search, type: ANIME) {
            id
            coverImage { large }
            description
        }
    }
    '''
    variables = {"search": anime_name}

    try:
        async with aiohttp.ClientSession() as session:
            async with session.post(
                "https://graphql.anilist.co",
                json={"query": query, "variables": variables}
            ) as resp:
                resp.raise_for_status()
                data = await resp.json()
    except Exception:
        logger.exception("AniList request failed for %s", anime_name)
        raise

    if "errors" in data:
        logger.error("AniList GraphQL returned errors for %s: %s", anime_name, data['errors'])
        raise ValueError(f"GraphQL error: {data['errors']}")

    media = data.get("data", {}).get("Media")
    if media is None:
        logger.warning("AniList returned no media for %s", anime_name)
        return None

    logger.info("AniList metadata found for %s (id=%s)", anime_name, media.get("id"))
    return {
        "id": media["id"],
        "cover": media["coverImage"]["large"] if media["coverImage"] else None,
        "description": media.get("description")[:200] if len(media.get("description")) > 200 else "Description failed successfully :("
    }   
