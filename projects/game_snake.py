# УКАЗАТЕЛЬНЫЙ ПАЛЕЦ
# if results.multi_hand_landmarks:
#     for landmarks in results.multi_hand_landmarks:
#         # Отрисовка точек на руке
#         mp_drawing.draw_landmarks(image, landmarks, mp_hands.HAND_CONNECTIONS)
#         index_x = int(landmarks.landmark[mp_hands.HandLandmark.INDEX_FINGER_TIP].x * screen_width)
#         index_y = int(landmarks.landmark[mp_hands.HandLandmark.INDEX_FINGER_TIP].y * screen_height)
#         cv2.circle(image, (index_x, index_y), 8, (0, 255, 0), -1)
import time

import cv2
import mediapipe as mp
import random
import sys
import subprocess

from cv_video_capt import NumbVideoCapt


def run_snake_game():
    try:
        mp_drawing = mp.solutions.drawing_utils
        mp_hands = mp.solutions.hands

        screen_width, screen_height = 640, 480
        cell_size, fruit_size, special_fruit_size = 20, 40, 30
        snake_speed, smooth_factor = 4.5, 0.8
        min_speed_threshold = 3

        snake = [(screen_width // 2, screen_height // 2)]
        snake_direction = (0, -1)
        smoothed_vector_x, smoothed_vector_y = 0, 0
        hand_x, hand_y = 0, 0

        update_count = 0
        score = 0
        time_sec = 0

        def generate_fruit_location():
            return (random.randint(0, (screen_width - fruit_size) // cell_size) * cell_size,
                    random.randint(0, (screen_height - fruit_size) // cell_size) * cell_size)

        def generate_special_fruit_location():
            return (random.randint(0, (screen_width - special_fruit_size) // cell_size) * cell_size,
                    random.randint(0, (screen_height - special_fruit_size) // cell_size) * cell_size), "special"

        fruit = generate_fruit_location()
        special_fruit = generate_special_fruit_location()

        numbVC = NumbVideoCapt()
        cap = cv2.VideoCapture(numbVC.numb)

        with mp_hands.Hands(min_detection_confidence=0.5, min_tracking_confidence=0.5) as hands:
            while True:
                time_sec += 0.05

                ret, image = cap.read()
                if not ret:
                    continue

                image = cv2.flip(image, 1)
                results = hands.process(cv2.cvtColor(image, cv2.COLOR_BGR2RGB))

                if results.multi_hand_landmarks:
                    for landmarks in results.multi_hand_landmarks:
                        mp_drawing.draw_landmarks(image, landmarks, mp_hands.HAND_CONNECTIONS)
                        index_x = int(landmarks.landmark[mp_hands.HandLandmark.WRIST].x * screen_width)
                        index_y = int(landmarks.landmark[mp_hands.HandLandmark.WRIST].y * screen_height)
                        cv2.circle(image, (index_x, index_y), 8, (0, 255, 0), -1)

                        prev_hand_x, prev_hand_y = hand_x, hand_y
                        hand_x, hand_y = index_x, index_y

                        vector_x = hand_x - prev_hand_x
                        vector_y = hand_y - prev_hand_y

                        smoothed_vector_x = (1 - smooth_factor) * vector_x + smooth_factor * smoothed_vector_x
                        smoothed_vector_y = (1 - smooth_factor) * vector_y + smooth_factor * smoothed_vector_y

                        if abs(smoothed_vector_x) > min_speed_threshold or abs(smoothed_vector_y) > min_speed_threshold:
                            if abs(smoothed_vector_x) > abs(smoothed_vector_y):
                                if smoothed_vector_x < 0 and snake_direction != (1, 0):
                                    snake_direction = (-1, 0)
                                elif smoothed_vector_x > 0 and snake_direction != (-1, 0):
                                    snake_direction = (1, 0)
                            else:
                                if smoothed_vector_y < 0 and snake_direction != (0, 1):
                                    snake_direction = (0, -1)
                                elif smoothed_vector_y > 0 and snake_direction != (0, -1):
                                    snake_direction = (0, 1)

                snake_head = (snake[0][0] + snake_direction[0] * cell_size, snake[0][1] + snake_direction[1] * cell_size)

                if snake_head[0] < 0:
                    snake_head = (screen_width - cell_size, snake_head[1])
                elif snake_head[0] >= screen_width:
                    snake_head = (0, snake_head[1])
                elif snake_head[1] < 0:
                    snake_head = (snake_head[0], screen_height - cell_size)
                elif snake_head[1] >= screen_height:
                    snake_head = (snake_head[0], 0)

                update_count += 1

                if update_count > (10 - snake_speed * 2):
                    update_count = 0
                    snake.insert(0, snake_head)

                    if snake_head[0] <= fruit[0] + fruit_size and snake_head[0] + cell_size >= fruit[0] and snake_head[1] <= fruit[1] + fruit_size and snake_head[1] + cell_size >= fruit[1]:
                        fruit = generate_fruit_location()
                        score += 1
                        snake.append(snake[-1])  # Увеличиваем длину змейки на 1 при съедании обычного фрукта

                    if snake_head[0] <= special_fruit[0][0] + special_fruit_size and snake_head[0] + cell_size >= special_fruit[0][0] and snake_head[1] <= special_fruit[0][1] + special_fruit_size and snake_head[1] + cell_size >= special_fruit[0][1]:
                        special_fruit = generate_special_fruit_location()
                        score += 2
                        snake.extend([snake[-1]] * 2)  # Увеличиваем длину змейки на 2 при съедании специального фрукта

                    else:
                        snake.pop()

                    if snake_head in snake[1:]:
                        break

                for idx, segment in enumerate(snake):
                    if idx == 0:
                        cv2.rectangle(image, (segment[0], segment[1]),
                                      (segment[0] + cell_size, segment[1] + cell_size), (255, 0, 0), -1)
                    else:
                        cv2.rectangle(image, (segment[0], segment[1]),
                                      (segment[0] + cell_size, segment[1] + cell_size), (0, 0, 255), -1)

                cv2.rectangle(image, (fruit[0], fruit[1]), (fruit[0] + fruit_size, fruit[1] + fruit_size),
                              (0, 255, 0), -1)

                cv2.rectangle(image, (special_fruit[0][0], special_fruit[0][1]),
                              (special_fruit[0][0] + special_fruit_size, special_fruit[0][1] + special_fruit_size),
                              (255, 255, 0), -1)

                cv2.putText(image, f"Score: {score}", (10, 30), cv2.FONT_HERSHEY_SIMPLEX, 1, (200, 0, 255), 2)
                cv2.putText(image, f"Time: {'{:.2f}'.format(time_sec)}", (10, 70), cv2.FONT_HERSHEY_SIMPLEX, 1, (200, 0, 255), 2)

                cv2.imshow('Snake Game', image)
                if cv2.waitKey(1) & 0xFF == 27:
                    break

            cap.release()
            cv2.destroyAllWindows()
            subprocess.run([sys.executable, "menu.py"])
            sys.exit()
    except:
        cap.release()
        cv2.destroyAllWindows()
        subprocess.run([sys.executable, "menu.py"])
        sys.exit()

