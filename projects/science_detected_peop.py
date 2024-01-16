import subprocess
import sys

import cv2
import mediapipe as mp
import numpy as np
import colorsys

from classes.class_video_capt import NumbVideoCapt


def draw_lines(image, landmarks, connections, colors):
    height, width, _ = image.shape
    landmark_list = landmarks.landmark
    landmark_coords = [(int(landmark.x * width), int(landmark.y * height)) for landmark in landmark_list]

    for i, connection in enumerate(connections):
        start_idx, end_idx = connection
        start_point = landmark_coords[start_idx]
        end_point = landmark_coords[end_idx]
        color = colors[i]
        cv2.line(image, start_point, end_point, color, 2)

    for landmark in landmark_coords:
        hue = (landmark[0] + landmark[1]) % 360
        color = tuple(int(255 * i) for i in colorsys.hsv_to_rgb(hue / 360, 1.0, 1.0))
        cv2.circle(image, landmark, 5, color, -1)


def run_detected():
    try:
        mp_pose = mp.solutions.pose

        # Инициализация модели
        pose = mp_pose.Pose(static_image_mode=False, min_detection_confidence=0.5, min_tracking_confidence=0.5)

        numbVC = NumbVideoCapt()
        cap = cv2.VideoCapture(numbVC.numb)

        while cap.isOpened():
            success, frame = cap.read()
            if not success:
                break

            # Создание черного фона
            black_image = np.zeros_like(frame)

            # Обработка изображения
            results = pose.process(frame)

            if results.pose_landmarks is not None:
                # Определение цветов для линий каждой части позы
                hue_values = np.linspace(0, 360, len(mp_pose.POSE_CONNECTIONS) + 1)[:-1]
                colors = [tuple(int(255 * i) for i in colorsys.hsv_to_rgb(hue / 360, 1.0, 1.0)) for hue in hue_values]

                # Рисование линий и точек позы на черном фоне
                draw_lines(black_image, results.pose_landmarks, mp_pose.POSE_CONNECTIONS, colors)

                # Вывод изображения с позой на черном фоне
                cv2.imshow('Pose Detection', black_image)

            if cv2.waitKey(5) & 0xFF == 27:
                break

        # Освобождение ресурсов
        cap.release()
        cv2.destroyAllWindows()

        # Освобождение ресурсов Mediapipe
        pose.close()
        subprocess.run([sys.executable, "menu.py"])
        sys.exit()

    except Exception as e:
        print(f"Со скелетом что то не так...")
        cap.release()
        cv2.destroyAllWindows()
        subprocess.run([sys.executable, "menu.py"])
        sys.exit()


