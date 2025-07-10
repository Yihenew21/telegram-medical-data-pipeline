import os
from dotenv import load_dotenv

# Load environment variables from .env file
# By default, it looks for .env in the current directory or parent directories
load_dotenv()

# Access environment variables
# We use os.getenv() for safety, returning None if the variable is not found
TELEGRAM_API_ID = os.getenv("TELEGRAM_API_ID")
TELEGRAM_API_HASH = os.getenv("TELEGRAM_API_HASH")
PHONE_NUMBER = os.getenv("PHONE_NUMBER")

POSTGRES_DB = os.getenv("POSTGRES_DB")
POSTGRES_USER = os.getenv("POSTGRES_USER")
POSTGRES_PASSWORD = os.getenv("POSTGRES_PASSWORD")
POSTGRES_HOST = os.getenv("POSTGRES_HOST")
POSTGRES_PORT = os.getenv("POSTGRES_PORT")

# Example usage (for testing)
if __name__ == "__main__":
    print("--- Environment Variables Loaded ---")
    print(f"Telegram API ID: {TELEGRAM_API_ID[:4]}...")  # Mask part of it
    print(f"Telegram API Hash: {TELEGRAM_API_HASH[:4]}...")  # Mask part of it
    print(f"Phone Number: {PHONE_NUMBER}")
    print(f"Postgres DB: {POSTGRES_DB}")
    print(f"Postgres User: {POSTGRES_USER}")
    print(f"Postgres Host: {POSTGRES_HOST}")
    print(f"Postgres Port: {POSTGRES_PORT}")
    print(
        f"Postgres Password: {'*' * len(POSTGRES_PASSWORD) if POSTGRES_PASSWORD else 'None'}"
    )  # Mask password
    print("----------------------------------")

    # You can also set a default value if the env var is not found
    SOME_DEFAULT = os.getenv("NON_EXISTENT_VAR", "default_value")
    print(f"Non-existent var (with default): {SOME_DEFAULT}")
