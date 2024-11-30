import os
from PyQt6 import QtWidgets, QtCore, QtGui, uic
import pandas as pd
from parametrs import *


class MainWindow(QtWidgets.QMainWindow):
    def __init__(self, *args, **kwargs) -> None:
        super().__init__(*args, **kwargs)
        # Импортируем ui
        uic.loadUi(PATH_TO_UI, self)  # Или преобразуем ui в py с помощью pyuic6
        # ПАРАМЕТРЫ
        self.uploaded_state = None  # True - ; False - ; None -
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

        self._table_model = None
        self.table = None

        # QBUTTON
        for button in self.centralwidget.findChildren(QtWidgets.QAbstractButton):  # Всем кнопкам в поле centralwidget устанавливаем NoFocus
            button.setFocusPolicy(QtCore.Qt.FocusPolicy.NoFocus)
        # 1. Переключение настройки/история
        self.history_button.pressed.connect(lambda: self.open_frame(True))  # Без lambda передается None
        self.settings_button.pressed.connect(lambda: self.open_frame(False))
        self.history_button.setFocusPolicy(QtCore.Qt.FocusPolicy.ClickFocus)
        self.settings_button.setFocusPolicy(QtCore.Qt.FocusPolicy.ClickFocus)
        self.history_button.setFocus()
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
        self.minus_btn.pressed.connect(lambda: self.scale_img(False))
        self.plus_btn.pressed.connect(lambda: self.scale_img(True))
    
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
        self.display_img(self.import_way)
        self.display_table()

    def upload_folder(self) -> None:
        self.uploaded_state = False
        self.import_way = QtWidgets.QFileDialog.getExistingDirectory(self, "Выберите папку")
        self.display_table()

    def change_grid(self) -> None:
        # TODO (Влад)
        if self.uploaded_state == None:
            # Вывать ошибку, тк ничего не загружено
            pass

    def display_img(self, img_path: str) -> None:
        # Отображение картинки
        img = QtGui.QPixmap(img_path)  # .scaled(*IMAGE_SIZE)  Портит качество изображения
        item = QtWidgets.QGraphicsPixmapItem(img)
        scene = QtWidgets.QGraphicsScene()
        scene.addItem(item)
        self.graphicview.setScene(scene)

    def display_table(self) -> None:
        # Отображение таблицы
        table_data = list()
        if self.uploaded_state:
            file_name = os.path.basename(self.import_way)
            file_size = round((os.path.getsize(self.import_way) / 8 / 1024), 1)
            file_extension = file_name.split(".")[-1].upper()
            table_data.append([file_name, file_size, file_extension,])
        else:
            for single_file in os.listdir(self.import_way):
                file_name = os.path.basename(os.path.join(self.import_way, single_file))
                file_size = round((os.path.getsize(self.import_way) / 8 / 1024), 1)
                file_extension = file_name.split(".")[-1].upper()
                if file_extension in ALLOWED_FILE_FROMAT:
                    table_data.append([file_name, file_size, file_extension,])
        self.table = pd.DataFrame(table_data, columns=TABLE_HEAD)
        self.table_model = TabelModel(self.table)
        self.tableview.setModel(self.table_model)
        # Растягиваем таблицу по размеру окна
        self.tableview.horizontalHeader().setSectionResizeMode(QtWidgets.QHeaderView.ResizeMode.Stretch)
        self.tableview.horizontalHeader().setSectionResizeMode(1, QtWidgets.QHeaderView.ResizeMode.ResizeToContents)
        self.tableview.horizontalHeader().setSectionResizeMode(2, QtWidgets.QHeaderView.ResizeMode.ResizeToContents)
        self.tableview.setSelectionBehavior(QtWidgets.QAbstractItemView.SelectionBehavior.SelectRows)
        # Отслеживаем клики по таблице
        follow = self.tableview.selectionModel()
        follow.currentRowChanged.connect(self.highlighted_img)

    def highlighted_img(self, idx: QtCore.QModelIndex) -> None:
        # self.uploaded_state заведомо != None
        if not self.uploaded_state:
            img_name = self.table.iloc[idx.row(), 0]
            path = os.path.join(self.import_way, img_name)
            self.display_img(path)

    def scale_img(self, way: bool) -> None:
        # Изменяем размер картинки
        if self.uploaded_state != None:
            if way:
                self.graphicview.scale(1.1, 1.1)
            else:
                self.graphicview.scale(0.9, 0.9)

    def process(self) -> None:
        # TODO
        if self.uploaded_state is None:
            # Вывать ошибку, тк ничего не загружено
            pass

        if self.uploaded_state:
            # Файл
            pass
        else:
            # Папка
            pass



class TabelModel(QtCore.QAbstractTableModel):
    """
    «Модель — представление — контроллер» (MVC).
    В PyQt таблицы и модели обычно реализуются с использованием архитектуры MVC.
    Можно сказать, что модель представляет данные, представление отображает данные,
    а контроллер управляет взаимодействием между моделью и представлением.
    """
    def __init__(self, table: pd.DataFrame):
        super().__init__()
        self._table = table

    def data(self, idx: QtCore.QModelIndex, role) -> str:  # type(idx) ??
        # Возвращает данные, которые будут отображаться по указанному индексу
        if role == QtCore.Qt.ItemDataRole.DisplayRole:  # DisplayRole - ключевые данные, которые будут отображаться в виде текста.
            cell_value = self._table.iloc[idx.row(), idx.column()]
            return str(cell_value)

    def rowCount(self, idx: QtCore.QModelIndex) -> int:
        # Возвращает количество строк в таблице
        return self._table.shape[0]

    def columnCount(self, idx: QtCore.QModelIndex) -> int:
        # Возвращает количество столбцов в таблице
        return self._table.shape[1]

    def headerData(self, idx: int, orientation, role) -> str:
        # Возвращает заголовки для строк и столбцов
        if role == QtCore.Qt.ItemDataRole.DisplayRole:
            if orientation == QtCore.Qt.Orientation.Horizontal:
                return str(self._table.columns[idx])
            if orientation == QtCore.Qt.Orientation.Vertical:
                return str(self._table.index[idx])
