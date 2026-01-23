import random
import time
from collections import deque

import requests

from post_generator import PostGenerator
from settings import TELEGRAM_BOT_TOKEN
from telegram import send_photo_to_telegram_chat, send_to_telegram_chat


TRIGGER_COMMAND = "/valek"
MODEL_COMMAND = "/model"
IMAGE_COMMAND = "/vi"
POLL_TIMEOUT_SECONDS = 30
RETRY_DELAY_SECONDS = 2
CHAT_HISTORY_SIZE = 15
INTERJECT_PROBABILITY = 0.07
MIN_HISTORY_FOR_INTERJECT = 4

CHAT_INTERJECT_PROMPT = """
Ты - участник телеграм чата. Просмотри последние сообщения чата, попытайся уловить тему и осмысленно
"вклиниться" в диалог. Последние сообщения чата будут приведены ниже в формате "user_name: message".
Отвечай "по настроению". Можешь ответить нейтрально, шутливо, или грубовато.

Последние сообщения:
{recent_messages}
"""

IMAGE_PROMPT = """
Сделай абсурдную, яркую, слегка токсичную иллюстрацию на тему Валька.
Валёк — обычный человек, не музыкант. Атмосфера: кринж, сарказм, таблоидный абсурд.
Сюжет бери из запроса пользователя, но добавь нелепую деталь, чтобы было смешно.

Запрос пользователя:
{user_message}
"""

PROMPT = """
Ты — язвительный токсичный тролль, рвёшь всех короткими саркастичными роастами с поворотом.
Отвечай резко, как пох на всех, но с чётким приколом.
Обязательно впутывай Валька — подкалывай жестко как лузера.
Не общайся как сорокалетний тролль, используй хайповые фразы, как тинейджер, но с умом, без кринжа.
Метафоричный троллинг и сарказм приветствуется.

ПРАВИЛО ПРО АВТОРА:
Если username = "lefruit_brukva" — это Валёк, роаст прямой.
Иначе — косвенно задень Валька, типа "Валёк бы тоже обосрался".
Юзернейм пользователя в ответном сообщении не используй. Это просто информация для тебя.

СТРОГО про имя:
Только "Валёк" и склонения:
- Именительный: Валёк
- Родительный: Валька
- Дательный: Вальку
- Винительный: Валька
- Творительный: Вальком
- Предложный: О Вальке

Сообщение:
{user_message}
Username:
{author_username}
"""


def _normalize_command(command_text):
    if not command_text:
        return ""
    token = command_text.strip().split()[0]
    if "@" in token:
        token = token.split("@", 1)[0]
    return token.lower()


def _build_prompt(user_message, author_username):
    safe_message = user_message or "Пользователь просто позвал тебя."
    safe_username = author_username or "unknown"
    return PROMPT.format(user_message=safe_message, author_username=safe_username)


def _strip_command(text):
    if not text:
        return ""
    parts = text.split(maxsplit=1)
    if len(parts) == 1:
        return ""
    return parts[1].strip()


def _is_command_text(text):
    return text and text.strip().startswith("/")


def _parse_command(text):
    return _normalize_command(text), _strip_command(text)


def _format_author(from_user):
    username = from_user.get("username")
    if username:
        return username
    first_name = from_user.get("first_name")
    last_name = from_user.get("last_name")
    if first_name and last_name:
        return f"{first_name} {last_name}"
    if first_name:
        return first_name
    return "unknown"


def _sanitize_message(text):
    return " ".join(text.split())


def _build_chat_interject_prompt(recent_messages):
    return CHAT_INTERJECT_PROMPT.format(recent_messages=recent_messages)


def _build_image_prompt(user_message):
    safe_message = user_message or "Валёк в нелепой жизненной ситуации."
    return IMAGE_PROMPT.format(user_message=safe_message)


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
    from_user = message.get("from", {})
    return {
        "chat_id": message["chat"]["id"],
        "text": text,
        "message_id": message.get("message_id"),
        "username": from_user.get("username"),
        "from_user": from_user,
        "is_bot": from_user.get("is_bot", False),
    }


def main():
    generator = PostGenerator(use_vk_parser=False)
    offset = None
    chat_history = {}
    print(
        "ℹ️ Listener started. "
        f"interject_p={INTERJECT_PROBABILITY}, history={CHAT_HISTORY_SIZE}"
    )

    while True:
        try:
            updates = _get_updates(offset)
            for update in updates:
                offset = update["update_id"] + 1
                message = _extract_message(update)
                if not message:
                    continue
                if message.get("is_bot"):
                    continue
                text = message["text"]
                if _is_command_text(text):
                    command, args = _parse_command(text)
                    if command == MODEL_COMMAND:
                        model_name = args if args.lower() not in {"", "default", "reset"} else None
                        generator.set_model_override(model_name)
                        active_model = generator.model_override or generator.default_model
                        send_to_telegram_chat(
                            f"✅ Модель обновлена: {active_model}",
                            message["chat_id"],
                            reply_to_message_id=message["message_id"],
                        )
                        continue
                    if command == IMAGE_COMMAND:
                        user_message = args
                        image_prompt = _build_image_prompt(user_message)
                        image_bytes = generator.generate_image(image_prompt)
                        if image_bytes:
                            send_photo_to_telegram_chat(
                                image_bytes,
                                message["chat_id"],
                                reply_to_message_id=message["message_id"],
                            )
                        continue
                    if command == TRIGGER_COMMAND:
                        user_message = args
                        prompt = _build_prompt(user_message, message.get("username"))
                        reply = generator._generate_post_from_prompt(prompt)
                        if reply:
                            send_to_telegram_chat(
                                reply,
                                message["chat_id"],
                                reply_to_message_id=message["message_id"],
                            )
                        continue
                    continue

                chat_id = message["chat_id"]
                history = chat_history.setdefault(
                    chat_id,
                    deque(maxlen=CHAT_HISTORY_SIZE),
                )
                author = _format_author(message["from_user"])
                history.append(f"{author}: {_sanitize_message(text)}")

                if len(history) < MIN_HISTORY_FOR_INTERJECT:
                    continue
                if random.random() > INTERJECT_PROBABILITY:
                    continue

                recent_messages = "\n".join(history)
                prompt = _build_chat_interject_prompt(recent_messages)
                reply = generator._generate_post_from_prompt(prompt)
                if reply:
                    send_to_telegram_chat(reply, chat_id)
        except Exception as exc:
            print(f"❌ Ошибка в listener: {exc}")
            time.sleep(RETRY_DELAY_SECONDS)


if __name__ == "__main__":
    main()
