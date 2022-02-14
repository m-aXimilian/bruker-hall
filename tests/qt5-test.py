import os, sys, yaml
import numpy as np
import logging
import threading
import time

from PyQt5.QtCore import *
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
    QLabel,
    QFileDialog,
    QMainWindow,
)

import pyqtgraph as pg

parentdir = os.path.dirname(os.path.dirname(os.path.realpath(__file__)))
sys.path.append(parentdir)

import src.helpers as helper
import src.HallHandler as hall

test_data = np.genfromtxt("tests/results/2022-02-09_15-50-08bruker-time-constant_to599mT.csv", delimiter=",",skip_header=1, names=True)

name_yaml_lookup = {
    "delta-fine (mT)": "delta-fine",
    "delta-start (mT)": "delta-start",
    "max-inc (mT)": "max-inc",
    "wait-b (s)": "wait-b",
    "timeout (s)": "timeout",
    "bruker-const (s/mT)": "bruker-const",
    "Form (n.v.)": "form",
    "Zero (p.u.)": "zero",
    "Amplitude (mT)": "amp",
    "N (n.v.)": "N",
    "Sample": "sample",
    "Path": "path",
}

yaml_name_lookup = {v: k for k, v in name_yaml_lookup.items()}

# Subclass QMainWindow to customize your application's main window

class MainWindow(QMainWindow):

    def __init__(self, parent=None):

        super(MainWindow, self).__init__(parent)
        self.form_widget = MainWidget(self)
        self.setWindowTitle("Bruker Measurement")
        self.setCentralWidget(self.form_widget)
        self.showMaximized()


