import os
import json
import asyncio
import logging
from datetime import datetime
from telethon.sync import TelegramClient
from telethon.tl.types import MessageMediaPhoto, MessageMediaDocument
from dotenv import load_dotenv

# --- 1. Configuration and Logging ---
load_dotenv()  # Load environment variables from .env file

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(levelname)s - %(message)s",
    handlers=[logging.FileHandler("scrape.log"), logging.StreamHandler()],
)

logger = logging.getLogger(__name__)

# Telegram API credentials from .env
API_ID = os.getenv("TELEGRAM_API_ID")
API_HASH = os.getenv("TELEGRAM_API_HASH")
PHONE_NUMBER = os.getenv("PHONE_NUMBER")

# Define the output directory for raw data
RAW_DATA_DIR = os.path.join(
    os.path.dirname(os.path.abspath(__file__)), "../data/raw/telegram_messages"
)
# Ensure the base directory exists
os.makedirs(RAW_DATA_DIR, exist_ok=True)

# List of public Telegram channels to scrape (replace with actual channel usernames or IDs)
# You can find usernames in the channel's info, e.g., @tikvahpharma
# For private channels, you need to be a member and might use their numeric ID.
# We will use public channels here.
TARGET_CHANNELS = [
    "@CheMed123",
    "@lobelia4cosmetics",
    "@tikvahpharma",
    # Add more channel usernames here
]


# --- 2. Asynchronous Scraping Function ---
async def scrape_channel_data(client, channel_username, limit=100):
    """
    Scrapes messages from a given Telegram channel and saves them as JSON files.
    Collects message data, including text and basic media info.
    """
    logger.info(f"Starting scraping for channel: {channel_username}")
    all_messages = []
    try:
        entity = await client.get_entity(channel_username)
        logger.info(f"Resolved entity for {channel_username}: {entity.title}")

        async for message in client.iter_messages(entity, limit=limit):
            message_dict = {
                "message_id": message.id,
                "channel_id": (
                    message.peer_id.channel_id
                    if hasattr(message.peer_id, "channel_id")
                    else None
                ),
                "channel_username": channel_username,
                "date": message.date.isoformat(),
                "text": message.text,
                "views": message.views,
                "forwards": message.forwards,
                "replies_count": message.replies.replies if message.replies else 0,
                "has_media": bool(message.media),
                "media_type": None,
                "file_name": None,
                "mime_type": None,
                "file_size": None,
                "is_photo": False,
                "is_document": False,
            }

            if message.media:
                message_dict["media_type"] = message.media.__class__.__name__
                if isinstance(message.media, MessageMediaPhoto):
                    message_dict["is_photo"] = True
                elif isinstance(message.media, MessageMediaDocument):
                    message_dict["is_document"] = True
                    document = message.media.document
                    message_dict["file_name"] = (
                        getattr(document.attributes[0], "file_name", None)
                        if document.attributes
                        else None
                    )
                    message_dict["mime_type"] = document.mime_type
                    message_dict["file_size"] = document.size

            all_messages.append(message_dict)

        logger.info(
            f"Finished scraping {len(all_messages)} messages from {channel_username}."
        )

        # Save to Data Lake
        today_str = datetime.now().strftime("%Y-%m-%d")
        channel_dir = os.path.join(RAW_DATA_DIR, today_str)
        os.makedirs(
            channel_dir, exist_ok=True
        )  # Create daily directory if it doesn't exist

        output_file_path = os.path.join(channel_dir, f"{channel_username}.json")
        with open(output_file_path, "w", encoding="utf-8") as f:
            json.dump(all_messages, f, ensure_ascii=False, indent=4)

        logger.info(f"Data for {channel_username} saved to: {output_file_path}")

    except Exception as e:
        logger.error(f"Error scraping channel {channel_username}: {e}", exc_info=True)


# --- 3. Main Execution Block ---
async def main():
    """
    Main function to establish Telegram connection and orchestrate scraping.
    """


if __name__ == "__main__":
    logger.info("Starting Telegram Data Scraping Process.")
    asyncio.run(main())
    logger.info("Telegram Data Scraping Process Finished.")
