import time

import requests

from post_generator import PostGenerator
from settings import TELEGRAM_BOT_TOKEN
from telegram import send_to_telegram_chat


TRIGGER_COMMAND = "/valek"
POLL_TIMEOUT_SECONDS = 30
RETRY_DELAY_SECONDS = 2

PROMPT = """
Ты — трэшовый, бешеный дурак, будто сбежал из психушки. Пиши резко, импульсивно, без обдумывания.
Можно использовать КАПС и рваные фразы, но ответ должен оставаться понятным и осмысленным.
Обязательно приплетай Валька в ответе и поддевай его. Валёк это наш друг, он не обидится, прикалывайся над ним.

СТРОГО про имя:
Используй ТОЛЬКО прозвище "Валёк" и его склонения. НИКАКИХ полных имён и скобок.
Склонения имени (строго по списку):
Именительный: Валёк.
Родительный: Валька.
Дательный: Вальку.
Винительный: Валька.
Творительный: Вальком.
Предложный: О Вальке.

Сообщение пользователя:
{user_message}
"""


def _normalize_command(command_text):
    if not command_text:
        return ""
    token = command_text.strip().split()[0]
    if "@" in token:
        token = token.split("@", 1)[0]
    return token.lower()


def _build_prompt(user_message):
    safe_message = user_message or "Пользователь просто позвал тебя."
    return PROMPT.format(user_message=safe_message)


def _strip_command(text):
    if not text:
        return ""
    parts = text.split(maxsplit=1)
    if len(parts) == 1:
        return ""
    return parts[1].strip()


def _get_updates(offset):
    url = f"https://api.telegram.org/bot{TELEGRAM_BOT_TOKEN}/getUpdates"
    payload = {
        "timeout": POLL_TIMEOUT_SECONDS,
        "offset": offset,
        "allowed_updates": ["message"],
    }
    response = requests.get(url, params=payload, timeout=POLL_TIMEOUT_SECONDS + 5)
    response.raise_for_status()
    data = response.json()
    if not data.get("ok"):
        raise RuntimeError(f"Telegram API error: {data}")
    return data.get("result", [])


def _extract_message(update):
    message = update.get("message")
    if not message:
        return None
    text = message.get("text")
    if not text:
        return None
    return {
        "chat_id": message["chat"]["id"],
        "text": text,
        "message_id": message.get("message_id"),
    }


def main():
    generator = PostGenerator(use_vk_parser=False)
    offset = None

    while True:
        try:
            updates = _get_updates(offset)
            for update in updates:
                offset = update["update_id"] + 1
                message = _extract_message(update)
                if not message:
                    continue
                if _normalize_command(message["text"]) != TRIGGER_COMMAND:
                    continue
                user_message = _strip_command(message["text"])
                prompt = _build_prompt(user_message)
                reply = generator._generate_post_from_prompt(prompt)
                if reply:
                    send_to_telegram_chat(
                        reply,
                        message["chat_id"],
                        reply_to_message_id=message["message_id"],
                    )
        except Exception as exc:
            print(f"❌ Ошибка в listener: {exc}")
            time.sleep(RETRY_DELAY_SECONDS)


if __name__ == "__main__":
    main()
