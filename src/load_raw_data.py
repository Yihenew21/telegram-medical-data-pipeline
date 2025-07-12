import os
import json
import glob
import psycopg2
from dotenv import load_dotenv
import logging

# --- 1. Configuration and Logging ---
load_dotenv()

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(levelname)s - %(message)s",
    handlers=[logging.FileHandler("load_raw_data.log"), logging.StreamHandler()],
)
logger = logging.getLogger(__name__)

# PostgreSQL Database Credentials from .env
DB_HOST = os.getenv("POSTGRES_HOST")
DB_NAME = os.getenv("POSTGRES_DB")
DB_USER = os.getenv("POSTGRES_USER")
DB_PASSWORD = os.getenv("POSTGRES_PASSWORD")
DB_PORT = os.getenv("POSTGRES_PORT")

# Path to your raw data lake
RAW_DATA_LAKE_PATH = os.path.join(
    os.path.dirname(os.path.abspath(__file__)), "../data/raw/telegram_messages"
)


# --- 2. Database Connection and Table Creation ---
def get_db_connection():
    """Establishes and returns a PostgreSQL database connection."""
    try:
        conn = psycopg2.connect(
            host=DB_HOST,
            database=DB_NAME,
            user=DB_USER,
            password=DB_PASSWORD,
            port=DB_PORT,
        )
        return conn
    except Exception as e:
        logger.error(f"Failed to connect to database: {e}", exc_info=True)
        raise


def create_raw_table(cursor):
    """
    Creates the 'raw.telegram_messages' table if it doesn't exist.
    Stores the original JSON message as JSONB for flexibility.
    """
    cursor.execute(
        """
        CREATE SCHEMA IF NOT EXISTS raw;

        CREATE TABLE IF NOT EXISTS raw.telegram_messages (
            message_id BIGINT PRIMARY KEY,
            channel_username VARCHAR(255) NOT NULL,
            scraped_date DATE NOT NULL,
            message_data JSONB NOT NULL,
            inserted_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        );

        -- Add an index for faster lookups based on channel and date
        CREATE INDEX IF NOT EXISTS idx_raw_channel_date
        ON raw.telegram_messages (channel_username, scraped_date);

        -- Add a unique constraint to prevent duplicate message_id per channel_username per scraped_date (though message_id itself should be unique globally)
        -- Consider carefully if message_id is truly globally unique or only unique within a channel.
        -- For Telegram messages, message.id is unique within a channel. For global uniqueness, we might need channel_id + message_id.
        -- Let's refine the PK to be (message_id, channel_id) later if needed for dbt or assume for now message_id from Telethon is globally distinct.
        -- For raw table, message_id as PK is fine if we only insert once.
    """
    )
    logger.info("Checked/created 'raw.telegram_messages' table.")


# --- 3. Data Loading Logic ---
def load_json_to_postgres():
    """
    Reads JSON files from the data lake and loads them into raw.telegram_messages.
    Handles incremental loading by checking existing data.
    """
    conn = None
    try:
        conn = get_db_connection()
        conn.autocommit = False  # Start transaction
        cursor = conn.cursor()

        create_raw_table(cursor)

        # Get list of all JSON files in the data lake
        # Walks through data/raw/telegram_messages/YYYY-MM-DD/*.json
        json_files = glob.glob(
            os.path.join(RAW_DATA_LAKE_PATH, "**", "*.json"), recursive=True
        )
        logger.info(f"Found {len(json_files)} JSON files to process.")

        new_records_count = 0
        for file_path in json_files:
            try:
                # Extract scraped_date from path (e.g., .../2025-07-11/channel.json)
                path_parts = file_path.split(os.sep)
                scraped_date_str = path_parts[-2]  # YYYY-MM-DD part
                # Extract channel_username from filename (e.g., channel.json -> channel)
                channel_username = os.path.basename(file_path).replace(".json", "")

                with open(file_path, "r", encoding="utf-8") as f:
                    messages = json.load(f)

                if not messages:
                    logger.warning(f"File {file_path} contains no messages. Skipping.")
                    continue

                for msg in messages:
                    # Ensure 'message_id' and 'channel_username' exist for insertion
                    if "message_id" not in msg or "channel_username" not in msg:
                        logger.warning(
                            f"Skipping malformed message in {file_path}: {msg.get('message_id', 'N/A')}"
                        )
                        continue

                    # Check if message already exists (simple check by PK)
                    cursor.execute(
                        """
                        SELECT 1 FROM raw.telegram_messages
                        WHERE message_id = %s AND channel_username = %s
                    """,
                        (msg["message_id"], msg["channel_username"]),
                    )  # Assuming (message_id, channel_username) is unique for now.
                    # Telethon message.id is unique per channel.
                    if cursor.fetchone():
                        # logger.debug(f"Message {msg['message_id']} from {channel_username} already exists. Skipping.")
                        continue  # Skip if message already exists

                    # Insert new message
                    cursor.execute(
                        """
                        INSERT INTO raw.telegram_messages (
                            message_id, channel_username, scraped_date, message_data
                        ) VALUES (%s, %s, %s, %s)
                    """,
                        (
                            msg["message_id"],
                            msg["channel_username"],
                            scraped_date_str,  # Use the date from the directory name
                            json.dumps(msg),  # Store the entire message as JSONB
                        ),
                    )
                    new_records_count += 1
                    if new_records_count % 100 == 0:
                        logger.info(
                            f"Inserted {new_records_count} new records so far..."
                        )

                conn.commit()  # Commit after processing each file (or batch of files)
                logger.info(
                    f"Successfully processed and loaded data from {file_path}. New records in this file: {new_records_count - (new_records_count - len(messages)) if new_records_count > 0 else 0}"
                )

            except json.JSONDecodeError as jde:
                logger.error(f"Invalid JSON in file {file_path}: {jde}", exc_info=True)
                conn.rollback()  # Rollback changes for this file if parsing fails
            except Exception as e:
                logger.error(f"Error processing file {file_path}: {e}", exc_info=True)
                conn.rollback()  # Rollback changes for this file on any other error

        logger.info(
            f"Finished loading raw data. Total new records inserted: {new_records_count}."
        )

    except Exception as e:
        logger.critical(
            f"Fatal error during raw data loading process: {e}", exc_info=True
        )
        if conn:
            conn.rollback()  # Ensure rollback on fatal errors
    finally:
        if conn:
            conn.close()


# --- 4. Main Execution ---
if __name__ == "__main__":
    logger.info("Starting raw data loading process to PostgreSQL.")
    load_json_to_postgres()
    logger.info("Raw data loading process finished.")
