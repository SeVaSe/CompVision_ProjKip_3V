import subprocess
import sys

import cv2

from classes.class_video_capt import NumbVideoCapt


def run_detect_peop_all():
    try:
        numbVC = NumbVideoCapt()
        cap = cv2.VideoCapture(numbVC.numb)
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
        print("С обнаружением людей чет не так...")
        cap.release()
        cv2.destroyAllWindows()
        # Запуск меню после возникновения ошибки
        subprocess.run([sys.executable, "menu.py"])
        sys.exit()