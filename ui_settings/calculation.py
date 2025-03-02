import os
import math
import numpy as np
from PIL import Image, ImageDraw


class EvaluatingAlg():
    def __init__(self, path: str, width: int, beam_length: int, angel_type: str, state: bool) -> None:
        self._img_list = list()
        if not state:
            for imgs in os.listdir(path):
                path_img = os.path.join(path, imgs)
                self._img_list.append(path_img)
        else:
            self._img_list.append(path)

        self.width = width
        self.beam_length = beam_length
        self.angel_type = 0 if angel_type == "Градусы °" else 1
    
    def find_rect(self, imgs_list: list) -> tuple:
        result = list()
        for img in imgs_list:
            path = self._img_list[imgs_list.index(img)]

            img_array = np.array(img)  # Преобразуем изображение в массив NumPy / mask
            top_point = None
            bottom_point = None
            left_point = None
            right_point = None
            for idx in range(img_array.shape[0]):
                row = img_array[idx]
                white_pixels = np.where(row == 255)[0]
                if len(white_pixels) > 0:
                    if top_point is None:
                        top_point = idx
                    bottom_point = idx
                    start_index = white_pixels[0]
                    end_index = white_pixels[-1]
                    midle = (end_index - start_index) // 2
                    if left_point is None and right_point is None:
                        left_point = start_index
                        right_point = end_index
                    else:
                        if start_index < left_point:
                            left_point = start_index
                        if end_index > right_point:
                            right_point = end_index
            rect = ((left_point, top_point, right_point, bottom_point), midle)  #x0, y0, x, y, m
            result.append((path, rect))
        return result
    
    def calc(self, values: tuple) -> int:
        # TODO: ускорить
        rect, midle = values
        # Ищем центр окружности
        diff = (abs(rect[0] - rect[2]) // 2)  # Смотрим по х
        x0 = rect[0] + diff
        y0 = rect[1] + diff
        # Редиус
        r = abs(rect[0] - x0)
        # Задаем точку
        y = rect[3]
        x = x0 - (math.sqrt((r ** 2) - ((y0 - y) ** 2)))
        # Ищем k касательной
        k = self.derivative_f(x, x0, r)
        angel1 = abs(math.degrees(math.atan(k)))
        # Ищем k секущей
        k2 = 0
        # TODO: Учитывать наклон поверхности
        # if midle <= 5:  # or angel1 <= 5
        #     angel2 = 0
        # else:
        #     k2 = abs(y0 - y) / abs(x0 - midle)
        #     angel2 = math.degrees(math.atan(k2))
        answer = 180 - angel1
        if self.angel_type:
            answer = math.radians(answer)
        return (answer, (x0, y0), (k, k2), r)

    def derivative_f(self, x: int, x0: int, r: int) -> int:
        """Производная к функции. Возвращает значение в точке х."""
        func = (x - x0) / (math.sqrt(-(x ** 2) + (2 * x * x0) - (x0 ** 2) + (r ** 2)))
        return func
    
    def draw(self, img_path: str, permissions: tuple, ks: int, rect: tuple, r: int, center: tuple, angel: int) -> Image:
        """Draw figures: rect - #ec00fe; circle - #006ffe; line and data - #6fa8dc"""
        # permisions: isrect, iscircle, isangel, isdata
        img = Image.open(img_path).convert("RGB")
        draw = ImageDraw.Draw(img)
        x0, y0 = center
        y = rect[0][3]
        x = x0 - (math.sqrt((r ** 2) - ((y0 - y) ** 2)))
        k, k2 = ks
        if permissions[0]:
            # Рисуем квадрат и ц.о.
            draw.rectangle(rect[0], outline="#ec00fe", width=self.width)
            draw.line(rect[0], fill="#ec00fe", width=self.width)
            draw.line((rect[0][0], rect[0][3], rect[0][2], rect[0][1]), fill="#ec00fe", width=self.width)

            # draw.point(center, fill="#33ff00")
        if permissions[1]:
            # Рисуем окружность
            draw.ellipse((x0 - r, y0 - r, x0 + r, y0 + r), outline="#006ffe", width=self.width)
        if permissions[2]:
            # Рисуем касательную и плоскость
            # TODO
            draw.line(((x - self.beam_length), y + (k * self.beam_length), x, y), fill="#6fa8dc", width=self.width)
            draw.line((x, y, (x + self.beam_length), y + (k2 * self.beam_length)), fill="#6fa8dc", width=self.width)
            # TODO: arc
            # half = self.beam_length // 4
            # l = 90  # Смещение
            # draw.arc(
            #     ((x - half), y + (k * half), (x + half), y + (k2 * half) + l),
            #     start=225,
            #     end=-3,
            #     fill="#6fa8dc",
            #     width=self.width
            #     )
        if permissions[3]:
            # Подписываем угол
            text = f'β = {angel}'
            draw.text((0, 0), text, fill="white")
        return img
