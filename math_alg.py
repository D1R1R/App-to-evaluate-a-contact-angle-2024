from math import atan, pi

from PIL import Image
import numpy as np 



class EvaluatingAlg():
    def __init__(self, path: str):
        # Чтение изображения в черно-белом формате 
        self.img = Image.open(path).convert('L')
    def calc(self):
        # Преобразуем изображение в массив NumPy  
        img_array = np.array(self.img)
        # Нахождение индексов первого и последнего нечерного пикселя по горизонтали и вертикали  
        x_nonzero = np.where(img_array.max(axis=0) > 0)[0]
        y_nonzero = np.where(img_array.max(axis=1) > 0)[0]
        # Обрезка изображения  
        img_cropped = img_array[y_nonzero[0]:y_nonzero[-1] + 1, x_nonzero[0]:x_nonzero[-1] + 1]  
        
        white_indices = []  
        
        # Перебор каждой строки обрезанного изображения  
        for row in img_cropped:  
            # Нахождение индексов первого и последнего белого пикселя в строке  
            white_pixels = np.where(row == 255)[0]  
            if len(white_pixels) > 0:  
                start_index = white_pixels[0]  
                end_index = white_pixels[-1]  
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
        k=y/x  # тангенс угла между радуисом и точкой пересечений  
        alpha = atan(k) * 180 / pi  
        x = alpha + 90  # искомый угол перпендикулярен радиусу  
        return x
