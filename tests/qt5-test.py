import os, sys, yaml
import numpy as np

from PyQt5.QtCore import QSize, Qt
from PyQt5.QtWidgets import (
    QApplication,
    QPushButton,
    QWidget,
    QTabWidget,
    QFormLayout,
    QHBoxLayout,
    QVBoxLayout,
    QSpinBox,
    QDoubleSpinBox,
    QLineEdit,
    QLCDNumber,
    QLabel
)

import pyqtgraph as pg

parentdir = os.path.dirname(os.path.dirname(os.path.realpath(__file__)))
sys.path.append(parentdir)

import src.helpers as helper

test_data = np.genfromtxt("./results/2022-02-09_15-50-08bruker-time-constant_to599mT.csv", delimiter=",",skip_header=1, names=True)

# Subclass QMainWindow to customize your application's main window
class MainWindow(QWidget):
    def __init__(self):
        super().__init__()
        if os.name == 'posix':
            self.default_conf = helper.loadYAMLConfig("../config/measurement.yaml")
        else:
            self.default_conf = helper.loadYAMLConfig("config/measurement.yaml")
        self.setWindowTitle("Bruker Measurement")
        self.setGeometry(100, 100, 900, 400)

        self.conf = {}

        outer_layout = QHBoxLayout()
        left_col = QVBoxLayout()
        left_col.setSpacing(10)
        conf_button_layout = QHBoxLayout()
        status_layout = QHBoxLayout()
        plot_layout = pg.PlotWidget()

        self.setLayout(outer_layout)

        self.configure_plot(plot_layout)
        self.plot_data(plot_layout)

        conf_layout = QTabWidget()
        
        self.make_config_tabs(conf_layout)
        self.make_config_buttons(conf_button_layout)

        status_layout.addStretch(2)
        status_layout.addWidget(QLabel("Current B-Field (mT)"))
        self.LCD(status_layout)

        left_col.addLayout(conf_button_layout)
        left_col.addWidget(conf_layout)
        left_col.addLayout(status_layout)

        self.make_start_button(left_col)        
        outer_layout.addLayout(left_col,1)
        outer_layout.addWidget(plot_layout,3)


    def LCD(self, layout):
        tmp = QLCDNumber()
        layout.addWidget(tmp)
        return tmp


    def configure_plot(self, plt_widget):
        plt_widget.setBackground('w')


    def plot_data(self, plt_widget):
        pen = pg.mkPen(color=(0,105,80))
        plt_widget.plot(test_data["setval"], test_data["reachedat"], pen=pen)


    def make_start_button(self, start_widget):
        start_button = QPushButton("Start Measurement")
        start_button.setStyleSheet("font: bold 20px")
        start_widget.addWidget(start_button)
        

    def make_config_tabs(self, conf_widget):
        conf_widget.addTab(self.measurement_conf(), "Measurement")
        conf_widget.addTab(self.wave_conf(), "Wave")
        conf_widget.addTab(self.data_conf(), "Data")


    def make_config_buttons(self, button_layout):
        save_conf_button = QPushButton("Save Configuration")
        load_conf_button = QPushButton("Load Configuration")

        button_layout.addWidget(save_conf_button)
        button_layout.addWidget(load_conf_button)



    def wave_conf(self):
        tab = QWidget()
        t_l = QFormLayout()
        w = self.default_conf["wave"]

        self.wave = {
            "Form": QLineEdit(),
            "Zero": QDoubleSpinBox(),
            "Amplitude": QSpinBox(),
            "N": QSpinBox()
        }
        self.wave["Form"].setText(w["form"])
        self.wave["Zero"].setValue(w["zero"])
        self.wave["Zero"].setRange(0.0,1.0)
        self.wave["Zero"].setSingleStep(0.1)
        self.wave["Amplitude"].setRange(-10,1200)
        self.wave["Amplitude"].setValue(w["amp"]),
        self.wave["N"].setRange(10,100000)
        self.wave["N"].setValue(w["N"])


        for k, v in self.wave.items():
            t_l.addRow(k, v)
            
        tab.setLayout(t_l)
        return tab

    def measurement_conf(self):
        tab = QWidget()
        t_l = QFormLayout()
        self.meas = {}

        for k, v in self.default_conf["settings"].items():
            self.meas[k] = QDoubleSpinBox()
            self.meas[k].setValue(v)
            t_l.addRow(k, self.meas[k])


        tab.setLayout(t_l)
        return tab

    def data_conf(self):
        tab = QWidget()
        t_l = QFormLayout()
        self.data = {"Sample": QLineEdit(), "Path": QLineEdit()}
        
        for k, v in self.data.items():
            t_l.addRow(k, v)
            
        tab.setLayout(t_l)
        return tab
        



def main():
    app = QApplication(sys.argv)

    window = MainWindow()

    window.show()

    app.exec()

if __name__ == "__main__":
    main()
