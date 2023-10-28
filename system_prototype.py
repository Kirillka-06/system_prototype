import os

import ast

from tkinter import Tk, Button, Entry, Label

import cv2
import numpy as np

import psycopg2
from psycopg2 import sql

from dotenv import load_dotenv


# Загрузка переменных окружения
load_dotenv()

global db_name
global user
global password
DB_NAME = os.getenv('DB_NAME')
DB_USER = os.getenv('USER')
DB_PASSWORD = os.getenv('PASSWORD')

RADIUS = 5
LENGTH = 180

# Класс для работы с бд
class DBActions:
    
    def __init__(self, db_name, user, password, host='localhost'):
        self.__db_name = db_name
        self.__user = user
        self.__password = password
        self.__host = host
        #print(db_name)
        #print(password)
        print(db_name)
        print(DB_NAME)
        
        self.__conn = psycopg2.connect(
            dbname=self.__db_name,
            user=self.__user,
            password=self.__password,
            host=self.__host,
        )
        self._cursor = self.__conn.cursor()
        self._cursor.execute('SELECT current_database()')
        print(self._cursor.fetchall())
    
    def create_notion(self, name, data):
        self._cursor.execute(
            'INSERT INTO schemes (name, objects) '
            f'VALUES (%(name)s, %(data)s)',
            {
                'name': name,
                'data': str(data)
            }
        )
        self.__conn.commit()
        self.__conn.close()
    
    def get_notion(self, table='schemes'):
        self._cursor.execute(f'SELECT name, objects FROM "{table}";')
        #self.__cursor.execute(sql.SQL('SELECT * FROM {}').format(sql.Identifier(table)))
        return self._cursor.fetchall()


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

    def mark_exhibit(event, x, y, flags, param):
        """
        Нажатие кнопки 'v' на клавиатуре.
        Отмечаем экспонаты
        """

        if event == cv2.EVENT_LBUTTONUP:
            # Рисуем зеленый прямоугольник на холсте
            cv2.rectangle(canvas, (x-10, y-10), (x+10, y+10), (0, 255, 0), -1)

            exhibits = project.get('exhibits')
            exhibits.append((x, y, (0, 255, 0), -1))
            #print(exhibits)

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
            #print(f'camera {x} {y}')

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
        #print(f'draw {center_x} {center_y}')
        length = 180

        # Определение двух других вершин
        vertex2_x = center_x + int(LENGTH * np.cos(np.radians(angle + 300)))
        vertex2_y = center_y + int(LENGTH * np.sin(np.radians(angle + 300)))
        vertex3_x = center_x + int(LENGTH * np.cos(np.radians(angle + 60)))
        vertex3_y = center_y + int(LENGTH * np.sin(np.radians(angle + 60)))

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
        #print(cameras)
    
    def save_scheme_window():
        """
        Нажатие кнопки 's' на клавиатуре.
        Сохраняем проект
        """

        #print(project)

        # Создаем окно
        global root_save_scheme
        root_save_scheme = Tk()

        # Создаем текстовое поле
        label = Label(root_save_scheme, text='Enter name of canvas', width=30)
        label.pack()

        # Поле ввода названия
        global entry_name
        entry_name = Entry(root_save_scheme, width=30)
        entry_name.pack()

        # Кнопка сохранения проекта
        button = Button(root_save_scheme, text='Save', command=save_scheme_to_db)
        button.pack()

        root_save_scheme.mainloop()

    def save_scheme_to_db():
        """
        Создает новую запись в таблице для схем
        """
        
        #print(entry_name.get())

        # Создание записи в бд
        name = entry_name.get()
        db = DBActions(DB_NAME, DB_USER, DB_PASSWORD)
        db.create_notion(name, project)

        # Закрытие окон редактирования
        root_save_scheme.destroy()
        cv2.destroyWindow('Create canvas')

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
    #def draw_objects(objects):

    def show_layout(objects):
        objects = ast.literal_eval(objects)
        canvas = np.zeros((480, 640, 3), dtype=np.uint8)
        cv2.namedWindow('Show  layout')

        while True:
            cv2.imshow('Show layout', canvas)
            for camera in objects.get('cameras'):
                cv2.circle(canvas, (camera[0], camera[1]), RADIUS, (0, 0, 255), -1)

                cv2.line(canvas, (camera[0], camera[1]), (camera[2], camera[3]), (255, 0, 0), 2)
                cv2.line(canvas, (camera[0], camera[1]), (camera[4], camera[5]), (255, 0, 0), 2)
                cv2.line(canvas, (camera[4], camera[5]), (camera[2], camera[3]), (255, 0, 0), 2)
            
            for exhibitions in objects.get('exhibits'):
                ...
            
            if cv2.getWindowProperty('Create canvas', cv2.WND_PROP_VISIBLE) <1:
                break
        
        cv2.destroyAllWindows()



    def create_button(window, text, objects):
        btn = Button(window, text=text, command=lambda: show_layout(objects))
        return btn

    root_get_layouts = Tk()
    root_get_layouts.geometry('400x250')
    root_get_layouts.title('Список схем')

    db = DBActions(DB_NAME, DB_USER, DB_PASSWORD)
    #print(db.get_notion())
    print(db.get_notion())
    #print(db._cursor.fetchall())
    n_column = 1
    n_row = 1
    for notion in db.get_notion():
        name, objects = notion
        create_button(root_get_layouts, name, objects).grid(column=n_column, row=n_row)
        n_row += 1

    
    #create_button(root_get_layouts, 'da')#.grid(column=1, row=1)
    


# Функция для просмотра статистики
def check_statistics():
    ...

def main():
    # Создание основного окна
    main_window = Tk()
    main_window.geometry('400x250')
    main_window.title('Система распознавания поведения и эмоций')

    btn_create = Button(main_window, text='Создание макета музея', command=create_layout)
    btn_create.place(height=50, width=150, x=15, y=75)

    btn_check = Button(main_window, text='Просмотр макетов', command=get_layouts)
    btn_check.place(height=50, width=150, x=235, y=75)

    main_window.mainloop()

if __name__ == '__main__':
    main()
