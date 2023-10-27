from tkinter import Tk, Button, Entry, Label
import cv2
import numpy as np
import time
import psycopg2
from dotenv import load_dotenv
from dotenv import find_dotenv
import os

# Загрузка переменных окружения
load_dotenv(find_dotenv())

global db_name
global user
global password
DB_NAME = os.getenv('DB_NAME')
DB_USER = os.getenv('USER')
DB_PASSWORD = os.getenv('PASSWORD')

# Класс для работы с бд
class DBActions:
    def __init__(self, db_name, user, password, host='localhost'):
        self.__db_name = db_name
        self.__user = user
        self.__password = password
        self.__host = host
        self.__conn = psycopg2.connect(
            dbname=db_name,
            user=user,
            password=password,
            host=host,
        )
        self.__cursor = self.__conn.cursor()
    
    def create_notion(self, name, data):
        self.__cursor.execute(
            'INSERT INTO schemes (name, data) '
            f'VALUES (%(name)s, %(data)s)',
            {
                'name': name,
                'data': str(data)
            }
        )
        self.__conn.commit()
        self.__conn.close()
    
    def get_notion(self):
        self.__cursor.execute('SELECT * FROM schemes')

# Функция создания макета
def create_layout():

    # Создание пустого холста
    canvas = np.zeros((480, 640, 3), dtype=np.uint8)

    global project
    global exhibits
    global cameras
    project = {
        'exhibits': [],
        'cameras': []
    }

    global is_clicked
    is_clicked = False

    RADIUS = 10


    def mark_exhibit(event, x, y, flags, param):
        """
        Нажатие кнопки 'v' на клавиатуре.
        Отмечаем экспонаты
        """

        if event == cv2.EVENT_LBUTTONUP:
            # Рисуем зеленый прямоугольник на холсте
            cv2.rectangle(canvas, (x-10, y-10), (x+10, y+10), (0, 255, 0), -1)

            exhibits = project.get('exhibits')
            exhibits.append(((x-10, y-10), (x+10, y+10), (0, 255, 0), -1))
     
    def mark_camera(event, x, y, flags, param):
        """
        Нажатие кнопки 'с' на клавиатуре.
        Отмечаем Камеры
        """

        global is_clicked

        # Ставим камеру, если первый клик
        if event == cv2.EVENT_LBUTTONDOWN and not is_clicked:
            cv2.circle(canvas, (x, y), RADIUS, (0, 0, 255), -1)

            global center_x
            global center_y
            center_x = x
            center_y = y

            is_clicked = True
            return

        # Указываем поле зрения камеры, если второй клик
        if event == cv2.EVENT_LBUTTONDOWN and is_clicked:
            angle = np.degrees(np.arctan2(y - center_y, x - center_x))
            draw_triangle(angle, center_x , center_y)

            is_clicked = False
            return


    def draw_triangle(angle, center_x, center_y):
        """Отрисовка поля зрения камеры"""

        # Вычисление координат вершин треугольника
        length = 180

        # Определение двух других вершин
        vertex2_x = center_x + int(length * np.cos(np.radians(angle + 300)))
        vertex2_y = center_y + int(length * np.sin(np.radians(angle + 300)))
        vertex3_x = center_x + int(length * np.cos(np.radians(angle + 60)))
        vertex3_y = center_y + int(length * np.sin(np.radians(angle + 60)))

        # Отрисовка треугольника на холсте
        cv2.line(canvas, (center_x, center_y), (vertex2_x, vertex2_y), (255, 0, 0), 2)
        cv2.line(canvas, (center_x, center_y), (vertex3_x, vertex3_y), (255, 0, 0), 2)
        cv2.line(canvas, (vertex3_x, vertex3_y), (vertex2_x, vertex2_y), (255, 0, 0), 2)

        # Добавление координат камеры в временный массив
        cameras = project.get('cameras')
        cameras.append(
            (center_x,
             center_y,
             vertex2_x,
             vertex2_y,
             vertex3_x,
             vertex3_y)
        )
    
    def save_scheme_window():
        """
        Нажатие кнопки 's' на клавиатуре.
        Сохраняем проект
        """

        # Создаем окно
        root = Tk()

        # Создаем текстовое поле
        label = Label(root, text='Enter name of canvas', width=30)
        label.pack()

        # Поле ввода названия
        global entry_name
        entry_name = Entry(root, width=30)
        entry_name.pack()

        # Кнопка сохранения проекта
        button = Button(root, text='Save', command=save_scheme_to_db)
        button.pack()
        root.mainloop()
    
    def save_scheme_to_db():
        """
        Создаем новую запись в таблице для схем
        """

        # Создание записи в бд
        name = entry_name.get()
        db = DBActions(DB_NAME, DB_USER, DB_PASSWORD)
        db.create_notion(name, project)

    # Создание окна с холстом
    cv2.namedWindow('Create canvas')
    # Привязка функций для отметки камеры и экспоната к окну с холстом
    cv2.setMouseCallback('Create canvas', mark_exhibit)

    # Главный цикл приложения
    while True:
        # Показываем холст
        cv2.imshow('Create canvas', canvas)

        # Ожидание нажатия клавиши 'v' для переключения в режим отметки экспонатов
        if cv2.waitKey(1) & 0xFF == ord('v'):
            # Привязка функции для отметки экспонатов к окну с холстом
            cv2.setMouseCallback('Create canvas', mark_exhibit)

        # Ожидание нажатия клавиши 'c' для переключения в режим отметки камер
        if cv2.waitKey(1) & 0xFF == ord('c'):
            # Привязка функции для отметки камер к окну с холстом
            cv2.setMouseCallback('Create canvas', mark_camera)

        # Ожидание нажатия клавиши 's' для сохранения холста в фото
        if cv2.waitKey(1) & 0xFF == ord('s'):
            save_scheme_window()

        if cv2.getWindowProperty('Create canvas', cv2.WND_PROP_VISIBLE) <1:
            break

    # Закрытие окна
    cv2.destroyAllWindows()

# Функция получения списка
def get_layouts():
    db = DBActions(DB_USER, DB_USER, DB_PASSWORD)

def main():
    # Создание окна
    window = Tk()
    window.geometry('400x250')
    window.title('Система распознавания поведения и эмоций')

    btn_create = Button(window, text='Создание макета музея', command=create_layout)
    btn_create.place(height=50, width=150, x=15, y=75)

    btn_check = Button(window, text='Просмотр макетов', command=get_layouts)
    btn_check.place(height=50, width=150, x=235, y=75)

    window.mainloop()

if __name__ == '__main__':
    main()
