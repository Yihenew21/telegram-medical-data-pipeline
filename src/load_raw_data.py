# src/load_raw_data.py
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

# Path to your raw data lake for Telegram messages
RAW_TELEGRAM_MESSAGES_PATH = os.path.join(
    os.path.dirname(os.path.abspath(__file__)), "../data/raw/telegram_messages"
)

# Path to your raw data lake for YOLO detections
RAW_YOLO_DETECTIONS_PATH = os.path.join(
    os.path.dirname(os.path.abspath(__file__)), "../data/raw/yolo_detections"
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


def create_telegram_messages_table(cursor):
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

        CREATE INDEX IF NOT EXISTS idx_raw_channel_date
        ON raw.telegram_messages (channel_username, scraped_date);
    """
    )
    logger.info("Checked/created 'raw.telegram_messages' table.")


def create_yolo_detections_table(cursor):  # NEW FUNCTION
    """
    Creates the 'raw.yolo_detections' table if it doesn't exist.
    Stores the entire JSON array of detections from a file as JSONB.
    """
    cursor.execute(
        """
        CREATE SCHEMA IF NOT EXISTS raw;

        CREATE TABLE IF NOT EXISTS raw.yolo_detections (
            id SERIAL PRIMARY KEY,
            detection_data JSONB NOT NULL,
            file_name VARCHAR(255) NOT NULL, -- To track which file it came from
            inserted_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        );

        CREATE INDEX IF NOT EXISTS idx_yolo_inserted_at
        ON raw.yolo_detections (inserted_at);
    """
    )
    logger.info("Checked/created 'raw.yolo_detections' table.")


# --- 3. Data Loading Logic ---
def load_telegram_messages_to_postgres():  # Renamed existing function
    """
    Reads JSON files from the telegram_messages data lake and loads them into raw.telegram_messages.
    Handles incremental loading by checking existing data.
    """
    conn = None
    try:
        conn = get_db_connection()
        conn.autocommit = False
        cursor = conn.cursor()

        create_telegram_messages_table(cursor)

        json_files = glob.glob(
            os.path.join(RAW_TELEGRAM_MESSAGES_PATH, "**", "*.json"), recursive=True
        )
        logger.info(f"Found {len(json_files)} Telegram message JSON files to process.")

        new_records_count = 0
        for file_path in json_files:
            try:
                path_parts = file_path.split(os.sep)
                scraped_date_str = path_parts[-2]
                channel_username = os.path.basename(file_path).replace(".json", "")

                with open(file_path, "r", encoding="utf-8") as f:
                    messages = json.load(f)

                if not messages:
                    logger.warning(f"File {file_path} contains no messages. Skipping.")
                    continue

                for msg in messages:
                    if "message_id" not in msg or "channel_username" not in msg:
                        logger.warning(
                            f"Skipping malformed message in {file_path}: {msg.get('message_id', 'N/A')}"
                        )
                        continue

                    cursor.execute(
                        """
                        SELECT 1 FROM raw.telegram_messages
                        WHERE message_id = %s AND channel_username = %s
                    """,
                        (msg["message_id"], msg["channel_username"]),
                    )
                    if cursor.fetchone():
                        continue

                    cursor.execute(
                        """
                        INSERT INTO raw.telegram_messages (
                            message_id, channel_username, scraped_date, message_data
                        ) VALUES (%s, %s, %s, %s)
                    """,
                        (
                            msg["message_id"],
                            msg["channel_username"],
                            scraped_date_str,
                            json.dumps(msg),
                        ),
                    )
                    new_records_count += 1
                    if new_records_count % 100 == 0:
                        logger.info(
                            f"Inserted {new_records_count} new Telegram message records so far..."
                        )

                conn.commit()
                logger.info(
                    f"Successfully processed and loaded Telegram messages from {file_path}."
                )

            except json.JSONDecodeError as jde:
                logger.error(f"Invalid JSON in file {file_path}: {jde}", exc_info=True)
                conn.rollback()
            except Exception as e:
                logger.error(f"Error processing file {file_path}: {e}", exc_info=True)
                conn.rollback()

        logger.info(
            f"Finished loading Telegram message raw data. Total new records inserted: {new_records_count}."
        )

    except Exception as e:
        logger.critical(
            f"Fatal error during Telegram message raw data loading process: {e}",
            exc_info=True,
        )
        if conn:
            conn.rollback()
    finally:
        if conn:
            conn.close()


def load_yolo_detections_to_postgres():  # NEW FUNCTION
    """
    Reads YOLO detection JSON files and loads their content into raw.yolo_detections.
    Each file (which contains an array of detections) is loaded as one JSONB record.
    """
    conn = None
    try:
        conn = get_db_connection()
        conn.autocommit = False
        cursor = conn.cursor()

        create_yolo_detections_table(cursor)

        json_files = glob.glob(
            os.path.join(RAW_YOLO_DETECTIONS_PATH, "yolo_detections_*.json"),
            recursive=False,  # Not recursive for yolo files
        )
        logger.info(f"Found {len(json_files)} YOLO detection JSON files to process.")

        new_files_loaded_count = 0
        for file_path in json_files:
            file_name = os.path.basename(file_path)
            try:
                # Check if this file has already been loaded
                cursor.execute(
                    """
                    SELECT 1 FROM raw.yolo_detections
                    WHERE file_name = %s
                """,
                    (file_name,),
                )
                if cursor.fetchone():
                    logger.debug(f"File {file_name} already loaded. Skipping.")
                    continue

                with open(file_path, "r", encoding="utf-8") as f:
                    detections_array = json.load(f)

                if not detections_array:
                    logger.warning(
                        f"File {file_path} contains no detections. Skipping."
                    )
                    continue

                # Insert the entire JSON array as one record
                cursor.execute(
                    """
                    INSERT INTO raw.yolo_detections (detection_data, file_name)
                    VALUES (%s::jsonb, %s)
                """,
                    (json.dumps(detections_array), file_name),
                )
                conn.commit()
                new_files_loaded_count += 1
                logger.info(f"Successfully loaded YOLO detections from {file_name}.")

            except json.JSONDecodeError as jde:
                logger.error(f"Invalid JSON in file {file_path}: {jde}", exc_info=True)
                conn.rollback()
            except Exception as e:
                logger.error(f"Error processing file {file_path}: {e}", exc_info=True)
                conn.rollback()

        logger.info(
            f"Finished loading YOLO detection raw data. Total new files loaded: {new_files_loaded_count}."
        )

    except Exception as e:
        logger.critical(
            f"Fatal error during YOLO detection raw data loading process: {e}",
            exc_info=True,
        )
        if conn:
            conn.rollback()
    finally:
        if conn:
            conn.close()


# --- 4. Main Execution ---
if __name__ == "__main__":
    logger.info("Starting raw data loading process to PostgreSQL.")
    load_telegram_messages_to_postgres()  # Call the Telegram messages loader
    load_yolo_detections_to_postgres()  # Call the NEW YOLO detections loader
    logger.info("Raw data loading process finished.")
