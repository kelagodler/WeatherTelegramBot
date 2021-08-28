import telebot
import os

from telebot.types import Message

TOKEN = os.getenv('TOKEN')
bot = telebot.TeleBot(TOKEN)


@bot.message_handler(commands=['start'])
def send_welcome(message: Message):
    welcome_text = "Welcome!"
    bot.reply_to(message=message, text=welcome_text)


@bot.message_handler(func=lambda message: True)
def echo(message: Message):
    user_text = message.text.lower()

    if "ты" in user_text:
        answer_text = f"Сам {user_text}!"
    else:
        answer_text = f"Сам ты {user_text}!"
    bot.reply_to(message=message, text=answer_text.lower().capitalize())


bot.polling()
