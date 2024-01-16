import subprocess
import mediapipe as mp
import cv2
import numpy as np
import time
import random
import sys

# Инициализация библиотек
mp_drawing = mp.solutions.drawing_utils
mp_hands = mp.solutions.hands
score = 0
level = 1
time_limit = 30  # 30 секунд на каждый уровень
lives = 3  # Изначальное количество жизней

enemies = []  # Список врагов (круги)
red_circles = []  # Список красных кругов
yellow_circles = []  # Список желтых кругов
num_enemies = 1  # Изначальное количество врагов

# Переменные для отслеживания времени и состояния игры
start_time = time.time()
game_over = False
pixelCoordinatesLandmark = None  # Переменная для хранения координат указательного пальца
yellow_circle_time = time.time()
yellow_circle_interval = 15  # Интервал появления желтых кружков


def run_circle_reaction_game():
    global score, level, time_limit, yellow_circle_time, lives, game_over, start_time, enemies, red_circles, num_enemies, pixelCoordinatesLandmark

    def generate_enemies(num):
        global enemies
        enemies = [(random.randint(50, 600), random.randint(50, 400)) for _ in range(num)]

    def generate_red_circles(num):
        global red_circles
        red_circles = [(random.randint(50, 600), 400) for _ in range(random.randint(1, 3))]

    def generate_yellow_circles():
        global yellow_circles
        yellow_circles.append((random.randint(50, 600), 400))

    def enemy():
        global enemies
        for x_enemy, y_enemy in enemies:
            cv2.circle(image, (x_enemy, y_enemy), 25, (0, 200, 0), 5)

    def red_circle():
        global red_circles
        for x_red, y_red in red_circles:
            cv2.circle(image, (x_red, y_red), 25, (0, 0, 200), 5)

    def yellow_circle():
        global yellow_circles
        for x_yellow, y_yellow in yellow_circles:
            cv2.circle(image, (x_yellow, y_yellow), 25, (0, 255, 255), 5)

    def game_over_screen():

        font = cv2.FONT_HERSHEY_COMPLEX
        color = (255, 0, 255)
        text = cv2.putText(image, "Проиграл", (250, 200), font, 2, color, 4, cv2.LINE_AA)
        text = cv2.putText(image, "Ты смог набрать: " + str(score), (300, 300), font, 1, color, 2, cv2.LINE_AA)
        text = cv2.putText(image, "Нажми 'R' для рестарта", (250, 400), font, 1, color, 2, cv2.LINE_AA)
        game_over = True
        start_time = time.time()
        num_enemies = 1
        lives = 3  # Сбросить количество жизней
        red_circles.clear()
        yellow_circles.clear()


    try:
        # Инициализация видеопотока с веб-камеры
        video = cv2.VideoCapture(0)
        with mp_hands.Hands(min_detection_confidence=0.8, min_tracking_confidence=0.5) as hands:
            while video.isOpened():
                _, frame = video.read()

                if not game_over:
                    elapsed_time = time.time() - start_time
                    if elapsed_time > time_limit:
                        game_over_screen()

                image = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
                image = cv2.flip(image, 1)
                imageHeight, imageWidth, _ = image.shape

                results = hands.process(image)
                image = cv2.cvtColor(image, cv2.COLOR_RGB2BGR)

                font = cv2.FONT_HERSHEY_COMPLEX
                color = (255, 0, 255)
                text = cv2.putText(image, "Уровень: " + str(level), (240, 30), font, 1, color, 2, cv2.LINE_AA)
                text = cv2.putText(image, "Очки: " + str(score), (460, 30), font, 1, color, 2, cv2.LINE_AA)
                text = cv2.putText(image, "Жизни: " + str(lives), (30, 30), font, 1, color, 2, cv2.LINE_AA)

                if not enemies and not game_over:
                    generate_enemies(num_enemies)

                if not red_circles and not game_over and score >= 5:
                    generate_red_circles(1)

                if not yellow_circles and not game_over and time.time() - yellow_circle_time > yellow_circle_interval:
                    generate_yellow_circles()

                enemy()
                red_circle()
                yellow_circle()

                if not game_over and results.multi_hand_landmarks:
                    for num, hand in enumerate(results.multi_hand_landmarks):
                        mp_drawing.draw_landmarks(image, hand, mp_hands.HAND_CONNECTIONS,
                                                  mp_drawing.DrawingSpec(color=(250, 44, 250), thickness=2, circle_radius=2))

                        for point in mp_hands.HandLandmark:
                            normalizedLandmark = hand.landmark[point]
                            if normalizedLandmark is not None:
                                pixelCoordinatesLandmark = mp_drawing._normalized_to_pixel_coordinates(normalizedLandmark.x,
                                                                                                   normalizedLandmark.y,
                                                                                                   imageWidth, imageHeight)

                                if point == mp_hands.HandLandmark.INDEX_FINGER_TIP:
                                    cv2.circle(image, (pixelCoordinatesLandmark[0], pixelCoordinatesLandmark[1]), 25, (250, 196, 0),
                                               5)
                                    for i, (x_enemy, y_enemy) in enumerate(enemies):
                                        if abs(pixelCoordinatesLandmark[0] - x_enemy) < 25 and abs(
                                                pixelCoordinatesLandmark[1] - y_enemy) < 25:
                                            del enemies[i]
                                            score += 1
                                    for i, (x_red, y_red) in enumerate(red_circles):
                                        if abs(pixelCoordinatesLandmark[0] - x_red) < 25 and abs(
                                                pixelCoordinatesLandmark[1] - y_red) < 25:
                                            del red_circles[i]
                                            lives -= 1
                                    for i, (x_yellow, y_yellow) in enumerate(yellow_circles):
                                        if abs(pixelCoordinatesLandmark[0] - x_yellow) < 25 and abs(
                                                pixelCoordinatesLandmark[1] - y_yellow) < 25:
                                            del yellow_circles[i]
                                            lives += 1

                if not game_over and pixelCoordinatesLandmark is not None:
                    # Проверяем, касается ли кружок синего цвета (game over при касании красных кружков)
                    for i, (x_red, y_red) in enumerate(red_circles):
                        if abs(pixelCoordinatesLandmark[0] - x_red) < 25 and abs(pixelCoordinatesLandmark[1] - y_red) < 25:
                            del red_circles[i]
                            lives -= 1
                            if lives <= 0:
                                game_over_screen()
                                game_over = True
                                cv2.destroyAllWindows()
                                print(f"Ты набрал: {score} очка")
                                sys.exit()  # Завершить программу

                if time.time() - yellow_circle_time > yellow_circle_interval:
                    yellow_circle_time = time.time()

                if not game_over:
                    for i in range(len(red_circles)):
                        red_circles[i] = (red_circles[i][0], red_circles[i][1] - 5)
                        if red_circles[i][1] < 0:
                            del red_circles[i]
                            break

                cv2.imshow('Hand Tracking', image)

                key = cv2.waitKey(10)
                if cv2.waitKey(1) & 0xFF == 27:
                    break
                elif key & 0xFF == ord('r') and game_over:
                    score = 0
                    game_over = False
                    start_time = time.time()
                    num_enemies = 1
                    lives = 3  # Сбросить количество жизней
                    red_circles.clear()
                    yellow_circles.clear()
                    continue  # Перезапустить основной цикл игры

                if score >= level * 10:
                    level += 1
                    num_enemies += 1  # Увеличиваем количество врагов на одного
                    start_time = time.time()

                if cv2.waitKey(1) & 0xFF == 27:
                    break

        video.release()
        cv2.destroyAllWindows()
        subprocess.run([sys.executable, "menu.py"])
        sys.exit()  # Завершить программу
    except Exception as e:
        video.release()
        cv2.destroyAllWindows()
        print("С кружками что-то не так1")
        print("Ошибка при выполнении: ", e)

        subprocess.run([sys.executable, "menu.py"])
        sys.exit()  # Завершить программу
