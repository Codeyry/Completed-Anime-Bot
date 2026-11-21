import feedparser
import sys 
from config import RSS_URL, MONITOR_TIME, DEV_MODE, LOGGER
from database.database import is_entry_already_processed
from plugins.process import process_entry

logger = LOGGER(__name__)

async def rss_monitor(session, client):
    try:
        processed = False
        logger.debug("Starting RSS check: %s", RSS_URL)

        async with session.get(RSS_URL) as response:
            if response.status == 304:
                logger.debug("RSS feed has not changed (HTTP 304)")
                return False

            response.raise_for_status()
            feed_content = await response.read() 

        feed = feedparser.parse(feed_content)
        logger.info("RSS feed parsed: %d entries", len(feed.entries))

        for entry in feed.entries:
            title = entry.get("title")

            # Ignore anything that isn't a batch release
            if "[Batch]" not in title:
                logger.debug("Skipping non-batch RSS entry: %s", title)
                continue

            logger.info("Found batch RSS entry: %s", title)

            entry_id = entry.get("guid")

            if await is_entry_already_processed(entry_id):
                logger.debug("Skipping already processed entry %s", entry_id)
                continue

            logger.info("Processing RSS entry %s", entry_id)
            await process_entry(client, entry, entry_id)

        processed = True
        return processed

    except Exception:
        logger.exception("RSS monitor crashed")
        raise


