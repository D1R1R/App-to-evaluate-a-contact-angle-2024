from PyQt6.QtGui import QMovie
from PyQt6.QtWidgets import QMessageBox, QSplashScreen

from dependensies.parametrs import PATH_TO_GIF


def RaiseSettingNotSavedMessage(parent) -> bool:
    """Вызывает окно с сообщением"""
    window = QMessageBox(parent)
    window.setWindowTitle("Предупреждение")
    window.setIcon(QMessageBox.Icon.Warning)
    window.setText("Вы не сохранили изменения в настройках. Вернуться к настройкам?")
    buttons = QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.Cancel
    window.setStandardButtons(buttons)

    button = window.exec()
    if button != QMessageBox.StandardButton.Yes:
        return False
    return True

def RaiseTreadInteruptionMessage(parent, text) -> bool:
    """Вызывает окно с сообщением"""
    window = QMessageBox(parent)
    window.setWindowTitle("Предупреждение")
    window.setIcon(QMessageBox.Icon.Warning)
    window.setText(f"Процесс обработки уже запущен. {text}. Прервать обработку изображений?")
    buttons = QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No
    window.setStandardButtons(buttons)

    button = window.exec()
    if button != QMessageBox.StandardButton.Yes:
        return False
    return True


def RaiseNotUploadedError(parent) -> bool:
    """Вызывает окно с ошибкой"""
    window = QMessageBox(parent)
    window.setWindowTitle("Ошибка")
    window.setIcon(QMessageBox.Icon.Critical)
    window.setText("Вы ничего не импортировали.")
    buttons = QMessageBox.StandardButton.Ok
    window.setStandardButtons(buttons)

    button = window.exec()


class LoaderSplashScreen(QSplashScreen):
    def __init__(self, *args, **kwargs):
        super(LoaderSplashScreen, self).__init__(*args, **kwargs)
        self.movie = QMovie(PATH_TO_GIF)
        self.movie.frameChanged.connect(self.onFrameChanged)
        self.movie.start()

    def onFrameChanged(self, _):
        self.setPixmap(self.movie.currentPixmap())

    def finish(self, widget):
        self.movie.stop()
        super(LoaderSplashScreen, self).finish(widget)