import subprocess
import sys

import cv2
import mediapipe as mp
import pyautogui as pag
import mouse
import numpy as np
import time
from ai_mouse import HandTrackingModule as tht
from ai_mouse import CVfunc as func
from pycaw.pycaw import AudioUtilities, IAudioEndpointVolume
from ctypes import cast, POINTER
from comtypes import CLSCTX_ALL
import keyboard

from cv_video_capt import NumbVideoCapt


def run_cursor():
    try:
        # Камера ###########
        numbVC = NumbVideoCapt()
        cam = cv2.VideoCapture(numbVC.numb) # cv2.CAP_DSHOW
        wCam, hCam = 640, 480
        cam.set(3, wCam)
        cam.set(4, hCam)
        ####################

        # FPS ##############
        pTime = 0
        ####################

        # Детектор #########
        detector = tht.HandDetector(detectionCon=0.7, maxHands=2)
        ####################

        # Размер экрана ######
        wScr, hScr = pag.size()
        # print(wScr, hScr) # Размер экрана
        frameR = 100  # Уменьшение окна ввода
        ####################

        # Сглаживание мыши
        smooth = 4.6
        plocX, plocY = 0, 0
        clockX, clockY = 0, 0
        ####################

        # Громкость ###########

        devices = AudioUtilities.GetSpeakers()
        interface = devices.Activate(IAudioEndpointVolume._iid_, CLSCTX_ALL, None)
        volume = cast(interface, POINTER(IAudioEndpointVolume))
        volRange = volume.GetVolumeRange()
        print(volRange)
        minVol = volRange[0]
        maxVol = volRange[1]
        ####################



        # Флаг ##############

        flag = False
        flag4time = False
        #####################

        prevLenght = 0
        # Начало
        while (True):
            success, img = cam.read()
            img = cv2.flip(img, 1)
            hands, img = detector.findHands(img, flipType=False)
            # print(len(hands)) # Вывод количества рук



            if hands:
                # Рука 1
                hand1 = hands[0]
                lmList1 = hand1["lmList"] # Список 21 точки landmarks
                bbox1 = hand1["bbox"] # Bounding box информация x,y,w,h
                centerPoint1 = hand1["center"] # Центр руки cx,cy
                handType1 = hand1["type"] # Тип руки (левая\правая)
                fingers1 = detector.fingersUp(hand1)


                # Угол наклона + расстояние
                if len(lmList1) != 0:
                    coord17x, coord17y = lmList1[17][1:]
                    coord0x, coord0y = lmList1[0][1:]
                    coord5x, coord5y = lmList1[5][1:]
                    coord517x, coord517y = (coord17x + coord5x) / 2, (coord17y + coord5y) / 2
                    shx17 = coord17x - coord0x
                    shy17 = coord17y - coord0y
                    shx517 = coord517x - coord0x
                    shy517 = coord517y - coord0y
                    ratioalpha = np.arctan(0)
                    try:
                        alphaplusbeta = np.arctan(shx517 / shy517)
                    except ZeroDivisionError:
                        alphaplusbeta = np.arctan(shx517 / (shy517 + 0.1))
                        # alphaplusbeta = 1.57
                    ratiobeta = -(alphaplusbeta - ratioalpha * 0)
                    shxnew = (shx17 * np.cos(ratiobeta)) + (shy17 * np.sin(ratiobeta))
                    shynew = (-shx17 * np.sin(ratiobeta)) + (shy17 * np.cos(ratiobeta))
                    ratioXY = abs(shxnew / shynew)
                    constratioXY = abs(-0.4)

                    if ratioXY >= constratioXY:
                        l = np.abs(shxnew * np.sqrt(1 + (1 / constratioXY) ** 2))
                        distanse170cm = 5503.9283512 * l ** (-1.0016171)
                    else:
                        l = np.abs(shynew * np.sqrt(1 + constratioXY ** 2))
                        distanse170cm = 5503.9283512 * l ** (-1.0016171)
                    cv2.putText(img, f'{str(int(distanse170cm))}cm', (20, 90), cv2.FONT_HERSHEY_PLAIN, 3, (255, 0, 0), 3)


                # голос
                # Проверка наличия руки
                if len(hands) > 0:
                    hand = hands[0]

                    # Проверка, что большой и мизинец подняты
                    fingers = detector.fingersUp(hand)
                    if fingers[0] and fingers[4] and not any(fingers[1:4]):
                        # Рассчет расстояния между большим и мизинцем
                        length, _, _ = detector.findDistance(hand["lmList"][8][:2], hand["lmList"][20][:2], img)

                        # Нормализация значения длины к диапазону громкости
                        vol = np.interp(length, [20, 120], [minVol, maxVol])

                        # Установка громкости
                        volume.SetMasterVolumeLevel(vol, None)
                        print(f"Громкость: {vol}")

                # Следим за положением указательного пальца
                if len(lmList1) != 0:
                    x1, y1 = lmList1[8][:2]

                # Проверяем, поднят ли палец
                finup = detector.fingersUp(hand1)

                # Ограничение кадра движения руки
                cv2.rectangle(img, (frameR, frameR), (wCam - frameR, hCam - frameR), (255, 0, 255), 2)
                # Режим перемещения мыши
                if finup[0] == 0 and finup[1] == 1 and finup[2] == 0 and finup[3] == 0 and finup[4] == 0:
                    # Конвертация координат для экрана
                    x3 = np.interp(x1, (frameR, wCam - frameR), (0, wScr))
                    y3 = np.interp(y1, (frameR, hCam - frameR), (0, hScr))

                    # Сглаживание мыши
                    clockX = clockX + (x3 - plocX) / smooth
                    clockY = clockY + (y3 - plocY) / smooth

                    # Движение мыши
                    mouse.move(clockX, clockY)
                    cv2.circle(img, (x1, y1), 10, (0, 0, 255), cv2.FILLED)
                    plocX, plocY = clockX, clockY

                # Левая кнопка мыши
                if finup[0] == 0 and finup[1] == 1 and finup[2] == 1 and finup[3] == 0 and finup[4] == 0:
                    length, info, img = detector.findDistance(lmList1[8][:2], lmList1[12][:2], img)
                    print(length)
                    # Нажатие мыши, если расстояние больше 25
                    if length > (40):
                        flag = True
                    if length < (35) and flag == True:
                        func.LCM(img, x1, y1, length)
                        flag = False
                # Правая кнопка мыши
                if finup[0] == 0 and finup[1] == 1 and finup[2] == 0 and finup[3] == 0 and finup[4] == 1:
                    length, info, img = detector.findDistance(lmList1[8][:2], lmList1[20][:2], img)
                    # print(length)

                    # Нажатие мыши, если расстояние меньше 50
                    if length > 30:
                        flag = True
                    if length < 50:
                        func.RCM(img, x1, y1, length)
                        flag = False

                # Захват и бросок
                if finup[0] == 1 and finup[1] == 1 and finup[2] == 1 and finup[3] == 0 and finup[4] == 0:
                    length, info, img = detector.findDistance(lmList1[8][:2], lmList1[12][:2], img)
                    print(length)
                    if length < 25:
                        mouse.press(button="left")
                        mouse.move(clockX, clockY)

                # Скролл
                if finup[0] == 1 and finup[1] == 0 and finup[2] == 0 and finup[3] == 0 and finup[4] == 0:
                    if len(lmList1) != 0:
                        x1, y1 = lmList1[4][:2]
                        x2, y2 = lmList1[5][:2]
                        if y1 > y2:
                            mouse.wheel(delta=-0.5)
                        elif y1 < y2:
                            mouse.wheel(delta=0.5)

            if len(hands) == 2:
                hand2 = hands[1]
                lmList2 = hand2["lmList"]  # Список 21 landmarks
                bbox2 = hand2["bbox"]  # Информация о bounding box x,y,w,h
                centerPoint2 = hand2["center"]  # Центр руки cx,cy
                handType2 = hand2["type"]  # Тип руки (левая\правая)
                fingers2 = detector.fingersUp(hand2)
                #print(fingers1,fingers2)
                #length, info, img = detector.findDistance(centerPoint1, centerPoint2, img)

                if finup[0] == 1 and finup[1] == 1 and finup[2] == 0 and finup[3] == 0 and finup[4] == 0 and fingers2[0] == 1 and fingers2[1] == 1 and fingers2[2] == 0 and fingers2[3] == 0 and fingers2[4] == 0:
                    length, info, img = detector.findDistance(centerPoint1, centerPoint2, img)
                    print(length, prevLenght)
                    if (length > prevLenght):
                        print(length, prevLenght)
                        keyboard.press('ctrl')
                        print("fsef")
                        mouse.wheel(0.1)
                        print("adadfd")
                        keyboard.release('ctrl')
                        # nextlenght = lenght
                        prevLenght = length
                    else:
                        print("abobobob")
                        keyboard.press('ctrl')
                        mouse.wheel(-0.1)
                        keyboard.release('ctrl')
                        prevLenght = length
                    print(length, prevLenght)


            if cv2.waitKey(1) & 0xFF == 27:
                break

            # FPS
            cTime = time.time()
            fps = 1 / (cTime - pTime)
            pTime = cTime
            cv2.putText(img, str(int(fps)), (20, 50), cv2.FONT_HERSHEY_PLAIN, 3, (255, 0, 0), 3)

            # Display
            cv2.imshow("AI-Cursor", img)
            cv2.waitKey(1)

        cam.release()
        cv2.destroyAllWindows()
        # Запуск меню после завершения игры
        subprocess.run([sys.executable, "menu.py"])
        sys.exit()
    except:
        print("С пинг-понг чет не так")
        cam.release()
        cv2.destroyAllWindows()
        # Запуск меню после возникновения ошибки
        subprocess.run([sys.executable, "menu.py"])
        sys.exit()