from bot import aiohttp
from plugins.progressbar import progress_bar
from pyrogram import client
from pyrogram.enums import ParseMode
from database.database import mark_entry
from .torrent import download_torrent
from .anilist import get_cover_and_anime_id
from .link_gen import link_gen_batch
import asyncio
import libtorrent as lt
import os, time

from config import DB_CHANNEL_ID, DOWNLOAD_DIR, POST_CHANNEL_ID, LOGGER, ANIME_POST_TEMPLATE, DEV_MODE
import re

logger = LOGGER(__name__)


def extract_anime_name(category: str) -> str:
    anime_name = re.sub(r'\s*-\s*720$', '', category).strip()
    logger.debug("Extracted anime name %s from category %s", anime_name, category)
    return anime_name


async def wait_metadata(handle, timeout=300):
    logger.info("Waiting for torrent metadata (timeout=%ss)", timeout)
    start = asyncio.get_event_loop().time()
    while not handle.has_metadata():
        if asyncio.get_event_loop().time() - start > timeout:
            logger.error("Torrent metadata was not received within %ss", timeout)
            raise TimeoutError("Metadata not received in time")
        await asyncio.sleep(1)
    logger.info("Torrent metadata received")

async def download_thumbnail(url, id):
    if id is None:
        logger.error(" guid is none type")
        logger.error("Cannot download thumbnail without AniList ID")

    logger.debug("Downloading thumbnail for AniList ID %s", id)
    async with aiohttp.ClientSession() as session:
        async with session.get(url) as response:
            response.raise_for_status()
            image_data = await response.read()

    thumb_path = os.path.join(DOWNLOAD_DIR, f"{id}.jpg")

    with open(thumb_path, "wb") as file:
        file.write(image_data)

    logger.info("Thumbnail saved to %s", thumb_path)
    return thumb_path


def normalize_anilist_title(title: str) -> str:
    title = re.sub(
        r"\bS(\d+)\b",
        r"Season \1",
        title,
        flags=re.IGNORECASE
    )
    logger.debug("Normalized AniList title: %s", title)
    return title


# Create torrent session
session = lt.session({
    "listen_interfaces": "0.0.0.0:6881",
    "enable_dht": True,  # Enable distributed peer discovery.
    "enable_lsd": True,  # Enable discovery of peers on the local network.
    "enable_upnp": True,  # Allow automatic router port forwarding.
    "enable_natpmp": True,  # Enable NAT-PMP port forwarding.
})






async def process_entry(client, entry, entry_id: str):
    try:
        logger.info("Starting processing for RSS entry %s", entry_id)
        normal_anime_name = normalize_anilist_title(entry.get("category"))
        anime_name = extract_anime_name(normal_anime_name)
        result = await get_cover_and_anime_id(anime_name)

        magnet_link = entry.get("link")
        # check that magnet_url if its a valid magnet link or not. 
        if not magnet_link.startswith("magnet:?"):
            logger.error("Invalid magnet URL in entry %s", entry_id)
            raise ValueError("Invalid magnet URL.")
        
        # parse magnet_url using libtorrent 
        params = lt.parse_magnet_uri(magnet_link)

        # save path 
        params.save_path = DOWNLOAD_DIR

        # Add the magnet torrent to the existing session.
        handle = session.add_torrent(params)
        logger.info("Torrent added for %s", anime_name)

        try: 
            # Wait until torrent metadata becomes available.
            await wait_metadata(handle)

            # get torrent files list
            files = handle.torrent_file().files()

            # Find video files in torrent order.
            video_files = [
                i for i in range(files.num_files())
                if files.file_path(i).lower().endswith((".mkv", ".mp4", ".avi"))
            ]

            if not video_files:
                logger.warning("No video files found for entry %s", entry_id)
                raise ValueError("video files are empty")
            

            message = await client.send_message(
                chat_id=DB_CHANNEL_ID,
                text="... !!"
                )
            logger.info("Found %d video files for %s", len(video_files), anime_name)

            # Download, upload, and process each video.
            for position, index in enumerate(video_files):

                file_path, filename = await download_torrent(handle, index, message)
                logger.info("Downloaded video file: %s", file_path)

                thumb_file = await download_thumbnail(result.get("cover"), result.get("id"))

                # upload to tg db channnel
                db_file = await client.send_document(
                    chat_id=DB_CHANNEL_ID,
                    document=file_path,
                    caption=filename,
                    progress=progress_bar,
                    thumb=thumb_file,
                    progress_args=(
                        time.time(),
                        message,
                        f"Uploading {os.path.basename(file_path)}",
                        handle,
                    )
                )
                logger.info("Uploaded %s to database channel", filename)

                os.remove(file_path) # cleanup: delete file after sending to tg
                logger.debug("Removed local video file %s", file_path)

                if position == 0:
                    first_db_file = db_file

                if position == len(video_files) - 1:
                    last_db_file = db_file

            # Link generation
            buttons = await link_gen_batch(first_db_file, last_db_file)
            logger.debug("Batch link buttons prepared")

            animeId = result.get("id")
            if animeId is not None:
                post_thumb_url = f"https://img.anili.st/media/{animeId}"
            
            if not post_thumb_url:
                raise ValueError("post_thumb_url is undefined")
            

            await client.send_photo(
                chat_id=POST_CHANNEL_ID,
                photo=post_thumb_url,
                caption=ANIME_POST_TEMPLATE.format(
                    anime_name=normal_anime_name,
                    eps=files.num_files(),
                    size=entry.get("subsplease_size"),
                    plot=result.get("description")
                ),
                reply_markup=buttons,
                parse_mode=ParseMode.HTML
            )
            logger.info("Published anime post for %s", normal_anime_name)

            await mark_entry(entry_id)
            logger.info("Finished processing RSS entry %s", entry_id)


        finally:
            handle.pause()
            session.remove_torrent(handle)
    except Exception:
        logger.exception("Failed to process RSS entry %s", entry_id)
