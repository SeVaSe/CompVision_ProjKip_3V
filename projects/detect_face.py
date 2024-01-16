import sys

import cv2
import subprocess
import numpy as np
import mediapipe as mp

from classes.class_video_capt import NumbVideoCapt

mp_holistic = mp.solutions.holistic  # Holistic Model
mp_drawing = mp.solutions.drawing_utils  # Drawing Utilities


def mediapipe_detection(image, model):
    image = cv2.cvtColor(image, cv2.COLOR_BGR2RGB)  # COLOR CONVERSION BGR to RGB
    image.flags.writeable = False  # IMAGE IS NOT WRITEABLE
    results = model.process(image)  # Make Prediction
    image.flags.writeable = True  # IMAGE IS WRITEABLE
    image = cv2.cvtColor(image, cv2.COLOR_RGB2BGR)  # COLOR CONVERSION RGB to BGR
    return image, results


def draw_landmarks(image, results):
    mp_drawing.draw_landmarks(image, results.face_landmarks, mp_holistic.FACEMESH_CONTOURS)  # Draw Face Connections
    mp_drawing.draw_landmarks(image, results.pose_landmarks, mp_holistic.POSE_CONNECTIONS)  # Draw pose Connections
    mp_drawing.draw_landmarks(image, results.left_hand_landmarks,
                              mp_holistic.HAND_CONNECTIONS)  # Draw left Hand Connections
    mp_drawing.draw_landmarks(image, results.right_hand_landmarks,
                              mp_holistic.HAND_CONNECTIONS)  # Draw right Hand Connections


def draw_styled_landmarks(image, results):
    mp_drawing.draw_landmarks(image, results.face_landmarks, mp_holistic.FACEMESH_CONTOURS,
                              mp_drawing.DrawingSpec(color=(80, 110, 100), thickness=1, circle_radius=1),
                              mp_drawing.DrawingSpec(color=(80, 256, 121), thickness=1,
                                                     circle_radius=1))  # Draw Face Connections
    mp_drawing.draw_landmarks(image, results.left_hand_landmarks, mp_holistic.HAND_CONNECTIONS,
                              mp_drawing.DrawingSpec(color=(121, 22, 76), thickness=2, circle_radius=4),
                              mp_drawing.DrawingSpec(color=(121, 44, 250), thickness=2,
                                                     circle_radius=2))  # Draw left Hand Connections
    mp_drawing.draw_landmarks(image, results.right_hand_landmarks, mp_holistic.HAND_CONNECTIONS,
                              mp_drawing.DrawingSpec(color=(245, 117, 66), thickness=2, circle_radius=4),
                              mp_drawing.DrawingSpec(color=(245, 66, 230), thickness=2,
                                                     circle_radius=2))  # Draw right Hand Connections


def extract_keypoints(results):
    pose = np.array([[res.x, res.y, res.z, res.visibility] for res in
                     results.pose_landmarks.landmark]).flatten() if results.pose_landmarks else np.zeros(132)
    lh = np.array([[res.x, res.y, res.z] for res in
                   results.left_hand_landmarks.landmark]).flatten() if results.left_hand_landmarks else np.zeros(21 * 3)
    rh = np.array([[res.x, res.y, res.z] for res in
                   results.right_hand_landmarks.landmark]).flatten() if results.right_hand_landmarks else np.zeros(
        21 * 3)
    face = np.array([[res.x, res.y, res.z] for res in
                     results.face_landmarks.landmark]).flatten() if results.face_landmarks else np.zeros(1404)
    return np.concatenate([pose, face, rh, lh])


##==================FOR COLLECTING DATA==================
# #path for exported data, np array
# DATA_PATH = os.path.join("MP_Data")
# #actions that we want to detect
# actions = np.array(["hello", "thankyou","ily"])
# #30 videos worth of data
# no_sequences = 30
# #30 frames in length
# sequence_length = 30
#
# #Creating Data Files
# for action in actions:
#     for sequence in range(no_sequences):
#         try:
#             os.makedirs(os.path.join(DATA_PATH, action,str(sequence)))
#         except:
#             pass


# collecting Data


def run_detect_face():
    try:
        numbVC = NumbVideoCapt()
        cap = cv2.VideoCapture(numbVC.numb)  # webcam capture to cap
        # set mediapipe models
        with mp_holistic.Holistic(min_detection_confidence=0.5, min_tracking_confidence=0.5) as hoslistic:
            while cap.isOpened():

                # Read Frame
                ret, frame = cap.read()


                # Make Detection
                image, results = mediapipe_detection(frame, hoslistic)
                # print(results)

                # Draw Landmarks
                draw_styled_landmarks(image, results)



                # wait logic

                # show frame
                cv2.imshow("OpenCV capture", image)

                # Break Gracefully
                if cv2.waitKey(1) & 0xFF == 27:
                    break
            cap.release()
            cv2.destroyAllWindows()
    except Exception as e:
        print(f"С лиуом что то не так...")
        cap.release()
        cv2.destroyAllWindows()
        subprocess.run([sys.executable, "menu.py"])
        sys.exit()