import os
from PyQt6 import QtWidgets, QtCore, uic
from parametrs import *


class MainWindow(QtWidgets.QMainWindow):
    def __init__(self, *args, **kwargs) -> None:
        super().__init__(*args, **kwargs)
        # Импортируем ui
        uic.loadUi(PATH_TO_UI, self)  # Или преобразуем ui в py с помощью pyuic6

        # ПАРАМЕТРЫ
        self.uploaded_state = None
        self.import_way = None

        self.show_angel = True
        self.show_data = True
        self.show_square = True
        self.show_circle = True
        self.beam_length = 20
        self.beam_width = 2

        self.text_file = False
        self.export_type = None  # TODO
        home_dir = os.path.expanduser('~')  # ??? работает только на Windows
        self.export_way = os.path.join(home_dir, "Downloads")

        # QBUTTON
        for button in self.centralwidget.findChildren(QtWidgets.QAbstractButton):  # Всем кнопкам в поле centralwidget устанавливаем NoFocus
            button.setFocusPolicy(QtCore.Qt.FocusPolicy.NoFocus)
        # 1. Переключение настройки/история
        self.history_button.pressed.connect(lambda: self.open_frame(True))  # Без lambda передается None
        self.settings_button.pressed.connect(lambda: self.open_frame(False))
        self.history_button.setFocusPolicy(QtCore.Qt.FocusPolicy.ClickFocus)
        self.settings_button.setFocusPolicy(QtCore.Qt.FocusPolicy.ClickFocus)
        self.settings_button.setFocus()
        # 2. Расширенные настройки
        self.folder_btn.pressed.connect(lambda: self.open_folder())
        self.apply_btn.pressed.connect(lambda: self.apply_settings())
        # 2.1 Отображение текущей папки QLABEL
        self.current_folder_lb.setText(f'Текущее место сохранения: {self.export_way}')
        # 3. История решений
        self.download_solution_btn.pressed.connect(lambda: self.download_solution())
        # 4. Работа с изображением
        self.upload_file_btn.pressed.connect(lambda: self.upload_file())
        self.upload_folder_btn.pressed.connect(lambda: self.upload_folder())
        self.change_grid_btn.pressed.connect(lambda: self.change_grid())
        self.process_btn.pressed.connect(lambda: self.process())
    
    def open_frame(self, f: bool) -> None:
        if f:
            self.Settings_frame.setMaximumSize(0, 16777215)
            self.History_frame.setMaximumSize(16777215, 16777215)
        else:
            self.Settings_frame.setMaximumSize(16777215, 16777215)
            self.History_frame.setMaximumSize(0, 16777215)

    def open_folder(self) -> None:
        self.export_way = QtWidgets.QFileDialog.getExistingDirectory(self, "Выберите папку")
        self.current_folder_lb.setText(f'Текущее место сохранения: {self.export_way}')

    def apply_settings(self) -> None:
        pass

    def download_solution(self) -> None:
        pass
        
    def upload_file(self) -> None:
        self.uploaded_state = True
        file_name, _ = QtWidgets.QFileDialog.getOpenFileName(
            self,
            "Выберите файл", 
            self.export_way, 
            "Images (*.png *.jpg *.jpeg *.bmp *.tiff)"
        )
        self.import_way = file_name

    def upload_folder(self) -> None:
        self.uploaded_state = False
        self.import_way = QtWidgets.QFileDialog.getExistingDirectory(self, "Выберите папку")

    def change_grid(self) -> None:
        # TODO
        if self.uploaded_state == None:
            # Вывать ошибку, тк ничего не загружено
            pass

    def process(self) -> None:
        if self.uploaded_state == None:
            # Вывать ошибку, тк ничего не загружено
            pass

        if self.uploaded_state:
            # Файл
            pass
        else:
            # Папка
            pass
