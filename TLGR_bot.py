import telebot
import sqlite3
import re
import time
import requests

path_toDB = 'data/DataBases/tlgr.db'
API_TOKEN = '7117476620:AAEqnvsrpp74V_YtsMsn4uUvrTtNyXnoHoE'
bot = telebot.TeleBot(API_TOKEN)

ch_EN = [0, 1, 2, 3, 4, 5, 6, 7, 8, 9, 'A', 'B', 'C', 'E', 'H', 'K', 'M', 'O', 'P', 'T', 'X', 'Y', 'A', 'B', 'C', 'E',
         'H', 'K', 'M', 'O', 'P', 'T', 'X', 'Y', 'A', 'B', 'C', 'E', 'H', 'K', 'M', 'O', 'P', 'T', 'X', 'Y', 'A', 'B',
         'C', 'E', 'H', 'K', 'M', 'O', 'P', 'T', 'X', 'Y']
ch_RU = [0, 1, 2, 3, 4, 5, 6, 7, 8, 9, 'А', 'В', 'С', 'К', 'Н', 'К', 'М', 'О', 'Р', 'Т', 'Х', 'У', 'а', 'в', 'с', 'е',
         'н', 'к', 'м', 'о', 'р', 'т', 'х', 'у', 'A', 'B', 'C', 'E', 'H', 'K', 'M', 'O', 'P', 'T', 'X', 'Y', 'a', 'b',
         'c', 'e', 'h', 'k', 'm', 'o', 'p', 't', 'x', 'y']


def send_number(chat_id, id, number):


    data = {"chat_id": chat_id, "caption": str(number)}
    url = f"https://api.telegram.org/bot{API_TOKEN}/sendPhoto?chat_id={chat_id}"
    with open(f'D:\\History\\{id}.jpg', "rb") as image_file:
        requests.post(url, data=data, files={"photo": image_file})


def num_normalize(text):
    number = ''
    for ch in text:

        for i, ru in enumerate(ch_RU):
            if ch == str(ru):
                number = number + str(ch_EN[i])
            else:
                pass

    return number


@bot.message_handler(commands=['start'])
def send_welcome(message):
    conn = sqlite3.connect(path_toDB)
    c = conn.cursor()
    c.execute("CREATE TABLE IF NOT EXISTS TG_users (user_id INTEGER , acsess INTEGER)")
    res = c.execute(f"SELECT * FROM TG_users WHERE user_id=?", (message.from_user.id,)).fetchone()

    if res is None:

        c.execute(f"INSERT INTO TG_users (user_id, acsess) VALUES (?, 0)", (message.from_user.id,))
        conn.commit()
        conn.close()
        bot.reply_to(message, f'Введи пароль')

    elif res[1] == 0:

        bot.reply_to(message, f'Введи пароль')
        conn.close()

    else:
        bot.reply_to(message, f'Скинь номера')
        conn.close()


@bot.message_handler()
def send_welcome(message):

    conn = sqlite3.connect(path_toDB)
    c = conn.cursor()
    res = c.execute(f"SELECT * FROM TG_users WHERE user_id=?", (message.from_user.id,)).fetchone()

    # если пользователь авторизован
    if res[1] == 1:

        if re.match(r'\D{1}\d{3}\D{2}\d{2,3}|\D{1}\d{4}\d{2,3}|\d{4}\D{2}\d{2,3}', message.text) is not None:

            number = num_normalize(message.text)
            t = time.strftime("%m-%Y", time.localtime())
            conn = sqlite3.connect(f'data/DataBases/history-{t}.db')
            c = conn.cursor()
            c.execute("CREATE TABLE IF NOT EXISTS History (id INTEGER PRIMARY KEY, datetime TEXT, number TEXT, route INTEGER) ")
            res = c.execute("SELECT * FROM History WHERE number=? ORDER BY time DESC", (number,)).fetchmany(10)
            conn.close()

            mess = 'Последние записи (максимум 10)\n'
            for r in res:
                mess = mess + f'\id{str(r[0])} Время {str(r[1])}, Номер - {str(r[2])}\n'

            bot.reply_to(message, mess)

        elif re.match(r"id\d{1,6}", message.text) is not None:

            id = re.findall(r"\d{1,6}", message.text)[0]
            photo = open(f'D:\\History\\{id}.jpg', "rb")
            bot.send_photo(message.from_user.id, photo)




    else:

        if message.text == 'vxO8sY8dr4MKDFLd':
            conn = sqlite3.connect(path_toDB)
            c = conn.cursor()
            c.execute(f"UPDATE TG_users SET acsess = 1 WHERE user_id=?", (message.from_user.id,))
            conn.commit()
            conn.close()

            bot.reply_to(message, f'Пароль принят')

        else:
            bot.reply_to(message, f'Неверный пароль')


bot.infinity_polling()
