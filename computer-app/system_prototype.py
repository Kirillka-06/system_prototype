import os

import ast

import tkinter as tk
from tkinter import Tk, Listbox, StringVar
from tkinter.ttk import (Button,
                         Entry,
                         Label,
                         Scrollbar,
                         Frame,)

import cv2
import numpy as np

import psycopg2

from dotenv import load_dotenv
from pygrabber.dshow_graph import FilterGraph


# Загрузка переменных окружения
load_dotenv()

# Получение переменных окружения
#global db_name
#global user
#global password
DB_NAME = os.getenv('DB_NAME')
DB_USER = os.getenv('USER')
DB_PASSWORD = os.getenv('PASSWORD')
DB_TABLE = os.getenv('DB_TABLE')

# дефолт данные для объектов макета
RADIUS = 5
LENGTH = 180

CAMERA_COLOR = (0, 0, 255)
EXHIBITION_COLOR = (0, 255, 0)
CAMERA_FIELD_OF_VIEW_COLOR = (255, 0, 0)

# Класс для работы с бд
class DBActions:

    def __init__(self, db_name, user, password, table, host='localhost'):
        self.__db_name = db_name
        self.__user = user
        self.__password = password
        self.__host = host
        self.__table = table
        
        self.__conn = psycopg2.connect(
            dbname=self.__db_name,
            user=self.__user,
            password=self.__password,
            host=self.__host,
        )
        self.__cursor = self.__conn.cursor()
        #self._cursor.execute('SELECT current_database()')
        #print(self._cursor.fetchall())
    
    def create_notion(self, name, data):
        self.__cursor.execute(
            f'INSERT INTO {self.__table} (name, objects) '
            f'VALUES (%(name)s, %(data)s)',
            {
                'name': name,
                'data': str(data)
            }
        )
        self.__conn.commit()
        self.__conn.close()
    
    def get_notion_list(self):
        self.__cursor.execute(f'SELECT id, name, objects FROM "{self.__table}";')
        notion_list = self.__cursor.fetchall()
        #self.__conn.close()
        return notion_list

    def edit_notion(self, id):
        ...

    def delete_notion(self, id):
        self.__cursor.execute(f'DELETE FROM {self.__table} WHERE id={id};')
        self.__conn.commit()
        #self.__conn.close()


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
            cv2.rectangle(canvas, (x-10, y-10), (x+10, y+10), EXHIBITION_COLOR)

            # Добавление координат экспоната в временный массив
            exhibits = project.get('exhibits')
            exhibits.append((x, y))

    def mark_camera(event, x, y, flags, param):
        """
        Нажатие кнопки 'с' на клавиатуре.
        Отмечаем Камеры
        """

        global is_clicked

        # Ставим камеру, если первый клик
        if event == cv2.EVENT_LBUTTONDOWN and not is_clicked:
            cv2.circle(canvas, (x, y), RADIUS, CAMERA_COLOR, -1)

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

        # Определение двух других вершин
        vertex2_x = center_x + int(LENGTH * np.cos(np.radians(angle + 300)))
        vertex2_y = center_y + int(LENGTH * np.sin(np.radians(angle + 300)))
        vertex3_x = center_x + int(LENGTH * np.cos(np.radians(angle + 60)))
        vertex3_y = center_y + int(LENGTH * np.sin(np.radians(angle + 60)))

        # Отрисовка треугольника на холсте
        cv2.line(canvas, (center_x, center_y), (vertex2_x, vertex2_y), CAMERA_FIELD_OF_VIEW_COLOR, 1)
        cv2.line(canvas, (center_x, center_y), (vertex3_x, vertex3_y), CAMERA_FIELD_OF_VIEW_COLOR, 1)
        cv2.line(canvas, (vertex3_x, vertex3_y), (vertex2_x, vertex2_y), CAMERA_FIELD_OF_VIEW_COLOR, 1)

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
        root_save_scheme = Tk()

        # Создаем текстовое поле
        label = Label(root_save_scheme, text='Enter name of canvas', width=30)
        label.pack()

        # Поле ввода названия
        entry_name = Entry(root_save_scheme, width=30)
        entry_name.pack()

        # Кнопка сохранения проекта
        button = Button(
            root_save_scheme,
            text='Save',
            command=lambda: save_scheme_to_db(root_save_scheme, entry_name))
        button.pack()

        root_save_scheme.mainloop()

    def save_scheme_to_db(window: Tk, entry_name):
        """
        Создает новую запись в таблице для схем
        """

        # Создание записи в бд
        name = entry_name.get()
        db = DBActions(DB_NAME, DB_USER, DB_PASSWORD, DB_TABLE)
        db.create_notion(name, project)

        # Закрытие окон редактирования
        window.destroy()
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
        if cv2.waitKey(1) & 0xFF in (ord('v'), ord('V')):
            # Привязка функции для отметки экспонатов к окну с холстом
            cv2.setMouseCallback('Create canvas', mark_exhibit)

        # Ожидание нажатия клавиши 'c' для переключения в режим отметки камер
        if cv2.waitKey(1) & 0xFF in (ord('c'), ord('C')):
            # Привязка функции для отметки камер к окну с холстом
            cv2.setMouseCallback('Create canvas', mark_camera)

        # Ожидание нажатия клавиши 's' для сохранения холста в фото
        if cv2.waitKey(1) & 0xFF in (ord('s'), ord('S')):
            save_scheme_window()

        if cv2.getWindowProperty('Create canvas', cv2.WND_PROP_VISIBLE) < 1:
            break

    # Закрытие окна
    cv2.destroyAllWindows()

