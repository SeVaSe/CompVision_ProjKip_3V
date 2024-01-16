import subprocess
import sys

import numpy as np
import cv2

def run_detect_peop_all():
    try:
        cap = cv2.VideoCapture(0)
        human_cascade = cv2.CascadeClassifier('data_set/haarcascade_fullbody.xml')

        while 1:
            ret, frame = cap.read()
            gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
            human = human_cascade.detectMultiScale(gray, 1.1, 4)

            for (x, y, w, h) in human:
                cv2.rectangle(frame, (x, y), (x + w, y + h), (255, 0, 0), 3)

            cv2.imshow('img', frame)
            if cv2.waitKey(1) & 0xFF == 27:
                break

        cap.release()
        cv2.destroyAllWindows()
        subprocess.run([sys.executable, "menu.py"])
        sys.exit()
    except:
        print("С пинг-понг чет не так")
        cap.release()
        cv2.destroyAllWindows()
        # Запуск меню после возникновения ошибки
        subprocess.run([sys.executable, "menu.py"])
        sys.exit()