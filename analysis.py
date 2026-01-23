import sys
import numpy as np

from PySide6.QtWidgets import (
    QApplication,
    QPushButton,
    QFileDialog,
    QMessageBox,
    QSplitter,
    QVBoxLayout,
    QWidget,
)
from PySide6.QtCore import Qt

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

        self.plethys_plot = pg.PlotWidget(self)
        self.plethys_plot.showGrid(x=True, y=True)
        self.plethys_curve = (self.plethys_plot).plot()
        main_layout.addWidget(self.plethys_plot, 3)

        # ins/exp markers
        self.ins_scatter = pg.ScatterPlotItem(
            pen=None,
            brush='g',
            size=8,
            symbol='t'
        )
        self.exp_scatter = pg.ScatterPlotItem(
            pen=None,
            brush='r',
            size=8,
            symbol='t1'
        )
        self.plethys_plot.addItem(self.ins_scatter)
        self.plethys_plot.addItem(self.exp_scatter)

        # linear region for deltaZ computation
        self.region = pg.LinearRegionItem()
        self.region.setRegion((0, 2400))
        self.plethys_plot.addItem(self.region)
        ## need to connect moved to compute dz
        self.region.sigRegionChanged.connect(self.update_zmap)

        # internal data
        self.zs = []
        self.ps = []
        self.pressure = []
        self.flow = []
        self.volume = []
        self.inspiration = []
        self.expiration = []

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
        # load impedance frames, plethysmograph, pressure, flow, volume waveforms
        # into memory and display it

        with Img(filename) as img:
            for frame in img:
                self.zs.append(np.asarray(frame.impedance))
                self.ps.append(np.asarray(frame.plethysmograph))
                self.inspiration.append(np.asarray(frame.inspiration))
                self.expiration.append(np.asarray(frame.expiration))

        if not self.zs:
            QMessageBox.warning(self, "Error", "Could not load impedance frames (empty)")
            return

        self.plethys_curve.setData(self.ps)

        x_ins = [i for i, v in enumerate(self.inspiration) if v]
        y_ins = [self.ps[i] for i in x_ins]

        x_exp = [i for i, v in enumerate(self.expiration) if v]
        y_exp = [self.ps[i] for i in x_exp]

        self.ins_scatter.setData(x_ins, y_ins)
        self.exp_scatter.setData(x_exp, y_exp)

        self.update_zmap()
        print(filename)

    def update_zmap(self):
        start, finish = self.region.getRegion()
        if finish <= start:
            aux = start
            start = finish
            finish = aux
        # check bounds if region is within file
        # an interesting idea would be to have a warning indicator at bottom
        start = max(0, int(start))
        finish = min(len(self.zs) - 1, int(finish))

        ins_frames = []
        exp_frames = []

        for i in range(start, finish):
            if self.inspiration[i]:
                ins_frames.append(self.zs[i])
            if self.expiration[i]:
                exp_frames.append(self.zs[i])

        if not ins_frames or not exp_frames:
            return # could not compute deltaZ

        ins_stack = np.stack(ins_frames)
        exp_stack = np.stack(exp_frames)

        ins_mean = np.ma.masked_where(ins_stack < -999, ins_stack).mean(axis=0)
        exp_mean = np.ma.masked_where(exp_stack < -999, exp_stack).mean(axis=0)

        zmap = exp_mean - ins_mean
        zmap = zmap.reshape(32, 32)

        zmap = np.rot90(zmap)

        # color scale should use valid pixels only
        self.zmap_view.setImage(
            zmap,
            autoLevels=False,
            levels=(zmap.min(), zmap.max()),
            autoRange=False
        )


if __name__ == "__main__":
    app = QApplication(sys.argv)
    viewer = ImpedanceViewer()
    viewer.show()
    sys.exit(app.exec())