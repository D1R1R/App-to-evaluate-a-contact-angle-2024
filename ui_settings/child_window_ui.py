from PyQt6 import QtWidgets, QtCore, QtGui, uic

from dependensies.parametrs import PATH_TO_UI_CHILD, PATH_TO_UI_BAR



class ChildWindow(QtWidgets.QWidget):
    def __init__(self):
        super().__init__()
        # Импортируем ui
        uic.loadUi(PATH_TO_UI_CHILD, self)  # Или преобразуем ui в py с помощью pyuic6
        self.setFixedSize(QtCore.QSize(800, 500))

class ChildWindow_BAR(QtWidgets.QWidget):
    def __init__(self):
        super().__init__()
        # Импортируем ui
        uic.loadUi(PATH_TO_UI_BAR, self)  # Или преобразуем ui в py с помощью pyuic6