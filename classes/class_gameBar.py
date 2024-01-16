import cv2

from projects.game_snake import run_snake_game
from projects.game_pin_pong import run_pin_pong_game
from projects.game_circle_reaction import run_circle_reaction_game
from projects.science_project_growth import run_science_project
from projects.science_detected_peop import run_detected
from projects.detect_face import run_detect_face
from projects.peop_detect_all import run_detect_peop_all
from projects.qr_time import run_qr

from ai_mouse.mouse_prog_cv import run_cursor




class GameBar:
    """КЛАСС ДЛЯ ЗАПУСКА ПРОЕКТОВ"""
    @staticmethod
    def start_game_1():
        """Метод для запуска Змейки"""
        global game_active
        game_active = True
        cv2.destroyWindow("Menu")
        run_snake_game()

    @staticmethod
    def start_game_2():
        """Метод для запуска Пин-Понг"""
        global game_active
        game_active = True
        cv2.destroyWindow("Menu")
        run_pin_pong_game()

    @staticmethod
    def start_game_3():
        """Метод для запуска Реакции"""
        global game_active
        game_active = True
        cv2.destroyWindow("Menu")
        run_circle_reaction_game()

    @staticmethod
    def start_game_4():
        """Метод для запуска Научного проекта"""
        global game_active
        game_active = True
        cv2.destroyWindow("Menu")
        run_science_project()

    @staticmethod
    def start_game_5():
        """Метод для запуска Научного проекта"""
        global game_active
        game_active = True
        cv2.destroyWindow("Menu")
        run_detected()

    @staticmethod
    def start_game_6():
        """Метод для запуска Детекта лица"""
        global game_active
        game_active = True
        cv2.destroyWindow("Menu")
        run_detect_face()

    @staticmethod
    def start_game_7():
        """Метод для запуска Детект толпы людей"""
        global game_active
        game_active = True
        cv2.destroyWindow("Menu")
        run_detect_peop_all()

    @staticmethod
    def start_game_8():
        """Метод для запуска Курсор"""
        global game_active
        game_active = True
        cv2.destroyWindow("Menu")
        run_cursor()

    @staticmethod
    def start_game_9():
        """Метод для запуска Курсор"""
        global game_active
        game_active = True
        cv2.destroyWindow("Menu")
        run_qr()



