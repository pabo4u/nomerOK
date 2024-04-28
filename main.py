import sys
from backend import *


model = YOLO("data/YOLO_models/car&carplate.pt")
modelOCR = YOLO("data/YOLO_models/OCR.pt")
vid = "rtsp://admin:Admin123@192.168.10.100:554/11"


def main():

    results = model(vid, stream=True, conf=0.6, classes=[0,1])

    for result in results:

        t = time.time()

        result = Predictor(result)
        result.carplate_extrate()
        numbers = result.carplate_OCR()

        frame = cv.resize(result.frame, (800, 600))
        endT = str(round((time.time() - t) * 1000, 1))
        gpu_temp, gpu_load = get_gpu_info()
        FPS = f'ms {endT} : gpuTemp {gpu_temp} : gpuLoad {gpu_load}'

        cv.putText(frame, FPS, (5, 15), cv.FONT_HERSHEY_SIMPLEX, 0.5, (255, 255, 255), 1, cv.LINE_AA)
        cv.imshow("frame", frame)


        if len(numbers) == 0:
            break
        #если номера найдены
        save_carplate(numbers, result.frame)

        if cv.waitKey(33) & 0xFF == ord('q'):
            sys.exit()


if __name__ == "__main__":
    main()
