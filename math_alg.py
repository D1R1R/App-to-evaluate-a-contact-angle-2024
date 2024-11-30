from math import atan, pi
from PIL import Image, ImageDraw
import numpy as np


class EvaluatingAlg():
    def __init__(self, path: str) -> None:
        # Чтение изображения в черно-белом формате
        self.img = Image.open(path).convert('L')

    def calc(self) -> tuple:
        # Преобразуем изображение в массив NumPy
        img_array = np.array(self.img)
        # Нахождение индексов первого и последнего нечерного пикселя по горизонтали и вертикали
        x_nonzero = np.where(img_array.max(axis=0) > 0)[0]
        y_nonzero = np.where(img_array.max(axis=1) > 0)[0]
        # Обрезка изображения
        img_cropped = img_array[y_nonzero[0]:y_nonzero[-1] + 1, x_nonzero[0]:x_nonzero[-1] + 1]

        white_indices = []
        top_point = None
        bottom_point = None
        left_point = None
        right_point = None

        # Перебор каждой строки обрезанного изображения
        for idx in range(img_cropped.shape[0]):
            # Нахождение индексов первого и последнего белого пикселя в строке
            row = img_cropped[idx]
            white_pixels = np.where(row == 255)[0]
            if len(white_pixels) > 0:
                if top_point is None:
                    top_point = idx
                bottom_point = idx
                start_index = white_pixels[0]
                end_index = white_pixels[-1]
                if left_point is None and right_point is None:
                    left_point = start_index
                    right_point = end_index
                else:
                    if start_index < left_point:
                        left_point = start_index
                    if end_index > right_point:
                        right_point = end_index
                white_indices.append((start_index, end_index))
                # находим диаметр
        d = [i[1] + i[0] for i in white_indices]
        s = len(d)
        d = sum(d) / s
        # находим высоту картинки
        height = img_cropped.shape[0]
        y_delta = d - height
        y = y_delta - d / 2  # уравнение прямой пересекающей окружность в центре 0
        x = -((d / 2) ** 2 - (d / 2 - y_delta) ** 2) ** 0.5
        # print(f"Координаты точки пересечения: {x}, {y}")
        k = y / x  # тангенс угла между радуисом и точкой пересечений
        alpha = atan(k) * 180 / pi
        x = alpha + 90  # искомый угол перпендикулярен радиусу

        rect = ((top_point, bottom_point), (left_point, right_point))
        return x, rect
