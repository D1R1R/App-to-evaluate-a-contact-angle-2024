import sys, time
from PyQt6.QtWidgets import QApplication

from ui_settings.window_ui import MainWindow
from ui_settings.dialogs import LoaderSplashScreen

if __name__ == "__main__":

    # Передаём sys.argv, чтобы разрешить аргументы командной строки для приложения.
    app = QApplication(sys.argv)
    # Экран загрузки
    splash = LoaderSplashScreen()
    splash.show()
    # Минимум один оборот заставки
    start = time.time()
    while time.time() < start + 8:
        app.processEvents()
    
    window = MainWindow()
    window.show()
    splash.finish(window)
    app.setStyle('Fusion')

    sys.exit(app.exec())
