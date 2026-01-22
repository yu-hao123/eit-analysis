import sys
import numpy as np

from PySide6.QtWidgets import (
    QApplication, QWidget, QVBoxLayout, QPushButton, QFileDialog, QMessageBox
)

import pyqtgraph as pg
from img import Img

class ImpedanceViewer(QWidget):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Impedance Viewer")
        self.resize(1280, 720)

        main_layout = QVBoxLayout(self)

        # open file
        self.open_button = QPushButton("Open IMG File")
        self.open_button.clicked.connect(self.open_file)
        main_layout.addWidget(self.open_button)

        # ventilation map image view
        self.zmap_view = pg.ImageView(self)
        main_layout.addWidget(self.zmap_view, 5)

        # plethysmograph
        self.plethys_plot = pg.PlotWidget(self)
        self.plethys_curve = (self.plethys_plot).plot()
        main_layout.addWidget(self.plethys_plot, 3)

        # internal data
        self.zs = []
        self.ps = []
        self.pressure = []
        self.flow = []
        self.volume = []

    def open_file(self):
        filename, ok = QFileDialog.getOpenFileName(
            self, "Open File", "${HOME}", "IMG Files (*.img);; All Files (*)"
        )
        print(filename, ok)
        if (ok != "IMG Files (*.img)"):
            QMessageBox.warning(self, "Error", "Did not select a IMG file (.img), please retry!")
            return
        self.load_file(filename)

    def load_file(self, filename):
        # load file impedance frames, plethysmograph, pressure, flow, volume waveforms
        # into memory and display it

        with Img(filename) as img:
            for frame in img:
                self.zs.append(np.asarray(frame.impedance))
                self.ps.append(np.asarray(frame.plethysmograph))

        if not self.zs:
            QMessageBox.warning(self, "Error", "Could not load impedance frames (empty)")
            return

        self.plethys_curve.setData(self.ps)
        print(filename)

if __name__ == "__main__":
    app = QApplication(sys.argv)
    viewer = ImpedanceViewer()
    viewer.show()
    sys.exit(app.exec())