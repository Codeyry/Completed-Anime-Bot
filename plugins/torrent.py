import re
import asyncio
import aiohttp
import time
import libtorrent as lt
from config import DOWNLOAD_DIR
from .progressbar import progress_bar
import os 





async def download_torrent(handle, index, message, save_path=DOWNLOAD_DIR):
    files = handle.torrent_file().files()


    filename = files.file_path(index)
    start_time = time.time()
    total_size = files.file_size(index)
    file_path = os.path.join(save_path, filename)


        # Wait until this episode finishes downloading.
    while True:
        file_progress = await asyncio.to_thread(handle.file_progress)
        current = file_progress[index]

        await progress_bar(
            current=current,
            total=total_size,
            start_time=start_time,
            message=message,
            status=f"Downloading {files.file_path(index)}",
        )

        if current >= total_size:
            break

        await asyncio.sleep(1)
    
    return file_path


