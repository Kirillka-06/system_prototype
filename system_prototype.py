from tkinter import Tk, Button, Entry
import cv2
import numpy as np
import time
import psycopg2
from dotenv import load_dotenv
from dotenv import find_dotenv
import os


load_dotenv(find_dotenv())


class DBActions:
    
    def __init__(self, db_name, user, password, host='localhost'):
        self.__db_name = db_name
        self.__user = user
        self.__password = password
        self.__host = host
        print(db_name)
        print(password)
        self.__conn = psycopg2.connect(
            dbname=db_name,
            user=user,
            password=password,
            host=host,
        )
        self.__cursor = self.__conn.cursor()
    
    def create_notion(self, name, data):
        self.__cursor.execute('INSERT INTO schemes (name, data)'
                              'VALUES ()')
    
    def get_notion(self):
        self.__cursor.execute('SELECT * FROM schemes')


def create_maket():

    # Создание пустого холста
    canvas = np.zeros((480, 640, 3), dtype=np.uint8)

    exhibits = []
    cameras = []

    RADIUS = 10
    '''center_x = 0
    center_y = 0'''


    def draw_triangle(angle, center_x, center_y):
        # Очистка холста
        #canvas.fill(255)

        # Вычисление координат вершин треугольника
        print(f'draw {center_x} {center_y}')
        length = 120

        '''vertex1_x = center_x + int(length * np.cos(np.radians(angle)))
        vertex1_y = center_y + int(length * np.sin(np.radians(angle)))'''
        vertex2_x = center_x + int(length * np.cos(np.radians(angle + 300)))
        vertex2_y = center_y + int(length * np.sin(np.radians(angle + 300)))
        vertex3_x = center_x + int(length * np.cos(np.radians(angle + 60)))
        vertex3_y = center_y + int(length * np.sin(np.radians(angle + 60)))

        # Отрисовка треугольника на холсте
        cv2.line(canvas, (center_x, center_y), (vertex2_x, vertex2_y), (255, 0, 0), 2)
        cv2.line(canvas, (center_x, center_y), (vertex3_x, vertex3_y), (255, 0, 0), 2)
        cv2.line(canvas, (vertex3_x, vertex3_y), (vertex2_x, vertex2_y), (255, 0, 0), 2)

        cv2.setMouseCallback('Create canvas', mark_camera)

    def mouse_callback(event, x, y, flags, param):
        # Определяем координаты клика
        #click_x = x
        #click_y = y
        click_x, click_y = x, y
        #center_x, center_y = param
        print(f'mouse callback {param}')

        # Вычисляем угол между центром круга и точкой клика
        angle = np.degrees(np.arctan2(click_y - center_y, click_x - center_x))
        print(angle)

        # Вызываем функцию для отображения треугольника с новым углом
        draw_triangle(angle, center_x , center_y)


    # Отметка расположения камеры
    def mark_camera(event, x, y, flags, param):

        if event == cv2.EVENT_LBUTTONUP:
            cv2.circle(canvas, (x, y), RADIUS, (0, 0, 255), -1)

            global center_x
            global center_y
            center_x = x
            center_y = y
            print(f'camera {x} {y}')
            #time.sleep(1)

        if event == cv2.EVENT_RBUTTONUP:
            cv2.setMouseCallback('Create canvas', mouse_callback)

    # Отметка расположения экспоната
    def mark_exhibit(event, x, y, flags, param):
        if event == cv2.EVENT_LBUTTONUP:
            # Рисуем зеленый прямоугольник на холсте
            cv2.rectangle(canvas, (x-10, y-10), (x+10, y+10), (0, 255, 0), -1)
    
    def entry_name():
        root = Tk()
        
        entry = Entry(root, width=30)
        entry.pack()

        button = Button(root, text='Save')#, command=process_text)
        button.pack()

    # Создание окна с холстом
    cv2.namedWindow('Create canvas')
    # Привязка функций для отметки камеры и экспоната к окну с холстом
    cv2.setMouseCallback('Create canvas', mark_exhibit)

    # Главный цикл приложения
    while True:
        # Показываем холст
        cv2.imshow('Create canvas', canvas)

        # Ожидание нажатия клавиши 'c' для переключения в режим отметки камер
        if cv2.waitKey(1) & 0xFF == ord('c'):
            # Привязка функции для отметки камер к окну с холстом
            cv2.setMouseCallback('Create canvas', mark_camera)

        # Ожидание нажатия клавиши 'v' для переключения в режим отметки экспонатов
        if cv2.waitKey(1) & 0xFF == ord('v'):
            # Привязка функции для отметки экспонатов к окну с холстом
            cv2.setMouseCallback('Create canvas', mark_exhibit)

        # Ожидание нажатия клавиши 's' для сохранения холста в фото
        if cv2.waitKey(1) & 0xFF == ord('s'):
            # Сохраняем холст в фото
            cv2.namedWindow('Save canvas')

        if cv2.getWindowProperty('Create canvas', cv2.WND_PROP_VISIBLE) <1:
            break

    # Закрытие окна
    cv2.destroyAllWindows()


def get_makets():
    db_name = os.getenv('DB_NAME')
    user = os.getenv('USER')
    password = os.getenv('PASSWORD')
    db = DBActions(db_name, user, password)


window = Tk()
window.geometry('400x250')
window.title('Система распознавания поведения и эмоций')

btn_create = Button(window, text='Создание макета музея', command=create_maket)
btn_create.place(height=50, width=150, x=15, y=75)

btn_check = Button(window, text='Просмотр макетов', command=get_makets)
btn_check.place(height=50, width=150, x=235, y=75)


window.mainloop()

