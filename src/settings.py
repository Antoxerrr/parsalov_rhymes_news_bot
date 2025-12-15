import os

from dotenv import load_dotenv

load_dotenv()

VK_SERVICE_TOKEN = os.getenv('VK_SERVICE_TOKEN')
YANDEX_CLOUD_API_KEY = os.getenv('YANDEX_CLOUD_API_KEY')
YANDEX_CLOUD_FOLDER = os.getenv('YANDEX_CLOUD_FOLDER')
TELEGRAM_BOT_TOKEN = os.getenv('TELEGRAM_BOT_TOKEN')
