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

# Define the output directory for raw message JSON data
RAW_DATA_DIR = os.path.join(
    os.path.dirname(os.path.abspath(__file__)), "../data/raw/telegram_messages"
)
# Ensure the base directory exists for JSON data
os.makedirs(RAW_DATA_DIR, exist_ok=True)

# NEW: Define the output directory for downloaded media files
MEDIA_DOWNLOAD_DIR = os.path.join(
    os.path.dirname(os.path.abspath(__file__)), "../data/raw/telegram_media"
)
# Ensure media directory exists
os.makedirs(MEDIA_DOWNLOAD_DIR, exist_ok=True)

# List of public Telegram channels to scrape (replace with actual channel usernames or IDs)
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
    Collects message data, including text and basic media info, and downloads media.
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
                # Initialize media fields, will be updated if media exists
                "has_media": False,
                "media_type": None,
                "file_name": None,
                "mime_type": None,
                "file_size": None,
                "is_photo": False,
                "is_document": False,
                "local_media_path": None,  # NEW: To store the path to downloaded media
            }

            if message.media:
                message_dict["has_media"] = True
                message_dict["media_type"] = message.media.__class__.__name__

                # Handle Photo Media
                if isinstance(message.media, MessageMediaPhoto):
                    message_dict["is_photo"] = True
                    # Construct a unique path for the photo
                    photo_filename = f"photo_{message.id}_{message.date.strftime('%Y%m%d%H%M%S')}.jpg"
                    photo_path = os.path.join(MEDIA_DOWNLOAD_DIR, photo_filename)
                    try:
                        downloaded_path = await client.download_media(
                            message.media, file=photo_path
                        )
                        message_dict["local_media_path"] = downloaded_path
                        logger.info(
                            f"Downloaded photo for message {message.id} to: {downloaded_path}"
                        )
                    except Exception as download_e:
                        logger.warning(
                            f"Failed to download photo for message {message.id}: {download_e}"
                        )

                # Handle Document Media (which includes GIFs, videos, files)
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

                    # Construct a unique path for the document
                    # Use provided filename or a generic one if not available
                    doc_filename = (
                        message_dict["file_name"]
                        if message_dict["file_name"]
                        else f"document_{message.id}"
                    )
                    doc_path = os.path.join(MEDIA_DOWNLOAD_DIR, doc_filename)
                    try:
                        downloaded_path = await client.download_media(
                            message.media, file=doc_path
                        )
                        message_dict["local_media_path"] = downloaded_path
                        logger.info(
                            f"Downloaded document for message {message.id} to: {downloaded_path}"
                        )
                    except Exception as download_e:
                        logger.warning(
                            f"Failed to download document for message {message.id}: {download_e}"
                        )

            all_messages.append(message_dict)

        logger.info(
            f"Finished scraping {len(all_messages)} messages from {channel_username}."
        )

        # Save to Data Lake (JSON metadata)
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
    if not all([API_ID, API_HASH, PHONE_NUMBER]):
        logger.error(
            "Telegram API credentials (API_ID, API_HASH, PHONE_NUMBER) not found in .env file. Please set them."
        )
        return

    # Initialize Telegram Client
    client = TelegramClient("telegram_scraper_session", API_ID, API_HASH)

    try:
        logger.info("Connecting to Telegram...")
        await client.connect()

        if not await client.is_user_authorized():
            logger.info("Client not authorized. Sending authentication code...")
            await client.start(
                phone=PHONE_NUMBER
            )  # This will prompt for code/password if not already logged in
            logger.info("Client authorized successfully.")

        logger.info("Telegram client connected and authorized.")

        # Run scraping for each target channel concurrently
        tasks = [scrape_channel_data(client, channel) for channel in TARGET_CHANNELS]
        await asyncio.gather(*tasks)

    except Exception as e:
        logger.critical(
            f"Fatal error during Telegram client operation: {e}", exc_info=True
        )
    finally:
        if client.is_connected():
            logger.info("Disconnecting Telegram client.")
            await client.disconnect()


if __name__ == "__main__":
    logger.info("Starting Telegram Data Scraping Process.")
    asyncio.run(main())
    logger.info("Telegram Data Scraping Process Finished.")
