import requests

from settings import TELEGRAM_BOT_TOKEN

# TELEGRAM_CHAT_ID = '-1002172002211'
TELEGRAM_CHAT_ID = '-5006656044'  # test

def send_to_telegram(text_to_send):
    url = f'https://api.telegram.org/bot{TELEGRAM_BOT_TOKEN}/sendMessage'
    payload = {
        'chat_id': TELEGRAM_CHAT_ID,
        'text': text_to_send,
        'parse_mode': 'Markdown'
    }
    try:
        response = requests.post(url, json=payload)
        response.raise_for_status()
        print(f"✅ Новость отправлена в Telegram!")
    except requests.exceptions.RequestException as e:
        print(f"❌ Ошибка при отправке в Telegram: {e}")
