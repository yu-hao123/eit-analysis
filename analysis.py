import sys
import numpy as np

from PySide6.QtWidgets import (
    QApplication, QWidget, QVBoxLayout, QPushButton
)

import pyqtgraph as pg
from img import Img

class ImpedanceViewer(QWidget):
    def __init__(self):
        super().__init__()

if __name__ == "__main__":
    app = QApplication(sys.argv)
    viewer = ImpedanceViewer()
    viewer.show()
    sys.exit(app.exec())