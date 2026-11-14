from plugins.progressbar import progress_bar
from pyrogram import client, filters
# from database.database import mark_entry
from .torrent import download_torrent
import asyncio
import libtorrent as lt
import os, time

from config import DB_CHANNEL_ID, DOWNLOAD_DIR



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

        # Wait until torrent metadata becomes available.
        await wait_metadata(handle)

        # get torrent files list
        files = handle.torrent_file().files()

        # Find video files in torrent order.
        video_files = [
            i for i in range(files.num_files())
            if files.file_path(i).lower().endswith((".mkv", ".mp4", ".avi"))
        ]

        message = await client.send_message(
            chat_id=DB_CHANNEL_ID,
            text="... !!"
        )

        # Download, upload, and process each video.
        for index in video_files:
            file_path = await download_torrent(handle, index, message)

            # upload to tg db channnel
            await client.send_document(
                chat_id=DB_CHANNEL_ID,
                document=file_path,
                caption=entry.get("category"),
                progress=progress_bar,
                progress_args=(
                    time.time(),
                    message,
                    f"Uploading {os.path.basename(file_path)}",
                    handle,
                )
            )

        
    except Exception as e:
        print(f"{e}")




