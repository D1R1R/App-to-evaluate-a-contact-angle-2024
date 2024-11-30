import sys
from PyQt6 import QtWidgets

from window_ui import MainWindow
from math_alg import EvaluatingAlg

if __name__ == "__main__":
    # Передаём sys.argv, чтобы разрешить аргументы командной строки для приложения.
    app = QtWidgets.QApplication(sys.argv)

    window = MainWindow()
    window.show()
    app.setStyle('Fusion')
    sys.exit(app.exec())  # app.exec() ???
