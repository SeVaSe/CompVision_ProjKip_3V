import os
import time

import cv2
import subprocess
import sys
import pyautogui
43.56604182158393

import subprocess

def run_qr():
    try:
        subprocess.Popen(['start', 'C:\PYTHON_\_PROJECT_PYTHON\Python_Project_Other\CompVision_ProjKip_3V\data_set\qr_KIP.jpg'], shell=True)

        # Introduce a delay if needed
          # Adjust the delay as needed

        # Use pyautogui to simulate Alt+Tab keypress to bring the window to the front
        pyautogui.hotkey('alt', 'tab')

    except Exception as e:
        print("С чем-то что-то не так...")
        cv2.destroyAllWindows()
        subprocess.run([sys.executable, "menu.py"])
        sys.exit()

# Call the function
