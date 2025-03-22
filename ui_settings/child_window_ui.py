import os

from torch import nn
from PyQt6 import QtWidgets, QtCore, QtGui, uic

from PyQt6.QtCore import QThread
from PyQt6.QtCore import QObject
from PyQt6.QtCore import pyqtSlot as Slot
from PyQt6.QtCore import pyqtSignal as Signal

from dependensies.parametrs import PATH_TO_UI_CHILD, PATH_TO_UI_BAR
from nn.neural_network import predict



class ChildWindow(QtWidgets.QWidget):
    def __init__(self):
        super().__init__()
        # Импортируем ui
        uic.loadUi(PATH_TO_UI_CHILD, self)  # Или преобразуем ui в py с помощью pyuic6
        self.setFixedSize(QtCore.QSize(800, 500))


class ChildWindow_BAR(QtWidgets.QWidget):
    work_requested = Signal(nn.Module, str)

    def __init__(self, num: int, calc_func):
        super().__init__()
        # Импортируем ui
        uic.loadUi(PATH_TO_UI_BAR, self)  # Или преобразуем ui в py с помощью pyuic6
        self.progress_bar.setValue(0)
        self.progress_bar.setMaximum(num)
        # Results
        self.mw_func = calc_func
        # NN WORKER
        self.worker = NN_Worker()
        self.worker_thread = QThread()
        self.worker.work.connect(self.update_progress)
        self.worker.end.connect(self.complete)

        self.work_requested.connect(self.worker.do_work)
        self.worker.moveToThread(self.worker_thread)
        self.worker_thread.start()

        self.show()
    
    def update_progress(self, val: int) -> None:
        self.progress_bar.setValue(val)

    def complete(self, predict_masks: list) -> None:
        self.mw_func(predict_masks)
        self.progress_bar.setValue(0)
        self.close()
        self.worker_thread.quit()

    def start(self, model: nn.Module, path_x: str) -> None:
        self.work_requested.emit(model, path_x)

    def get_tread_obj(self):
        return self.worker_thread
    
    def interupt(self):
        self.progress_bar.setValue(0)
        self.close()
        self.worker_thread.quit()


class NN_Worker(QObject):
    work = Signal(int)
    end = Signal(list)
    
    @Slot(nn.Module, str)
    def do_work(self, model, path_x):
        predict_masks = list()
        for cnt, img in enumerate(os.listdir(path_x)):
            img = os.path.join(path_x, img)
            predict_masks.append(predict(model, img, _mode=True))
            self.work.emit(cnt)
        self.end.emit(predict_masks)