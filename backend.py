import cv2 as cv
import time
import numpy as np
from ultralytics import YOLO
import sqlite3
import re
import GPUtil

black_list_numbers = ['M549YA05', 'P052CO05']
ids_names = [0, 1, 2, 3, 4, 5, 6, 7, 8, 9, 'A', 'B', 'C', 'E', 'H', 'K', 'M', 'O', 'P', 'T', 'X', 'Y']
ids_namesRU = [0, 1, 2, 3, 4, 5, 6, 7, 8, 9, 'А', 'В', 'Е', 'К', 'М', 'Н', 'О', 'Р', 'С', 'Т', 'У', 'Х']
modelOCR = YOLO("data/YOLO_models/OCR.pt")


class Predictor:

    def __init__(self, result):

        self.result = result.cpu()
        self.frame = self.result.orig_img
        self.boxes = self.result.boxes.xyxy.numpy()
        self.cls = self.result.boxes.cls.numpy()

        self.carplates = []
        self.numbers = []

    def carplate_extrate(self):

        for i, box in enumerate(self.boxes):

            if int(self.cls[i]) == 1:

                x, y, w, h = np.array(box, np.int32)
                image = self.frame[y:h, x:w]

                width = 500
                height = int((500 / (w - x)) * (h - y))
                dim = (width, height)
                carplate = cv.resize(image, dim)

                self.carplates.append(carplate)

        return self.carplates

    def carplate_OCR(self):

        for carplate in self.carplates:
            carplate_result = modelOCR(carplate, conf=0.7, device='cuda:0', max_det=9)[0].boxes.cpu()

            boxes = carplate_result.xyxy.numpy()
            cls = carplate_result.cls.numpy()
            dir = np.argsort(boxes[:, 0])

            cls = cls[dir]

            number = ''

            for i in cls:
                i = int(i)
                number = number + str(ids_names[i])

            # обычные номера формата р 052 со 05
            if re.match(r'\D{1}\d{3}\D{2}\d{2,3}', number) is not None:
                self.numbers.append(number)

            # номера ментов формата р 0520 05
            elif re.match(r'\D{1}\d{4}\d{2,3}', number) is not None:
                self.numbers.append(number)

            # номера военных формата 0052 со 05
            elif re.match(r'd{4}\D{2}\d{2,3}', number) is not None:
                self.numbers.append(number)

        return self.numbers


def get_gpu_info():

    gpus = GPUtil.getGPUs()

    temp = str(gpus[0].temperature)
    load = str(gpus[0].load)

    return temp, load


def save_carplate(numbers, frame):

    t = time.strftime("%m-%Y", time.localtime())
    t_add = time.strftime("%d-%m-%Y, %H:%M:%S", time.localtime())
    conn = sqlite3.connect(f'data/DataBases/history-{t}.db')
    c = conn.cursor()
    c.execute("CREATE TABLE IF NOT EXISTS History (id INTEGER PRIMARY KEY, datetime TEXT, number TEXT, route INTEGER) ")

    for number in numbers:

        res = c.execute("SELECT * FROM History WHERE number=? ORDER BY id DESC", (number,)).fetchall()

        if len(res) == 0:

            c.execute('INSERT INTO History (datetime, number, route) VALUES (?, ?, ?)', (t_add, number, 0))
            conn.commit()
            name = c.execute("SELECT id FROM History ORDER BY id DESC").fetchone()
            conn.close()

            name = str(name[0]) + '.jpg'
            frame = cv.resize(frame, (800, 600))
            cv.imwrite(img=frame, filename=f'D:\\History\\' + name)
            return

        else:
            res = res[0]
            dtime = time.mktime(time.strptime(res[1], "%d-%m-%Y, %H:%M:%S"))

            if int(dtime) + 60 < int(time.time()):

                c.execute('INSERT INTO History (datetime, number, route) VALUES (?, ?, ?)', (t_add, number, 0))
                conn.commit()
                name = c.execute("SELECT id FROM History ORDER BY id DESC").fetchone()
                conn.close()

                name = str(name[0]) + '.jpg'
                frame = cv.resize(frame, (800, 600))
                cv.imwrite(img=frame, filename=f'D:\\History\\' + name)
                return

            else:

                conn.commit()
                conn.close()
                return
