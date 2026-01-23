import requests

from settings import TELEGRAM_BOT_TOKEN

TELEGRAM_CHAT_ID = '-1002172002211'
# TELEGRAM_CHAT_ID = '-5006656044'  # test

def send_to_telegram(text_to_send):
    send_to_telegram_chat(text_to_send, TELEGRAM_CHAT_ID)


def send_to_telegram_chat(text_to_send, chat_id, reply_to_message_id=None):
    url = f'https://api.telegram.org/bot{TELEGRAM_BOT_TOKEN}/sendMessage'
    payload = {
        'chat_id': chat_id,
        'text': text_to_send,
        'parse_mode': 'Markdown'
    }
    if reply_to_message_id is not None:
        payload['reply_to_message_id'] = reply_to_message_id
    try:
        response = requests.post(url, json=payload)
        response.raise_for_status()
        print(f"✅ Сообщение отправлено в Telegram!")
    except requests.exceptions.RequestException as e:
        print(f"❌ Ошибка при отправке в Telegram: {e}")


def send_photo_to_telegram_chat(photo_bytes, chat_id, reply_to_message_id=None, caption=None):
    url = f'https://api.telegram.org/bot{TELEGRAM_BOT_TOKEN}/sendPhoto'
    payload = {
        'chat_id': chat_id,
    }
    if reply_to_message_id is not None:
        payload['reply_to_message_id'] = reply_to_message_id
    if caption:
        payload['caption'] = caption
    files = {
        'photo': ('image.jpg', photo_bytes, 'image/jpeg'),
    }
    try:
        response = requests.post(url, data=payload, files=files)
        response.raise_for_status()
        print(f"✅ Картинка отправлена в Telegram!")
    except requests.exceptions.RequestException as e:
        print(f"❌ Ошибка при отправке картинки в Telegram: {e}")
