import time
from pyrogram.errors import MessageNotModified, MessageIdInvalid
from config import LOGGER, DEV_MODE

logger = LOGGER(__name__)

LAST_UPDATE_TIME = 0

async def progress_bar(current, total, start_time, message, status, handle):
    global LAST_UPDATE_TIME

    CURRENT_TIME = time.time()
    DELAY = 5

    if CURRENT_TIME - LAST_UPDATE_TIME < DELAY:
        logger.debug("Progress update skipped within %ss throttle", DELAY)
        return

    LAST_UPDATE_TIME = CURRENT_TIME

    torrent_status = handle.status()

    elapsed = CURRENT_TIME - start_time
    percent = (current / total) * 100 if total else 0

    bar_length = 10
    filled_bar = int(bar_length * percent / 100)
    bar = "▣" * filled_bar + "▢" * (bar_length - filled_bar)

    speed = torrent_status.download_rate
    speed_in_mb = speed / (1024 * 1024)

    eta = (total - current) / speed if speed > 0 else 0

    downloaded_in_mb = current / (1024 * 1024)
    total_in_mb = total / (1024 * 1024)

    prog_text = (
        f"┌• {status} ~ {int(elapsed)}s\n"
        f"├• {bar}\n{percent:.2f}%\n"
        f"├• PEERS: {torrent_status.num_peers}\n"
        f"├• SEEDS: {torrent_status.num_seeds}\n"
        f"├• Download: {torrent_status.download_rate / 1024:.2f} KB/s\n"
        f"├• Upload: {torrent_status.upload_rate / 1024:.2f} KB/s\n"
        f"├• SIZE: {downloaded_in_mb:.2f} MB of {total_in_mb:.2f} MB\n"
        f"├• SPEED: {speed_in_mb:.2f} MB/s\n"
        f"└• ETA: {int(eta)}s"
    )

    try:
        await message.edit_text(prog_text)
        logger.debug("Progress updated: %s %.2f%%", status, percent)
    except (MessageNotModified, MessageIdInvalid):
        logger.debug("Progress message was unchanged or no longer valid")
