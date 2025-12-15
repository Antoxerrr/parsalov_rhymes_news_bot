from post_generator import PostGenerator
from telegram import send_to_telegram

send_to_telegram(PostGenerator().generate())
