from unicodedata import category

import telebot
import config
import requests
import json
import random
from telebot import types

bot = telebot.TeleBot(config.TOKEN)

url_news = lambda category_name: f'https://inshorts-news.vercel.app/{category_name}'
url_cat = lambda tag: f'https://cataas.com/cat/{tag}'


# welcome message handler
@bot.message_handler(commands=['start'])
def start(message):
    bot.send_message(message.chat.id, 'Привет! Я-какашечка! Могу высрать новости из интернета по некоторым категориям')
    getinfo(message)


# side message handler
@bot.message_handler(content_types=['text'])
def another_message(message):
    if message.text == 'Вернуться':
        getinfo(message)
    elif message.text == 'кота':
        get_cat(message)
        contin(message)
    else:
        bot.send_message(message.chat.id, 'Можешь не пытаться что либо писать, просто тыкай на кнопки!')
        getinfo(message)


def get_cat(message):
    res = requests.get('https://cataas.com/api/tags')

    obj = json.loads(res.text)
    try:
        bot.send_photo(message.chat.id, url_cat(random.choice(obj)))
    except Exception:
        get_cat(message)


# get info + inline keyboard
def getinfo(message):
    markup = types.InlineKeyboardMarkup(row_width=2)
    item0 = types.InlineKeyboardButton('наука', callback_data='science')
    item1 = types.InlineKeyboardButton('бизнесс', callback_data='business')
    item2 = types.InlineKeyboardButton('спорт', callback_data='sports')
    item3 = types.InlineKeyboardButton('дать кота', callback_data='cat')
    markup.row(item0, item1, item2)
    markup.row(item3)
    bot.send_message(message.chat.id, 'Кликни на кнопку', reply_markup=markup)


def json_request(url: str) -> dict:
    response = requests.get(url)
    obj = json.loads(response.text)
    num = obj['count-articles']
    rand = random.randint(0, num - 1)
    new_obj = obj['data'][rand]
    return new_obj


def complite_new(obj: dict) -> str:
    return f"<b><u>{obj['title']}</u></b>\n\n" \
           f"{obj['decription']}\n\n" \
           f"\n\nAuthor: {obj['author']}\n\n"


def contin(message):
    markup = types.ReplyKeyboardMarkup(resize_keyboard=True)
    item1 = types.KeyboardButton('Вернуться')
    item2 = types.KeyboardButton('кота')
    markup.add(item1, item2)
    bot.send_message(message.chat.id, 'Че дальше', reply_markup=markup)


def step(message):
    markup = types.InlineKeyboardMarkup(row_width=2)
    button = types.InlineKeyboardButton('Назад', callback_data='start')
    markup.add(button)
    bot.send_message(message.chat.id, 'Не удалось получить информацию из интернета. Попробуйте',
                     reply_markup=markup)


# data processing
@bot.callback_query_handler(func=lambda callback: True)
def callback_message(callback):
    if callback.data == 'start':
        getinfo(callback.message)
    elif callback.data == 'cat':
        get_cat(callback.message)
        contin(callback.message)
    else:
        try:

            new = json_request(url_news(callback.data))
            print(new)
            url = new['read-more']
            markup = types.InlineKeyboardMarkup(row_width=2)
            button = types.InlineKeyboardButton('Читать еще', url=url)
            markup.add(button)
            bot.send_photo(callback.message.chat.id, photo=new['images'], caption=complite_new(new),
                           parse_mode='HTML',
                           reply_markup=markup)
            contin(callback.message)
        except Exception as e:
            bot.send_message(callback.message.chat.id, type(e))
            step(callback.message)


bot.polling(none_stop=True)
