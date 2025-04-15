import os

from torch import nn
from PIL import ImageQt
from PyQt6 import QtWidgets, QtCore, QtGui, uic

from PyQt6.QtCore import QThread
from PyQt6.QtCore import QObject
from PyQt6.QtCore import pyqtSlot as Slot
from PyQt6.QtCore import pyqtSignal as Signal

from dependensies.parametrs import PATH_TO_UI_CHILD, PATH_TO_UI_BAR
from nn.neural_network import predict



class ChildWindow(QtWidgets.QWidget):
    signalCoords = QtCore.pyqtSignal(tuple)
    """Change grid window"""
    def __init__(self):
        super().__init__()
        # Импортируем ui
        uic.loadUi(PATH_TO_UI_CHILD, self)  # Или преобразуем ui в py с помощью pyuic6
        self.setFixedSize(QtCore.QSize(800, 500))
        self.setWindowIcon(QtGui.QIcon(r"ui_settings\ui\droplet_icon.png"))
        self.graphicsView.setMouseTracking(True)
        # Кнопки
        self.minus_btn.pressed.connect(lambda: self.scale_img(False))
        self.plus_btn.pressed.connect(lambda: self.scale_img(True))

        self.apply.pressed.connect(lambda: self.send())
        # Draw droplet
        self._scene = None
        self._rect = None
        self._line_h = None
        self._line_v = None

        self.start_pos, self.end_pos = None, None
        self._line_length = tuple()
        self._pen = QtGui.QPen()
        self._pen.setWidth(self.width_spin2.value())
        self._pen.setColor(QtGui.QColor("#ec00fe"))

        self._pen_line = QtGui.QPen()
        self._pen_line.setWidth(self.width_spin.value())
        self._pen_line.setColor(QtGui.QColor("#ADFF2F"))
        # Signal result
        self.result = None

    def image_receiver(self, img_path):
        if type(img_path) == str:
            img = QtGui.QPixmap(img_path)
        else:
            img = img_path.convert("RGBA")
            img = ImageQt.toqpixmap(img)
        item = QtWidgets.QGraphicsPixmapItem(img)
        self._line_length = (item.boundingRect().right(), item.boundingRect().bottom())
        self._scene = ModedQGraphicsScene()
        self._scene.signalMousePos.connect(self.draw_drop)
        self._scene.addItem(item)
        self.graphicsView.setScene(self._scene)

    def draw_drop(self, pos, event_type):
        if event_type == 1:
            # Press
            self.start_pos = pos
        if event_type == 2:
            # Move
            self._pen_line.setWidth(self.width_spin.value())
            self.end_pos = pos
            if self._line_h in self._scene.items() and self._line_v in self._scene.items():
                self._scene.removeItem(self._line_h)
                self._scene.removeItem(self._line_v)
            # HORIZONTAL LINE
            self._line_h = QtWidgets.QGraphicsLineItem(0, pos.y(), self._line_length[0], pos.y())
            self._line_h.setPen(self._pen_line)
            self._scene.addItem(self._line_h)
            # VERTICAL LINE
            self._line_v = QtWidgets.QGraphicsLineItem(pos.x(), 0, pos.x(), self._line_length[1])
            self._line_v.setPen(self._pen_line)
            self._scene.addItem(self._line_v)

            self.graphicsView.setScene(self._scene)
        if event_type == 3:
            # Release
            self._pen.setWidth(self.width_spin2.value())
            if self.start_pos and self.end_pos:
                if self._rect:
                    if self._rect in self._scene.items():
                        self._scene.removeItem(self._rect)
                self.result = QtCore.QRectF(self.start_pos, self.end_pos)
                self._rect = QtWidgets.QGraphicsRectItem(QtCore.QRectF(self.start_pos, self.end_pos))
                self._rect.setPen(self._pen)
                self._scene.addItem(self._rect)
                self.graphicsView.setScene(self._scene)
                self.start_pos, self.end_pos = None, None
    
    def scale_img(self, way: bool) -> None:
        """ Изменение размера картинки """
        if way:
            self.graphicsView.scale(1.1, 1.1)
        else:
            self.graphicsView.scale(0.9, 0.9)

    def send(self):
        coords = self.result.getCoords()
        self.signalCoords.emit(coords)
        self.close()
        self._scene.clear()

class ModedQGraphicsScene(QtWidgets.QGraphicsScene):
    signalMousePos = QtCore.pyqtSignal(QtCore.QPointF, int)
    def __init__(self):
        super().__init__()
        self._move_flag = False

    def mouseMoveEvent(self, event):
        self.signalMousePos.emit(event.scenePos(), 2)
        
    def mousePressEvent(self, event):
        if event.buttons() == QtCore.Qt.MouseButton.LeftButton:
            self.signalMousePos.emit(event.scenePos(), 1)
            self._move_flag = True

    def mouseReleaseEvent(self, event):
        if self._move_flag:
            self.signalMousePos.emit(event.scenePos(), 3)
            self._move_flag = False            


class ChildWindow_BAR(QtWidgets.QWidget):
    work_requested = Signal(nn.Module, str)

    def __init__(self, num: int, calc_func):
        super().__init__()
        # Импортируем ui
        uic.loadUi(PATH_TO_UI_BAR, self)  # Или преобразуем ui в py с помощью pyuic6
        self.setWindowIcon(QtGui.QIcon(r"ui_settings\ui\droplet_icon.png"))
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
        self.worker_thread.terminate()


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