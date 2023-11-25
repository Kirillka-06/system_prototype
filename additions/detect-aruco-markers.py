import numpy as np
import cv2
import argparse


# Подключаемся к камере
cap = cv2.VideoCapture(1)

while True:
    # Получаем видео изображение с камеры
    ret, frame = cap.read()
    # Показываем видео изображение
    cv2.imshow('Video', frame)
    
    # Загружаем словарь с нужными ArUco маркерами
    arucoDict = cv2.aruco.getPredefinedDictionary(cv2.aruco.DICT_6X6_250)
    # Определяем параметры
    arucoParams = cv2.aruco.DetectorParameters()
    # Обнаруживаем аруко маркеры
    corners, ids, rejected = cv2.aruco.detectMarkers(
        frame, arucoDict, parameters=arucoParams)
    print(corners)

    # Проверяем, что хотя бы один аруко маркер был обнаружен
    if len(corners) > 0:
		# Выравниваем ids в обычный список ids
        ids = ids.flatten()
        # Проходимся по обнаруженным углам ArUco
        for markerCorner, marker_id in zip(corners, ids):
            # Извлекаем углы маркера (которые всегда возвращаются
            # в верхнем левом, верхнем правом,
            # нижнем правом и нижнем левом нижнем углу)
            corners = markerCorner.reshape((4, 2))
            (topLeft, topRight, bottomRight, bottomLeft) = corners

            # Преобразуем каждую из пар координат (x, y) в целые числа
            topRight = (int(topRight[0]), int(topRight[1]))
            bottomRight = (int(bottomRight[0]), int(bottomRight[1]))
            bottomLeft = (int(bottomLeft[0]), int(bottomLeft[1]))
            topLeft = (int(topLeft[0]), int(topLeft[1]))

            # Рисуем ограничивающую рамку для ArUco маркера
            cv2.line(frame, topLeft, topRight, (0, 255, 0), 2)
            cv2.line(frame, topRight, bottomRight, (0, 255, 0), 2)
            cv2.line(frame, bottomRight, bottomLeft, (0, 255, 0), 2)
            cv2.line(frame, bottomLeft, topLeft, (0, 255, 0), 2)

            # Вычисляем и рисуем центр (x, y) - координаты маркера ArUco
            cX = int((topLeft[0] + bottomRight[0]) / 2.0)
            cY = int((topLeft[1] + bottomRight[1]) / 2.0)
            cv2.circle(frame, (cX, cY), 4, (0, 0, 255), -1)

            # Пишем ID ArUco маркера на видео
            cv2.putText(frame, str(marker_id),
				(topLeft[0], topLeft[1] - 15),
				cv2.FONT_HERSHEY_SIMPLEX,
				0.5, (0, 255, 0), 2)

	# Показ видео с камеры
    cv2.imshow('Video', frame)

    # При нажатии на кнопку 'q' на клавиатуре изображение сохранится
    if cv2.waitKey(1) & 0xFF == ord('q'):
        break

    # Закрытие окна
    if cv2.getWindowProperty('Video', cv2.WND_PROP_VISIBLE) < 1:
        break

cap.release()
cv2.destroyAllWindows()