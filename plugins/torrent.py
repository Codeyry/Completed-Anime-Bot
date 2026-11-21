import re
import asyncio
import aiohttp
import time
import libtorrent as lt
from config import DOWNLOAD_DIR, LOGGER, DEV_MODE
from .progressbar import progress_bar
import os 
from pathlib import PurePosixPath

logger = LOGGER(__name__)



def clean_filename(filename: str) -> str:
    filename = re.sub(r"^\[SubsPlease\]\s*", "", filename, flags=re.I)
    filename = re.sub(r"\s*\(720p\)", "", filename, flags=re.I)
    filename = re.sub(r"\s*\[[A-F0-9]{8}\](?=\.[^.]+$)", "", filename, flags=re.I)

    return filename.strip()





async def download_torrent(handle, index, message, save_path=DOWNLOAD_DIR):

    logger.info("Preparing torrent file index %s", index)
    files = handle.torrent_file().files()
    filename = files.file_path(index)
    logger.debug("Original torrent path: %s", filename)
    path = PurePosixPath(filename)
    new_filename = str(path.parent / clean_filename(path.name))
    logger.debug("Normalized torrent path: %s/%s", path.parent, path.name)

    # filename org:  [SubsPlease] Vinland Saga S2 (01-24) (720p) [Batch]/[SubsPlease] Vinland Saga S2 - 01v2 (720p) [CB08CBAA].mkv
    # here: [SubsPlease] Vinland Saga S2 (01-24) (720p) [Batch] **** [SubsPlease] Vinland Saga S2 - 01v2 (720p) [CB08CBAA].mkv

    start_time = time.time()
    total_size = files.file_size(index)
    file_path = os.path.join(save_path, new_filename)

    # edit file name
    handle.rename_file(index, new_filename)
    logger.debug("Renamed torrent file to %s", new_filename)

    # Disable downloading all files.
    priorities = [0] * files.num_files()

    # Download only the selected episode.
    priorities[index] = 7
    handle.prioritize_files(priorities)
    logger.debug("Prioritized file index %s for download", index)


    # Wait until this episode finishes downloading.
    while True:
        current = handle.file_progress()[index]

        if DEV_MODE:
            file_progress = handle.file_progress()
            logger.debug("Torrent file progress snapshot")
            for i in range(files.num_files()):
                logger.debug(
                    "Torrent file %s: %s",
                    files.file_path(i),
                    f"{file_progress[i] / files.file_size(i) * 100:.2f}%"
                    if files.file_size(i) else "0%"
                )

        await progress_bar(
            current=current,
            total=total_size,
            start_time=start_time,
            message=message,
            handle=handle,
            status=f"Downloading {files.file_path(index)}",
        )

        if current >= total_size:
            logger.info("Torrent file download complete: %s", file_path)
            break

        await asyncio.sleep(1)
    
    logger.debug("Returning downloaded file path %s", file_path)
    return file_path, clean_filename(path.name)


