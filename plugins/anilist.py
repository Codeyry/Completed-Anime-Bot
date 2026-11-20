import aiohttp

async def get_cover_and_anime_id(anime_name: str) -> dict | None:
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

    async with aiohttp.ClientSession() as session:
        async with session.post(
            "https://graphql.anilist.co",
            json={"query": query, "variables": variables}
        ) as resp:
            resp.raise_for_status()
            data = await resp.json()

    if "errors" in data:
        raise ValueError(f"GraphQL error: {data['errors']}")

    media = data.get("data", {}).get("Media")
    if media is None:
        return None

    return {
        "id": media["id"],
        "cover": media["coverImage"]["large"] if media["coverImage"] else None,
        "description": media.get("description")[:200] if len(media.get("description")) > 200 else "Description failed successfully :("
    }   