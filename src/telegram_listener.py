import time

import requests

from post_generator import PostGenerator
from settings import TELEGRAM_BOT_TOKEN
from telegram import send_to_telegram_chat


TRIGGER_COMMAND = "/valek"
MODEL_COMMAND = "/model"
POLL_TIMEOUT_SECONDS = 30
RETRY_DELAY_SECONDS = 2

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


def _parse_command(text):
    return _normalize_command(text), _strip_command(text)


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
                command, args = _parse_command(message["text"])
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
                if command != TRIGGER_COMMAND:
                    continue
                user_message = args
                prompt = _build_prompt(user_message, message.get("username"))
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
