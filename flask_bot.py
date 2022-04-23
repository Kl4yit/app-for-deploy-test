#!/usr/bin/env python
# -*- coding: utf-8 -*-

# This is a simple echo bot using decorators and webhook with flask
# It echoes any incoming text messages and does not use the polling method.

import logging
import time
from isIsomorphic import is_isomorphic

import flask

import telebot

API_TOKEN = '5318524118:AAFO6DrlWi-WCRPdXm50S7W64fJga0C2-kg'

WEBHOOK_HOST = ''
WEBHOOK_PORT = 8443  # 443, 80, 88 or 8443 (port need to be 'open')
WEBHOOK_LISTEN = '0.0.0.0'  # In some VPS you may need to put here the IP addr

WEBHOOK_SSL_CERT = './webhook_cert.pem'  # Path to the ssl certificate
WEBHOOK_SSL_PRIV = './webhook_pkey.pem'  # Path to the ssl private key

# Quick'n'dirty SSL certificate generation:
#
# openssl genrsa -out webhook_pkey.pem 2048
# openssl req -new -x509 -days 3650 -key webhook_pkey.pem -out webhook_cert.pem
#
# When asked for "Common Name (e.g. server FQDN or YOUR name)" you should reply
# with the same value in you put in WEBHOOK_HOST

WEBHOOK_URL_BASE = "https://%s:%s" % (WEBHOOK_HOST, WEBHOOK_PORT)
WEBHOOK_URL_PATH = "/%s/" % (API_TOKEN)

logger = telebot.logger
telebot.logger.setLevel(logging.INFO)

bot = telebot.TeleBot(API_TOKEN)

app = flask.Flask(__name__)


# Empty webserver index, return nothing, just http 200
@app.route('/', methods=['GET', 'HEAD'])
def index():
    return ''


# Process webhook calls
@app.route(WEBHOOK_URL_PATH, methods=['POST'])
def webhook():
    if flask.request.headers.get('content-type') == 'application/json':
        json_string = flask.request.get_data().decode('utf-8')
        update = telebot.types.Update.de_json(json_string)
        bot.process_new_updates([update])
        return ''
    else:
        flask.abort(403)


# # Handle '/start' and '/help'
# @bot.message_handler(commands=['help', 'start'])
# def send_welcome(message):
#     bot.reply_to(message,
#                  ("Hi there, I am EchoBot.\n"
#                   "I am here to echo your kind words back to you."))
#
#
# # Handle all other messages
# @bot.message_handler(func=lambda message: True, content_types=['text'])
# def echo_message(message):
#     bot.reply_to(message, message.text)


INTRO = '''
Привет, я обычный бот, каких тысячи. Меня создавали, 
чтобы продавать фейерверки, но пока я могу только 
поговорить поговорить с вами или сказать изоморфны 
ли две матрицы друг другу

/speak - чтобы поговорить

/isomorphic - проверить изоморфность матриц
'''
MAT_TYPE = '''
Введите матрицу вида:

1 2 3 4
5 6 7 8
4 3 2 9
'''


@bot.message_handler(commands=['speak', 'isomorphic'])
def start1(message):
    global INTRO
    global MAT_TYPE
    if message.text == '/speak':
        bot.send_message(message.from_user.id, "Как тебя зовут?")
        bot.register_next_step_handler(message, PollUser().get_name) #следующий шаг – функция get_name
    elif message.text == '/isomorphic':
        bot.send_message(message.from_user.id, MAT_TYPE)
        bot.register_next_step_handler(message, Isom().get_matrix)  # следующий шаг – функция get_name
    else:
        bot.send_message(message.from_user.id, 'Напиши /help')


@bot.message_handler(commands=['help'])
def start1(message):
    global INTRO
    global MAT_TYPE
    if message.text == '/help':
        bot.send_message(message.from_user.id, INTRO)



@bot.message_handler(content_types=['text'])
def start2(message):
    bot.send_message(message.from_user.id, 'Напиши /help')


class Isom:
    def __init__(self):
        self.A = None
        self.B = None

    def get_matrix(self, message):
        self.A = self.parse_string(message)
        self._swap()
        if not self.A:
            bot.send_message(message.from_user.id, MAT_TYPE)
            bot.register_next_step_handler(message, self.get_matrix)
        else:
            self.calc_isom(message)

    def parse_string(self, message):
        a = message.text
        try:
            arr = [list(map(int, a)) for a in [i.split() for i in a.strip().split('\n')]]
        except BaseException:
            bot.send_message(message.from_user.id, 'Плохая матрица!')
            bot.register_next_step_handler(message, self.get_matrix)
            return
        return arr

    def _swap(self):
        self.A, self.B = self.B, self.A

    def calc_isom(self, message):
        res = is_isomorphic(self.A, self.B)
        if res:
            bot.send_message(message.from_user.id, 'Матрицы изоморфны')
            return
        bot.send_message(message.from_user.id, 'Матрицы не изоморфны')


class PollUser:

    def __init__(self):
        self.data = {}

    def get_name(self, message): #получаем фамилию

        self.data['name'] = message.text
        bot.send_message(message.from_user.id, 'Какая у тебя фамилия?')
        bot.register_next_step_handler(message, self.get_surname)

    def get_surname(self, message):
        self.data['surname'] = message.text
        bot.send_message(message.from_user.id, 'Сколько тебе лет?')
        bot.register_next_step_handler(message, self.get_age)



    def get_age(self, message):

        try:
            self.data['age'] = int(message.text)  # проверяем, что возраст введен корректно
        except Exception:
            bot.send_message(message.from_user.id, 'Цифрами, пожалуйста')
            bot.register_next_step_handler(message, self.get_age)
            return
        keyboard = telebot.types.InlineKeyboardMarkup()  # наша клавиатура
        key_yes = telebot.types.InlineKeyboardButton(text='Да', callback_data='yes')  # кнопка «Да»
        keyboard.add(key_yes)  # добавляем кнопку в клавиатуру
        key_no = telebot.types.InlineKeyboardButton(text='Нет', callback_data='no')
        keyboard.add(key_no)
        question = f"Тебе {str(self.data['age'])} лет, тебя зовут {self.data['name']} {self.data['surname']}?"
        bot.send_message(message.from_user.id, text=question, reply_markup=keyboard)


@bot.callback_query_handler(func=lambda call: True)
def callback_worker(call):
    if call.data == "yes": #call.data это callback_data, которую мы указали при объявлении кнопки
        ... #код сохранения данных, или их обработки
        bot.send_message(call.message.chat.id, 'Запомню : )')
    elif call.data == "no":
        bot.send_message(call.message.chat.id, 'Мне поебать')
        ... #переспрашиваем






# Remove webhook, it fails sometimes the set if there is a previous webhook
bot.remove_webhook()

time.sleep(0.1)

# Set webhook
bot.set_webhook(url=WEBHOOK_URL_BASE + WEBHOOK_URL_PATH,
                certificate=open(WEBHOOK_SSL_CERT, 'r'))

# Start flask server
if __name__ == '__main__':
    app.run(host=WEBHOOK_LISTEN,
            port=WEBHOOK_PORT,
            ssl_context=(WEBHOOK_SSL_CERT, WEBHOOK_SSL_PRIV),
            debug=True)