class MainWidget(QWidget):
    def __init__(self,parent):
        super().__init__()
        if os.name == 'posix':
            self.default_conf = helper.loadYAMLConfig("../config/measurement.yaml")
        else:
            self.default_conf = helper.loadYAMLConfig("config/measurement.yaml")
        # self.setGeometry(100, 100, 1000, 600)
        self.parent = parent
        self.parent.statusBar().showMessage("init.")

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

        self.conf_layout = QTabWidget()
        
        self.make_config_tabs(self.conf_layout)
        self.make_config_buttons(conf_button_layout)

        status_layout.addStretch(2)
        status_layout.addWidget(QLabel("Current B-Field (mT)"))
        self.LCD(status_layout)

        left_col.addLayout(conf_button_layout)
        left_col.addWidget(self.conf_layout)
        left_col.addLayout(status_layout)

        self.make_start_button(left_col)        
        outer_layout.addLayout(left_col,1)
        outer_layout.addWidget(plot_layout,3)

        self.connect_devices()
        self.show_last_b()


    def connect_devices(self):
        self.m_handler = hall.HallHandler()
        
    
    def show_last_b(self):
        set_b = lambda: self.b_lcd.display(self.m_handler.m_hall.read_field())
        self.last_b_timer = QTimer()
        self.last_b_timer.setInterval(500)
        self.last_b_timer.timeout.connect(set_b)
        self.last_b_timer.start()
        

    def generate_config_dict(self):     
        self.conf = {"wave": self.__dict_convert(self.wave),
                     "settings": self.__dict_convert(self.meas),
                     "data": self.__dict_convert(self.data)
                     }


    def override_default_dict(self, file_name):
        self.default_conf = helper.loadYAMLConfig(file_name)
        

    def __dict_convert(self, orig):
        res = {}
        for k, v in orig.items():
            if isinstance(v, QLineEdit):
                res[k] =  v.text()
            if isinstance(v, (QSpinBox, QDoubleSpinBox)):
                res[k] =  v.value()
        return res


    def LCD(self, layout):
        self.b_lcd = QLCDNumber()
        self.b_lcd.setNumDigits(6)
        self.b_lcd.setStyleSheet("background-color: red")
        layout.addWidget(self.b_lcd)
        return self.b_lcd


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
        conf_widget.clear()
        conf_widget.addTab(self.measurement_conf(), "Measurement")
        conf_widget.addTab(self.wave_conf(), "Wave")
        conf_widget.addTab(self.data_conf(), "Data")


    def make_config_buttons(self, button_layout):
        self.save_conf_button = QPushButton("Save Configuration")
        self.load_conf_button = QPushButton("Load Configuration")

        self.save_conf_button.clicked.connect(self.save_conf_button_handler)
        self.load_conf_button.clicked.connect(self.load_conf_button_handler)
        button_layout.addWidget(self.save_conf_button)
        button_layout.addWidget(self.load_conf_button)


    def save_conf_button_handler(self):
        self.generate_config_dict()
        tmp_p = self.conf["data"]["path"]
        if tmp_p == "":
            tmp_p = "./tmp_conf/test.yaml"
        else:
            tmp_p += "conf/test.yaml"

        self.status_bar_info("wrote config to: %s" % os.path.abspath(tmp_p))
        self.disable_button(self.save_conf_button)

        os.makedirs(os.path.dirname(tmp_p), exist_ok=True)
        with open(tmp_p, 'w') as out:
            yaml.dump(self.conf, out)
            

    def load_conf_button_handler(self):
        f = QFileDialog.getOpenFileName(self, "Select Configuration File", filter="Configuration Files (*.yaml *.yml)")
        
        logging.debug("config file from %s" % f[0])
        self.status_bar_info("load config from: %s" %f[0])

        self.override_default_dict(f[0])
        self.make_config_tabs(self.conf_layout)
        

    def disable_button(self, button):
        button.setEnabled(False)


    def enable_button(self, button):
        button.setEnabled(True)
    
        
    def wave_conf(self):
        tab = QWidget()
        t_l = QFormLayout()
        w = self.default_conf["wave"]

        self.wave = {
            "form": QLineEdit(),
            "zero": QDoubleSpinBox(),
            "amp": QSpinBox(),
            "N": QSpinBox()
        }
        
        self.wave["form"].setText(w["form"])
        self.wave["zero"].setValue(w["zero"])
        self.wave["zero"].setRange(0.0,1.0)
        self.wave["zero"].setSingleStep(0.1)
        self.wave["amp"].setRange(-10,1200)
        self.wave["amp"].setValue(w["amp"]),
        self.wave["N"].setRange(10,100000)
        self.wave["N"].setValue(w["N"])

        for k, v in self.wave.items():
            t_l.addRow(yaml_name_lookup[k], v)

            if isinstance(v, QLineEdit):
                v.textChanged.connect((lambda: self.enable_button(self.save_conf_button)))
            if isinstance(v, (QSpinBox, QDoubleSpinBox)):
                v.valueChanged.connect((lambda: self.enable_button(self.save_conf_button)))

            
        tab.setLayout(t_l)
        return tab

    def measurement_conf(self):
        tab = QWidget()
        t_l = QFormLayout()
        self.meas = {}

        for k, v in self.default_conf["settings"].items():
            self.meas[k] = QDoubleSpinBox()
            self.meas[k].setValue(v)
            t_l.addRow(yaml_name_lookup[k], self.meas[k])

        for v in self.meas.values():
            if isinstance(v, QLineEdit):
                v.textChanged.connect((lambda: self.enable_button(self.save_conf_button)))
            if isinstance(v, (QSpinBox, QDoubleSpinBox)):
                v.valueChanged.connect((lambda: self.enable_button(self.save_conf_button)))



        tab.setLayout(t_l)
        return tab

    def data_conf(self):
        tab = QWidget()
        t_l = QFormLayout()
        self.data = {"sample": QLineEdit(), "path": QLineEdit()}
        
        if "data" in self.default_conf:
            self.data[yaml_name_lookup["sample"]].setText(self.default_conf["data"]["sample"])
            self.data[yaml_name_lookup["path"]].setText(self.default_conf["data"]["path"])


        for k, v in self.data.items():
            t_l.addRow(k, v)

        for v in self.data.values():
            if isinstance(v, QLineEdit):
                v.textChanged.connect((lambda: self.enable_button(self.save_conf_button)))
            if isinstance(v, (QSpinBox, QDoubleSpinBox)):
                v.valueChanged.connect((lambda: self.enable_button(self.save_conf_button)))
            
            
        tab.setLayout(t_l)
        return tab

    def status_bar_info(self, msg):
        self.parent.statusBar().setStyleSheet("color: black")
        self.parent.statusBar().showMessage(msg)

    def status_bar_error(self, msg):
        self.parent.statusBar().setStyleSheet("color: red")
        self.parent.statusBar().showMessage(msg)
        
        

def main():
    app = QApplication(sys.argv)
    app.setApplicationName("Bruker MR")

    window = MainWindow()

    window.show()

    app.exec()

if __name__ == "__main__":
    logging.basicConfig(filename='log/gui.log', filemode='w', level=logging.DEBUG)
    main()
