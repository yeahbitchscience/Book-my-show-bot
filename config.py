import os
from dotenv import load_dotenv

load_dotenv()

TELEGRAM_BOT_TOKEN = os.getenv("TELEGRAM_BOT_TOKEN", "")
TELEGRAM_CHAT_ID = os.getenv("TELEGRAM_CHAT_ID", "")
TARGET_URL = os.getenv("TARGET_URL", "")
TARGET_FORMAT = os.getenv("TARGET_FORMAT", "IMAX").upper()

# If you specifically want to filter dates from elements, can be configured
# TARGET_DATES = os.getenv("TARGET_DATES", "").split(",")
