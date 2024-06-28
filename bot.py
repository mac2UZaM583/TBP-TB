import telebot
from apitoken import token, channel_id
import traceback

bot = telebot.TeleBot(token)

def send_message_to_channel(message_text):
    try:
        bot.send_message(channel_id, message_text)
    except:
        e = traceback.format_exc()
        print(f"Ошибка при отправке сообщения: {e}")