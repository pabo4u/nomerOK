import time
import sqlite3
import re
import requests


black_list_numbers = ['M549YA05', 'P052CO05']


def send_warn(id, number):

    chat_id = 407474816
    _TOKEN = "7051164091:AAEjcgmczl_xu7cl32i6BA-dsTrgADH0kGM"

    data = {"chat_id": chat_id, "caption": str(number)}
    url = f"https://api.telegram.org/bot{_TOKEN}/sendPhoto?chat_id={chat_id}"
    with open(f'D:\\History\\{id}.jpg', "rb") as image_file:
        requests.post(url, data=data, files={"photo": image_file})


def main():

    while True:

        t = time.strftime("%m-%Y", time.localtime())
        conn = sqlite3.connect(f'data/DataBases/history-{t}.db')
        c = conn.cursor()
        c.execute("CREATE TABLE IF NOT EXISTS History (id INTEGER PRIMARY KEY, datetime TEXT, number TEXT, route INTEGER) ")
        res = c.execute("SELECT * FROM History ORDER BY id DESC").fetchone()
        conn.close()

        number = res[2]
        # номера ментов формата р 0520 05
        if re.match(r'\D{1}\d{4}\d{2,3}|\d{4}\D{2}\d{2,3}', number) is not None:
            send_warn(res[0], number)

        elif number in black_list_numbers:
            send_warn(res[0], number)

        time.sleep(1)



if __name__ == '__main__':
    main()