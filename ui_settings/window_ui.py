import os
from torch import nn

from PyQt6 import QtCore, QtGui, QtWidgets
from PyQt6 import uic

from PIL import ImageQt
import pandas as pd

from ui_settings.dialogs import *
from ui_settings.child_window_ui import ChildWindow
from ui_settings.calculation import EvaluatingAlg
from dependensies.parametrs import *
from nn.neural_network import initialize_nn, predict
from ui_settings.child_window_ui import ChildWindow_BAR


class MainWindow(QtWidgets.QMainWindow):
    def __init__(self, *args, **kwargs) -> None:
        super().__init__(*args, **kwargs)
        # Импортируем ui
        uic.loadUi(PATH_TO_UI, self)  # Или преобразуем ui в py с помощью pyuic6
        self.setWindowIcon(QtGui.QIcon(r"ui_settings\ui\droplet_icon.png"))
        # ПАРАМЕТРЫ
        self.uploaded_state = None  # True - файл; False - папка; None - ничего
        self.import_way = None

        self.show_angel = True
        self.show_data = True
        self.show_square = True
        self.show_circle = True
        self.angel_type = "Градусы °"
        self.beam_length = 20
        self.lines_width = 2

        self.text_file = False
        self.export_type = None
        home_dir = os.path.expanduser('~')  # ??? работает только на Windows
        self.export_way = os.path.join(home_dir, "Downloads")

        self._table_model = None
        self.table = None
        self._original_table = None
        self.flag_settings_changes = False

        # CHANGE GRID WINDOW
        self._chg_window = ChildWindow()
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
        self.apply_btn.pressed.connect(lambda: self.apply_settings())  # QCOMDOBOX; QSPINBOX; QCHECKBOX     
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
        # 5. Qtable
        self._follow = None
        # Нейронная сеть
        self._nn = initialize_nn()
        # TREAD
        self._tread = None
    
    def open_frame(self, f: bool) -> None:
        if f:
            answer = False
            if self.flag_settings_changes:
                # Предупредить пользователя что изменения не сохранены
                answer = RaiseSettingNotSavedMessage(self)
            if not answer:
                self.Settings_frame.setMaximumSize(0, 16777215)
                self.History_frame.setMaximumSize(16777215, 16777215)
            else:
                self.settings_button.setFocus()
        else:
            self.flag_settings_changes = True
            self.Settings_frame.setMaximumSize(16777215, 16777215)
            self.History_frame.setMaximumSize(0, 16777215)

    def open_folder(self) -> None:
        self.export_way = QtWidgets.QFileDialog.getExistingDirectory(self, "Выберите папку")
        self.current_folder_lb.setText(f'Текущее место сохранения: {self.export_way}')

    def apply_settings(self) -> None:
        # TODO: ENABLED\DISABLED
        if self._tread != None:
            if self._tread.isRunning():
                # Вывать предупреждение, тк поток не закончен
                answer = RaiseTreadInteruptionMessage(self, "Выбранны еизменения не повлияют на результат")
                if not answer:
                    return
                self.bar.interupt()
                self._tread = None
        # QCHECKBOX
        if self.datashow_cb.isChecked():
            self.show_data = True
        else:
            self.show_data = False

        if self.sqareshow_cb.isChecked():
            self.show_square = True
        else:
            self.show_square = False
            
        if self.angelshow_cb.isChecked():
            self.show_angel = True
        else:
            self.show_angel = False

        if self.circleshow_cb.isChecked():
            self.show_circle = True
        else:
            self.show_circle = False

        if self.istextfile_cb.isChecked():
            self.text_file = True
        else:
            self.text_file = False
        # QSPINBOX
        self.beam_length = self.beamlength_sb.value()
        self.lines_width = self.lineswidth.value()
        self.flag_settings_changes = False
        # QCOMBOBOX
        self.angel_type = self.comboBox.currentText().strip()
        self.export_type = self.comboBox2.currentText().strip()

    def download_solution(self) -> None:
        # TODO
        if self.uploaded_state == None:
            # Вызвать ошибку, тк ничего не загружено
            RaiseNotUploadedError(self)
            return
        if self._tread != None:
            if self._tread.isRunning():
                # Вывать предупреждение, тк поток не закончен
                answer = RaiseTreadInteruptionMessage(self, "Загрузка результатов станет доступна после завершения потока")
                if not answer:
                    return
                self.bar.interupt()
                self._tread = None
        
        if self.uploaded_state:
            if self.export_type in {
                "Архив *.tar (Если загружена папка)",
                "JSON *.json (Если загружена папка)",
                 "Таблица *.xlsx, *.xls (Если загружена папка)"
                }:
                # Вызвать ошибку тк вид экспорта не соответствует виду импорта
                return
            if self.export_type == "PNG *.png (Если загружен файл)":
                pass
            elif self.export_type == "JPEG *.jpeg (Если загружен файл)":
                pass
            else:
                pass
        else:
            pass
        
    def upload_file(self) -> None:
        # NOTE: При загрузке одного файла отдельный поток не создается
        if self._tread != None:
            if self._tread.isRunning():
                # Вывать предупреждение, тк поток не закончен
                answer = RaiseTreadInteruptionMessage(self, "Загрузив файл вы прервете поток")
                if not answer:
                    return
                self.bar.interupt()
                self._tread = None

        self.uploaded_state = True
        file_name, _ = QtWidgets.QFileDialog.getOpenFileName(
            self,
            "Выберите файл", 
            self.export_way, 
            "Images (*.png *.jpg *.jpeg *.bmp *.tiff)"
        )
        self.import_way = file_name
        self.historyview.setModel(None)  # Очищаем таблицу
        self.display_img(self.import_way)
        self.display_table()

    def upload_folder(self) -> None:
        if self._tread != None:
            if self._tread.isRunning():
                # Вывать предупреждение, тк поток не закончен
                answer = RaiseTreadInteruptionMessage(self, "Загрузив папку вы прервете поток")
                if not answer:
                    return
                self.bar.interupt()
                self._tread = None

        self.uploaded_state = False
        self.import_way = QtWidgets.QFileDialog.getExistingDirectory(self, "Выберите папку")
        self.historyview.setModel(None)  # Очищаем таблицу
        self.display_table()

    def change_grid(self) -> None:
        # TODO
        if self.uploaded_state == None:
            # Вызвать ошибку, тк ничего не загружено
            RaiseNotUploadedError(self)
            return
        if self._tread != None:
            if self._tread.isRunning():
                # Вывать предупреждение, тк поток не закончен
                answer = RaiseTreadInteruptionMessage(self, "Данная опция станет доступна после завершения потока")
                if not answer:
                    return
                self.bar.interupt()
                self._tread = None
        
        self._chg_window.show()
        
        if self.uploaded_state:
            self._chg_window.image_receiver(self.import_way)
        else:
            idx = self._follow.currentIndex()
            img_name = self.table.iloc[idx.row(), 0]
            if type(img_name) == str:
                img_path = os.path.join(self.import_way, img_name)
            else:
                img_path = img_name
            self._chg_window.image_receiver(img_path)
    
    def display_img(self, img_path: str) -> None:
        """ Отображение картинки в окне"""
        if type(img_path) == str:
            img = QtGui.QPixmap(img_path)  # .scaled(*IMAGE_SIZE)  Портит качество изображения
        else:
            img = img_path.convert("RGBA")  # Без
            img = ImageQt.toqpixmap(img)
        item = QtWidgets.QGraphicsPixmapItem(img)
        scene = QtWidgets.QGraphicsScene()
        scene.addItem(item)
        self.graphicview.setScene(scene)

    def display_table(self) -> None:
        """ Отображение таблицы """
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
        self._original_table = self.table.copy()
        self._table_model = TabelModel(self.table)
        self.tableview.setModel(self._table_model)
        # Растягиваем таблицу по размеру окна
        self.tableview.horizontalHeader().setSectionResizeMode(QtWidgets.QHeaderView.ResizeMode.Stretch)
        self.tableview.horizontalHeader().setSectionResizeMode(1, QtWidgets.QHeaderView.ResizeMode.ResizeToContents)
        self.tableview.horizontalHeader().setSectionResizeMode(2, QtWidgets.QHeaderView.ResizeMode.ResizeToContents)
        self.tableview.setSelectionBehavior(QtWidgets.QAbstractItemView.SelectionBehavior.SelectRows)
        # Отслеживаем клики по таблице
        self._follow = self.tableview.selectionModel()
        self._follow.currentRowChanged.connect(self.highlighted_img)

    def highlighted_img(self, idx: QtCore.QModelIndex) -> None:
        """ Вспомогательная функция к таблице. Отображает выбранное изоюражение."""
        # self.uploaded_state заведомо != None
        if not self.uploaded_state:
            img_name = self.table.iloc[idx.row(), 0]
            if type(img_name) == str:
                path = os.path.join(self.import_way, img_name)
            else:
                path = img_name
            self.display_img(path)

    def scale_img(self, way: bool) -> None:
        """ Изменение размера картинки """
        if self.uploaded_state != None:
            if way:
                self.graphicview.scale(1.1, 1.1)
            else:
                self.graphicview.scale(0.9, 0.9)

    def process(self) -> None:
        """ Обработка изображений нейронной сетью. """
        if self.uploaded_state is None:
            # Вывать ошибку, тк ничего не загружено
            RaiseNotUploadedError(self)
            return
        if self._tread != None:
            if self._tread.isRunning():
                # Вывать предупреждение, тк поток не закончен
                answer = RaiseTreadInteruptionMessage(self, "Начав обработку заново вы прервете существующий поток")
                if not answer:
                    return
                self.bar.interupt()
                self._tread = None
        
        # NN
        if not self.uploaded_state:
            # IN NEW THREAD
            self.bar = ChildWindow_BAR(len(os.listdir(self.import_way)), self.calculate_angle)
            self.bar.work_requested.emit(self._nn, self.import_way)
            self._tread = self.bar.get_tread_obj()
        else:
            # WITHOUT NEW THREAD
            pred_img_mask = predict(self._nn, self.import_way, self.uploaded_state)
            self.calculate_angle(pred_img_mask)
    
    def calculate_angle(self, pred_img_mask: list) -> None:
        """ Вычисление угла. Разметка изображений. Обновление таблицы."""
        if self.uploaded_state:
            # Файл
            algorithm = EvaluatingAlg(self.import_way, self.lines_width, self.beam_length, self.angel_type, True)
        else:
            # Папка
            algorithm = EvaluatingAlg(self.import_way, self.lines_width, self.beam_length, self.angel_type, False)
        
        position = algorithm.find_rect(pred_img_mask)
        permissions = [self.show_square, self.show_circle, self.show_angel, self.show_data]
        
        solution = list()
        grided_imgs = dict()
        for path, rect in position:
            file_name = os.path.basename(path)
            angel, center, k, r = algorithm.calc(rect)
            img = algorithm.draw(path, permissions, k, rect, r, center, angel)
            solution.append((file_name, angel))
            grided_imgs[file_name] = img
        # Таблица
        table = pd.DataFrame(solution, columns=["Имя файла", f"Угол ({self.angel_type.lower()})"])
        table_model = TabelModel(table)
        self.historyview.setModel(table_model)
        # Растягиваем таблицу по размеру окна
        self.historyview.horizontalHeader().setSectionResizeMode(QtWidgets.QHeaderView.ResizeMode.Stretch)
        self.historyview.horizontalHeader().setSectionResizeMode(1, QtWidgets.QHeaderView.ResizeMode.ResizeToContents)
        self.historyview.setSelectionMode(QtWidgets.QAbstractItemView.SelectionMode.NoSelection)
        self.temp_replace(grided_imgs)
        self.highlighted_img(self.tableview.currentIndex())
        if self.uploaded_state:
            idx = self.tableview.currentIndex()  # Только один объект всегда
            img_name = self.table.iloc[idx.row(), 0]
            self.display_img(img_name)

    def temp_replace(self, new_names: dict):
        """ Вспомогательная функция таблицы. Для обработанных изображений. """
        new_table_data = list()
        for _, row in self._original_table.iterrows():
            file_name, file_size, file_extension = row.tolist()
            if type(file_name) == str:
                new_table_data.append([new_names[file_name], file_size, file_extension])           
        new_table = pd.DataFrame(new_table_data, columns=TABLE_HEAD)
        self.table = new_table
        # self._table_model.replace(new_table)
        # self.tableview.setModel(self._table_model)



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

    def data(self, idx: QtCore.QModelIndex, role: QtCore.Qt.ItemDataRole = QtCore.Qt.ItemDataRole.DisplayRole) -> str:  # type(idx) ??
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
            
    def replace(self, new_table: pd.DataFrame):
        self._table = new_table
