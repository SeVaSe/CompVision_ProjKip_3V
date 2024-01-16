import subprocess
import sys
import cv2
import mediapipe as mp

from classes.class_video_capt import NumbVideoCapt


def calculate_distance(x1, y1, x2, y2):
    return ((x2 - x1) ** 2 + (y2 - y1) ** 2) ** 0.5

def mirror_landmarks(landmarks, image_width):
    # Отзеркаливание по оси X
    mirrored_landmarks = []
    for landmark in landmarks:
        mirrored_landmarks.append((image_width - landmark[0], landmark[1]))
    return mirrored_landmarks

def run_science_project():
    mp_holistic = mp.solutions.holistic
    mp_drawing = mp.solutions.drawing_utils

    numbVC = NumbVideoCapt()
    cap = cv2.VideoCapture(numbVC.numb)
    holistic = mp_holistic.Holistic()

    interesting_points = {
        0: 'Нос',
        2: 'Правый глаз',
        5: 'Левый глаз',
        7: 'Правое ухо',
        8: 'Левое ухо',
        9: 'Рот',
        11: 'Правое плечо',
        12: 'Левое плечо',
        13: 'Правый локоть',
        14: 'Левый локоть',
        15: 'Правая кисть',
        16: 'Левая кисть',
        23: 'Правая тазовая кость',
        24: 'Левая тазовая кость',
        25: "Правое колено",
        26: "Левое колено",
        27: "Правая стопа",
        28: "Левая стопа"
    }

    mp_hands = mp.solutions.hands
    hands = mp_hands.Hands()

    nearest_part = None

    while cap.isOpened():
        ret, frame = cap.read()

        if not ret:
            continue

        # Отзеркаливание изображения
        frame = cv2.flip(frame, 1)

        gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
        cv2.namedWindow("Interactive Body Detection", cv2.WINDOW_NORMAL)
        cv2.resizeWindow("Interactive Body Detection", 800, 600)

        results_body = holistic.process(frame)
        results_hands = hands.process(frame)

        if results_body.pose_landmarks:
            for idx, landmark in enumerate(results_body.pose_landmarks.landmark):
                x, y = int(landmark.x * frame.shape[1]), int(landmark.y * frame.shape[0])
                if idx in interesting_points:
                    cv2.circle(frame, (x, y), 5, (0, 0, 255), -1)

        if results_hands.multi_hand_landmarks:
            for hand_landmarks in results_hands.multi_hand_landmarks:
                if len(hand_landmarks.landmark) > mp_hands.HandLandmark.INDEX_FINGER_TIP:
                    index_finger_tip = hand_landmarks.landmark[mp_hands.HandLandmark.INDEX_FINGER_TIP]
                    ix, iy = int(index_finger_tip.x * frame.shape[1]), int(index_finger_tip.y * frame.shape[0])

                    # Отзеркаливание landmarks руки
                    mirrored_hand_landmarks = mirror_landmarks([(lm.x, lm.y) for lm in hand_landmarks.landmark], frame.shape[1])

                    min_distance = float('inf')
                    for idx, body_landmark in enumerate(results_body.pose_landmarks.landmark):
                        body_x, body_y = int(body_landmark.x * frame.shape[1]), int(body_landmark.y * frame.shape[0])
                        distance = calculate_distance(ix, iy, body_x, body_y)
                        if distance < min_distance:
                            min_distance = distance
                            nearest_part = interesting_points.get(idx, None)

                    cv2.circle(frame, (ix, iy), 5, (255, 0, 0), -1)

        if nearest_part:
            cv2.putText(frame, f'Часть тела: {nearest_part}', (10, 30), cv2.FONT_HERSHEY_COMPLEX, 0.7, (255, 255, 0), 2)

        cv2.imshow('Interactive Body Detection', frame)

        if cv2.waitKey(1) & 0xFF == 27:
            break

    cap.release()
    cv2.destroyAllWindows()
    print("Пока3")
    subprocess.run([sys.executable, "menu.py"])
    sys.exit()


