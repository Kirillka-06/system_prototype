import cv2
import io
from cv2 import aruco
import tkinter as tk
from tkinter import ttk, NW
import tkinter.messagebox as tk_mb
import tkinter.filedialog as tk_fd
from PIL import Image, ImageTk

ARUCO_DICT = {
    'DICT_4X4_50': aruco.DICT_4X4_50,
    'DICT_4X4_100': aruco.DICT_4X4_100,
    'DICT_4X4_250': aruco.DICT_4X4_250,
    'DICT_4X4_1000': aruco.DICT_4X4_1000,
    'DICT_5X5_50': aruco.DICT_5X5_50,
    'DICT_5X5_100': aruco.DICT_5X5_100,
    'DICT_5X5_250': aruco.DICT_5X5_250,
    'DICT_5X5_1000': aruco.DICT_5X5_1000,
    'DICT_6X6_50': aruco.DICT_6X6_50,
    'DICT_6X6_100': aruco.DICT_6X6_100,
    'DICT_6X6_250': aruco.DICT_6X6_250,
    'DICT_6X6_1000': aruco.DICT_6X6_1000,
    'DICT_7X7_50': aruco.DICT_7X7_50,
    'DICT_7X7_100': aruco.DICT_7X7_100,
    'DICT_7X7_250': aruco.DICT_7X7_250,
    'DICT_7X7_1000': aruco.DICT_7X7_1000,
    'DICT_ARUCO_ORIGINAL': aruco.DICT_ARUCO_ORIGINAL
}
ARUCO_CHOICES = list(ARUCO_DICT.keys())
byte_image = None

def generate_aruco_marker(dict, id):
    try:
        # Получаем предустановленный словарь аруко маркеров
        dictionary = aruco.getPredefinedDictionary(ARUCO_DICT[dict])
        # Сгенерировать изображение аруко маркера
        aruco_marker_image = aruco.generateImageMarker(dictionary, int(id), 200, borderBits=1)

        # Кодируем массив картинки в формат .png
        img_imcode = cv2.imencode('.png', aruco_marker_image)
        # Превращаем массив картинки в байт-строчку и сохраняем её глобально
        global img
        img = img_imcode[1].tobytes()
        return img
    except KeyError:
        tk_mb.showerror(title='Ошибка', message='Выбор словаря обязателен')
    except ValueError:
        tk_mb.showerror(title='Ошибка', message='Поле ID обязательно к заполнению')

def show_aruco_marker(window: tk.Misc, dict, id):
    # Получаем сгенерированный аруко маркер в байтах
    generated_aruco_image = generate_aruco_marker(dict, id)

    # 
    opened_aruco_image = Image.open(io.BytesIO(generated_aruco_image))
    image_label = tk.Label(window, name='image_label')
    aruco_image = ImageTk.PhotoImage(opened_aruco_image)
    image_label.image = aruco_image
    image_label['image'] = image_label.image

    canvas: tk.Canvas = window.children['canvas']
    canvas.create_image((15, 15), state = "normal", image=aruco_image, anchor=NW)
    canvas.place(x=187.5, y=250)

def save_aruco_marker():
    try:
        filepath = tk_fd.asksaveasfilename(defaultextension='png', initialfile='aruco-marker.png')
        if filepath != '':
            aruco_image = Image.open(io.BytesIO(img))
            aruco_image.save(filepath)
            return
        raise NameError('Выбор ArUco маркера обязателен')
    except NameError:
        tk_mb.showerror(title='Ошибка', message='Выберите ArUco маркер')

def define_aruco(window: tk.Misc):
    aruco_dictionary_label = tk.Label(
        window,
        name='aruco_dictionary_label',
        text='Aruco dictionary'
    ) 
    aruco_dictionary_label.place(x=50, y=55)

    aruco_choices_var = tk.StringVar(value=ARUCO_CHOICES[10])
    combobox = ttk.Combobox(
        window,
        name='combobox',
        textvariable=aruco_choices_var,
        values=ARUCO_CHOICES,
        state='readonly'
    )
    combobox.place(height=50, width=225, x=50, y=75)

    id_label = tk.Label(
        window,
        name='id_label',
        text='Marker ID'
    )
    id_label.place(x=325, y=55)
    
    entry_id = tk.Entry(window, name='entry_id')
    entry_id.place(height=50, width=225, x=325, y=75)
    
    button_generate_aruco = tk.Button(
        window,
        name='button_generate_aruco',
        text='Generate ArUco marker',
        command=lambda: show_aruco_marker(window, combobox.get(), entry_id.get()))
    button_generate_aruco.place(height=50, width=150, x=225, y=165)

    canvas = tk.Canvas(window, name='canvas', bg='white', height=225, width=225)
    canvas.place(x=187.5, y=250)

    button_save_aruco = tk.Button(
        window,
        name='button_save_aruco',
        text='Save ArUco marker',
        command=save_aruco_marker
    )
    button_save_aruco.place(height=50, width=150, x=225, y=515)

def main():
    main_window = tk.Tk()
    main_window.geometry('600x600')
    main_window.title('Create ArUco marker')

    define_aruco(main_window)

    main_window.mainloop()

if __name__ == '__main__':
    main()