# Функция получения списка
def get_layouts():
    def connect_to_camera(objects):
        root_connect_to_camera = Tk()
        root_connect_to_camera.geometry('400x250')
        root_connect_to_camera.title('Подключение камер')

        # Получение списка доступных камер
        graph = FilterGraph()

        devices_list = graph.get_input_devices()
        print(graph.get_input_devices())
        # Получение индекса камеры
        device = graph.get_input_devices().index(devices_list[0])
        print(device)

        cameras_name_var = StringVar(root_connect_to_camera, value=devices_list)
        camera_listbox = Listbox(root_connect_to_camera, listvariable=cameras_name_var)
        camera_listbox.pack(side=tk.LEFT, fill=tk.BOTH, expand=1)

        scrollbar = Scrollbar(root_connect_to_camera, orient='vertical', command=camera_listbox.yview)
        scrollbar.pack(side=tk.RIGHT, fill=tk.Y)
        
        camera_listbox['yscrollcommand'] = scrollbar.set
        #print(root_connect_to_camera.winfo_children()[0].winfo_children())
        root_connect_to_camera.mainloop()

    def draw_objects(canvas, objects):
        for camera in objects.get('cameras'):
                cv2.circle(canvas, (camera[0], camera[1]), RADIUS, CAMERA_COLOR, -1)

                cv2.line(canvas, (camera[0], camera[1]), (camera[2], camera[3]), CAMERA_FIELD_OF_VIEW_COLOR, 2)
                cv2.line(canvas, (camera[0], camera[1]), (camera[4], camera[5]), CAMERA_FIELD_OF_VIEW_COLOR, 2)
                cv2.line(canvas, (camera[4], camera[5]), (camera[2], camera[3]), CAMERA_FIELD_OF_VIEW_COLOR, 2)

        for exhibition in objects.get('exhibits'):
            cv2.rectangle(canvas, (exhibition[0]-10, exhibition[1]-10), (exhibition[0]+10, exhibition[1]+10), EXHIBITION_COLOR, -1)

    def show_layout(objects):
        objects = ast.literal_eval(objects)
        canvas = np.zeros((480, 640, 3), dtype=np.uint8)

        while True:
            draw_objects(canvas, objects)
            cv2.imshow('Show layout', canvas)
            cv2.waitKey(0)

            if cv2.getWindowProperty('Create canvas', cv2.WND_PROP_VISIBLE) < 1:
                break

        cv2.destroyAllWindows()

    def edit_layout(id):
        db.edit_notion(id)

    def delete_layout(id):
        db.delete_notion(id)

    def create_buttons(window, id, text, objects, n_row):
        # Нумерация объектов
        object_number = Label(window, text=f'{n_row}')
        object_number.grid(column=1, row=n_row)#, ipadx=5, ipady=5, padx=45)

        # Коннект с камерами
        connect_btn = Button(window, text='conn', command=lambda: connect_to_camera(objects))
        connect_btn.grid(column=2, row=n_row)#, ipadx=10, ipady=5)

        # Просмотр макета
        show_btn = Button(window, text=text, command=lambda: show_layout(objects))
        show_btn.grid(column=3, row=n_row)#, ipadx=15, ipady=5)

        # Редактировать макет
        edit_btn = Button(window, text='edit', command=lambda: edit_layout(id))
        edit_btn.grid(column=4, row=n_row)#, ipadx=15, ipady=5)

        # Удалить макет
        del_btn = Button(window, text='del', command=lambda: delete_layout(id))
        del_btn.grid(column=5, row=n_row)#, ipadx=15, ipady=5)

    # Создание окна
    root_get_layouts = Tk('Список схем')
    root_get_layouts.geometry('400x250')
    root_get_layouts.title('Список схем')

    # Подключение к бд
    db = DBActions(DB_NAME, DB_USER, DB_PASSWORD, DB_TABLE)

    # Интерфейс окна
    #n_column = 1
    n_row = 1
    for notion in db.get_notion_list():
        id, name, objects = notion
        frame_notion_buttons = Frame(root_get_layouts, borderwidth=1, relief=tk.SOLID)
        create_buttons(frame_notion_buttons, id, name, objects, n_row)
        #button = create_button(root_get_layouts, name, objects, n_row)
        #button.place(height=50, width=150)
        #button.grid(column=n_column, row=n_row, ipadx=15, ipady=5)
        frame_notion_buttons.pack(pady=10)
        n_row += 1

