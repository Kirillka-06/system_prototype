import cv2 as cv
import numpy as np

# Загрузить предопределенный словарь
dictionary = cv.aruco.Dictionary.get(cv.aruco.DICT_6X6_250)

# Сгенерировать маркер
markerImage = np.zeros((200, 200), dtype=np.uint8)
markerImage = cv.aruco.drawMarker(dictionary, 33, 200, markerImage, 1)

cv.imwrite("marker33.png", markerImage)