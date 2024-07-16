import telebot
from settings__ import files_content
import traceback

bot = telebot.TeleBot(files_content['TOKEN'])

def send_message_to_channel(message_text):
    try:
        bot.send_message(files_content['ID'], message_text)
    except:
        traceback.print_exc()