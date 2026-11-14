import feedparser

import sys 
from config import RSS_URL, MONITOR_TIME, DEV_MODE
from database.database import is_entry_already_processed
from plugins.process import process_entry

async def rss_monitor(session, client):
    try:
        async with session.get(RSS_URL) as response:
            if response.status == 304:
                return

            response.raise_for_status()
            feed_content = await response.read() 

        feed = feedparser.parse(feed_content)

        for entry in feed.entries:
            title = entry.get("title")

            # Ignore anything that isn't a batch release
            if "[Batch]" not in title:
                continue

            print(title)

            entry_id = entry.get("guid")

            if await is_entry_already_processed(entry_id):
                continue

            await process_entry(client, entry, entry_id)
    except Exception as e:
        print(f"error on rss_monitor {e}")


