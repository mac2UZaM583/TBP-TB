import telebot
from apitoken import token as API_TOKEN, channel_id as CHANNEL_ID

# Создаем экземпляр бота
bot = telebot.TeleBot(API_TOKEN)

def send_message_to_channel(message_text):
    try:
        bot.send_message(CHANNEL_ID, message_text)
    except Exception as e:
        print(f"Ошибка при отправке сообщения: {e}")