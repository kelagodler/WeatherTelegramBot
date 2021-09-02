import telebot
import os
import requests
import json

from telebot.types import Message, ReplyKeyboardMarkup, KeyboardButton
from pprint import pprint

TOKEN = os.getenv('TOKEN')
WEATHER_API = os.getenv('WEATHER_API')
ADMIN_ID = os.getenv('ADMIN_ID')

bot = telebot.TeleBot(TOKEN)


def hPa_to_mmHg(pressure):
    return round(pressure * 0.75006375541921, 2)


def kelvin_to_celsius(temperature):
    return round(temperature - 273.15, 2)


def deg_to_dir(degrees):
    if degrees >= 350 or degrees <= 10:
        return 'Северный'
    elif degrees > 10 or degrees < 80:
        return 'Сев.-Вост.'
    elif degrees >= 80 or degrees <= 100:
        return 'Восточный'
    elif degrees > 100 or degrees < 170:
        return 'Юго-Вост.'
    elif degrees >= 170 or degrees <= 190:
        return 'Южный'
    elif degrees > 190 or degrees < 260:
        return 'Юго-Запад.'
    elif degrees >= 260 or degrees <= 280:
        return 'Западный'
    else:
        return 'Сев.-Запад.'


def preprocess_content(message, content):
    content_dict = json.loads(content)

    try:
        city_name = content_dict['name']
        intro_text = f"Погода {city_name} ({content_dict['coord']['lon']}, {content_dict['coord']['lat']})\n"
        weather_desc = f"{content_dict['weather'][0]['description'].capitalize()}\n"
        weather_data = f"Температура: {kelvin_to_celsius(content_dict['main']['temp'])}°C\n" \
                       f"По ощущениям: {kelvin_to_celsius(content_dict['main']['feels_like'])}°C\n" \
                       f"Давление: {hPa_to_mmHg(content_dict['main']['pressure'])} мм рт. ст.\n" \
                       f"Влажность: {content_dict['main']['humidity']}%\n"
        wind_text = f"Ветер {deg_to_dir(content_dict['wind']['deg'])}, {content_dict['wind']['speed']}м/с"
    except KeyError:
        bot.reply_to(message=message, text=f"Сам {message.text}")
    else:
        output_text = intro_text + weather_desc + weather_data + wind_text
        bot.reply_to(message=message, text=output_text)


@bot.message_handler(commands=['start'])
def send_welcome(message: Message):
    welcome_text = "Привет! Введи название города или /location"
    bot.reply_to(message=message, text=welcome_text)
    user_id = message.from_user.id
    print(user_id)


@bot.message_handler(commands=['location'])
def send_location(message: Message):
    button = KeyboardButton(text="Отправить местоположение", request_location=True)
    keyboard = ReplyKeyboardMarkup(row_width=1, resize_keyboard=True)
    keyboard.add(button)
    bot.send_message(chat_id=message.from_user.id, text="Отправьте Координаты", reply_markup=keyboard)


@bot.message_handler(content_types=['location'])
def location(message: Message):
    url = 'https://api.openweathermap.org/data/2.5/weather?lat={lat}&lon={lon}&appid={api}&lang=ru'
    lon = message.location.longitude
    lat = message.location.latitude
    response = requests.get(url.format(lat=lat, lon=lon, api=WEATHER_API))
    content = response.content.decode(encoding='UTF-8')
    preprocess_content(message, content)


@bot.message_handler(func=lambda message: True)
def echo(message: Message):
    url = 'https://api.openweathermap.org/data/2.5/weather?q={city_name}&appid={api}&lang=ru'
    city_name = message.text.capitalize()[:20]
    response = requests.get(url.format(city_name=city_name, api=WEATHER_API))
    content = response.content.decode(encoding='UTF-8')
    preprocess_content(message, content)


bot.send_message(chat_id=ADMIN_ID, text="Бот запущен!")
bot.polling()

