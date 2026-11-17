from plugins.progressbar import progress_bar
from pyrogram import client
from pyrogram.enums import ParseMode
# from database.database import mark_entry
from .torrent import download_torrent
from .anilist import get_cover_and_anime_id
from .link_gen import link_gen_batch
import asyncio
import libtorrent as lt
import os, time

from config import DB_CHANNEL_ID, DOWNLOAD_DIR, POST_CHANNEL_ID
import re



def extract_anime_name(category: str) -> str:
    return re.sub(r'\s*-\s*720$', '', category).strip()   


async def wait_metadata(handle, timeout=300):
    start = asyncio.get_event_loop().time()
    while not handle.has_metadata():
        if asyncio.get_event_loop().time() - start > timeout:
            raise TimeoutError("Metadata not received in time")
        await asyncio.sleep(1)



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
        anime_name = extract_anime_name(entry.get("category"))
        result = await get_cover_and_anime_id(anime_name)

        magnet_link = entry.get("link")
        # check that magnet_url if its a valid magnet link or not. 
        if not magnet_link.startswith("magnet:?"):
            raise ValueError("Invalid magnet URL.")
        
        # parse magnet_url using libtorrent 
        params = lt.parse_magnet_uri(magnet_link)

        # save path 
        params.save_path = DOWNLOAD_DIR

        # Add the magnet torrent to the existing session.
        handle = session.add_torrent(params)

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
                raise ValueError("video files are empty")
            

            message = await client.send_message(
                chat_id=DB_CHANNEL_ID,
                text="... !!"
                )

            # Download, upload, and process each video.
            for position, index in enumerate(video_files):

                file_path = await download_torrent(handle, index, message)

                # upload to tg db channnel
                db_file = await client.send_document(
                    chat_id=DB_CHANNEL_ID,
                    document=file_path,
                    caption=entry.get("category"),
                    progress=progress_bar,
                    thumbnail=result.get("cover"),
                    progress_args=(
                        time.time(),
                        message,
                        f"Uploading {os.path.basename(file_path)}",
                        handle,
                    )
                )

                os.remove(file_path) # cleanup: delete file after sending to tg

                if position == 0:
                    first_db_file = db_file

                if position == len(video_files) - 1:
                    last_db_file = db_file

            # Link generation
            buttons = await link_gen_batch(first_db_file, last_db_file)

            animeId = result.get("id")
            if animeId is not None:
                thumb = f"https://img.anili.st/media/{animeId}"
            
            if not thumb:
                raise ValueError("Thumb is undefined")

            await client.send_photo(
                chat_id=POST_CHANNEL_ID,
                photo=thumb,
                caption=None,
                reply_markup=buttons,
                parse_mode=ParseMode.MARKDOWN
            )
        finally:
            handle.pause()
            session.remove_torrent(handle)
    except Exception as e:
        print(f"{e}")