def viewing_cameras():
    def on_select(event):
        print(event)
        camera_element = camera_listbox.get(camera_listbox.curselection())
        print(camera_element)
        device_index = graph.get_input_devices().index(camera_element)

        # Подключаемся к камере
        cap = cv2.VideoCapture(device_index)

        while True:
            # Получаем видео изображение с камеры
            ret, frame = cap.read()
            # Показываем видео изображение
            cv2.imshow('Video', frame)
    

            # Показ видео с камеры
            #cv2.imshow('Video', frame)

            # При нажатии на кнопку 'q' на клавиатуре изображение сохранится
            if cv2.waitKey(1) & 0xFF == ord('q'):
                break

            # Закрытие окна
            if cv2.getWindowProperty('Video', cv2.WND_PROP_VISIBLE) < 1:
                break

        cap.release()
        cv2.destroyAllWindows()

    root_viewing_cameras = Tk()
    root_viewing_cameras.geometry('400x250')
    root_viewing_cameras.title('Просмотр камер')

    # Получение списка доступных камер
    graph = FilterGraph()

    devices_list = graph.get_input_devices()
    print(graph.get_input_devices())
    # Получение индекса камеры
    device = graph.get_input_devices().index(devices_list[0])
    print(device)

    cameras_name_var = StringVar(root_viewing_cameras, value=devices_list)
    camera_listbox = Listbox(root_viewing_cameras, listvariable=cameras_name_var)
    camera_listbox.pack(side=tk.LEFT, fill=tk.BOTH, expand=1)

    scrollbar = Scrollbar(root_viewing_cameras, orient='vertical', command=camera_listbox.yview)
    scrollbar.pack(side=tk.RIGHT, fill=tk.Y)
        
    camera_listbox['yscrollcommand'] = scrollbar.set
    camera_listbox.bind('<<ListboxSelect>>', on_select)
    #print(root_viewing_cameras.winfo_children()[0].winfo_children())

    root_viewing_cameras.mainloop()

# Функция для просмотра статистики
def check_statistics():
    ...

def main():
    # Создание основного окна
    main_window = Tk()
    main_window.geometry('400x250')
    main_window.title('Система распознавания поведения и эмоций')

    # Кнопки основного функционала программы
    btn_create = Button(main_window, text='Создание макета музея', command=create_layout)
    btn_create.place(height=50, width=150, x=15, y=50)

    btn_check = Button(main_window, text='Просмотр макетов', command=get_layouts)
    btn_check.place(height=50, width=150, x=235, y=50)

    btn_check = Button(main_window, text='Просмотр камер', command=viewing_cameras)
    btn_check.place(height=50, width=150, x=125, y=125)

    # Функция, чтобы окно не закрывалось
    main_window.mainloop()

if __name__ == '__main__':
    main()
