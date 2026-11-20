import re
import asyncio
import aiohttp
import time
import libtorrent as lt
from config import DOWNLOAD_DIR, LOGGER, DEV_MODE
from .progressbar import progress_bar
import os 
from pathlib import PurePosixPath




def clean_filename(filename: str) -> str:
    filename = re.sub(r"^\[SubsPlease\]\s*", "", filename, flags=re.I)
    filename = re.sub(r"\s*\(720p\)", "", filename, flags=re.I)
    filename = re.sub(r"\s*\[[A-F0-9]{8}\](?=\.[^.]+$)", "", filename, flags=re.I)

    return filename.strip()





async def download_torrent(handle, index, message, save_path=DOWNLOAD_DIR):

    files = handle.torrent_file().files()
    filename = files.file_path(index)
    print("filename org: ", filename)
    path = PurePosixPath(filename)
    new_filename = str(path.parent / clean_filename(path.name))
    print(f"here: {path.parent} **** {path.name}")

    # filename org:  [SubsPlease] Vinland Saga S2 (01-24) (720p) [Batch]/[SubsPlease] Vinland Saga S2 - 01v2 (720p) [CB08CBAA].mkv
    # here: [SubsPlease] Vinland Saga S2 (01-24) (720p) [Batch] **** [SubsPlease] Vinland Saga S2 - 01v2 (720p) [CB08CBAA].mkv

    start_time = time.time()
    total_size = files.file_size(index)
    file_path = os.path.join(save_path, new_filename)

    # edit file name
    handle.rename_file(index, new_filename)

    # Disable downloading all files.
    priorities = [0] * files.num_files()

    # Download only the selected episode.
    priorities[index] = 7
    handle.prioritize_files(priorities)


    # Wait until this episode finishes downloading.
    while True:
        current = handle.file_progress()[index]

        if DEV_MODE:
            file_progress = handle.file_progress()

            print("\n--- TORRENT DEBUG ---")
            for i in range(files.num_files()):
                LOGGER(__name__).info(
                    files.file_path(i),
                    f"{file_progress[i] / files.file_size(i) * 100:.2f}%"
                    if files.file_size(i) else "0%"
                )
            LOGGER(__name__).info("--------------------\n")

        await progress_bar(
            current=current,
            total=total_size,
            start_time=start_time,
            message=message,
            handle=handle,
            status=f"Downloading {files.file_path(index)}",
        )

        if current >= total_size:
            break

        await asyncio.sleep(1)
    
    return file_path, clean_filename(path.name)


