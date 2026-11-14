import time
from pyrogram.errors import MessageNotModified, MessageIdInvalid

# progress bar function
LAST_UPDATE_TIME = 0
async def progress_bar(current, total, start_time, message, status, handle):
    global LAST_UPDATE_TIME
    CURRENT_TIME = time.time()
    DELAY = 5

    # libtorrent info status 
    status = handle.status()

    if CURRENT_TIME - LAST_UPDATE_TIME < DELAY:
        return
    LAST_UPDATE_TIME = CURRENT_TIME

    elapsed = time.time() - start_time
    percent = (current / total) * 100 if total else 0

    bar_length = 10
    filled_bar = int(bar_length * percent / 100)
    bar = "▣" * filled_bar + "▢" * (bar_length - filled_bar)

    speed = current / elapsed if elapsed > 0 else 0
    speed_in_mb = speed / (1024 * 1024)

    eta = (total - current) / speed if speed > 0 else 0
    downloaded_in_mb = current / (1024 * 1024)
    total_in_mb = total / (1024 * 1024)

    prog_text = (
        f"┌• {status} ~ {int(elapsed)}s\n"
        f"├• {bar}\n{percent:.2f}%\n"
        f"├• PEERS: {status.num_peers}\n"
        f"├• SEEDS: {status.num_seeds}\n"
        f"├• Download: {status.download_rate / 1024:.2f} KB/s\n"
        f"├• Upload: {status.upload_rate / 1024:.2f} KB/s\n"
        f"├• SIZE: {downloaded_in_mb:.2f} MB of {total_in_mb:.2f} MB\n"
        f"├• SPEED: {speed_in_mb:.2f} MB/s\n"
        f"└• ETA: {int(eta)}s"
    )

    try:
        await message.edit_text(prog_text)
    except (MessageNotModified, MessageIdInvalid):
        pass  # ignore these safely