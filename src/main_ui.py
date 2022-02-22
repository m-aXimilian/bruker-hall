from concurrent.futures import thread
from faulthandler import disable
import os, sys, yaml
from turtle import width
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
    "f (Hz)": "f",
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
            self.default_conf = helper.loadYAMLConfig("config/measurement.yaml")
        else:
            self.default_conf = helper.loadYAMLConfig("config/measurement.yaml")
        # self.setGeometry(100, 100, 1000, 600)
        self.parent = parent
        self.parent.statusBar().showMessage("init.")

        self.conf = {}

        # connect a HallHandler
        self.connect_devices()

        outer_layout = QHBoxLayout()
        left_col = QVBoxLayout()
        right_col = QVBoxLayout()
        xy_row = QHBoxLayout()
        left_col.setSpacing(10)
        conf_button_layout = QHBoxLayout()
        status_layout = QHBoxLayout()
        self.field_plot = pg.PlotWidget()
        self.x_plot = pg.PlotWidget()
        self.y_plot = pg.PlotWidget()
        
        # outmost layout
        self.setLayout(outer_layout)

        # add plot layout
        self.configure_plot(self.field_plot)
        self.configure_plot(self.x_plot)   
        self.configure_plot(self.y_plot)

        # add configuration layout
        self.conf_layout = QTabWidget()
        self.make_config_tabs(self.conf_layout)
        self.make_config_buttons(conf_button_layout)

        # add status layout
        status_layout.addStretch(2)
        self.show_field_button = QPushButton("Current B-Field (mT)")
        self.show_field_button.clicked.connect(self.show_b)
        status_layout.addWidget(self.show_field_button)
        self.LCD(status_layout)

        # glue the left layout (conf and status)
        left_col.addLayout(conf_button_layout)
        left_col.addWidget(self.conf_layout)
        left_col.addLayout(status_layout)
        self.make_start_button(left_col)

        # glue the right col (plots)
        xy_row.addWidget(self.x_plot)
        xy_row.addWidget(self.y_plot)
        right_col.addLayout(xy_row)
        right_col.addWidget(self.field_plot)

        # set to the outer layout       
        outer_layout.addLayout(left_col,1)
        outer_layout.addLayout(right_col, 3)
        # outer_layout.addWidget(self.field_plot,3)


    def connect_devices(self):
        self.m_handler = hall.HallHandler()

    
    def do_measure(self):
        self.m_handler.signaller.new_data_available.connect(self.live_plot)
        self.field_plot.clear()
        self.x_plot.clear()
        self.y_plot.clear()
        self.m_handler.already_measured = True
        self.show_connect_b()
        self.status_bar_info("Running measurement...")
        self.disable_button(self.start_button)
        self.disable_button(self.load_conf_button)
        self.disable_button(self.save_conf_button)
        m_th = threading.Thread(target=self.meas_thread, args=(self,))
        m_th.start()


            
    @staticmethod
    def meas_thread(n):
        n.m_handler.measure_with_wave()
        n.enable_button(n.start_button)
        n.enable_button(n.load_conf_button)
        n.enable_button(n.save_conf_button)
        n.status_bar_info("done. \t results saved to: %s" %os.path.abspath(n.m_handler.filename))
     

    def show_connect_b(self):
        set_b = lambda: self.b_lcd.display(self.m_handler.current_field)
        self.m_handler.signaller.new_b_field.connect(set_b)

    
    def show_b(self):
        tmp = self.m_handler.m_hall.read_field()
        self.b_lcd.display(tmp)


    def generate_config_dict(self):     
        self.conf = {"wave": self.__dict_convert(self.wave),
                     "settings": self.__dict_convert(self.meas),
                     "data": self.__dict_convert(self.data)
                     }
       

    def override_default_dict(self, file_name):
        self.default_conf = helper.loadYAMLConfig(file_name)
        self.conf = self.default_conf

     
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


    def live_plot(self):
        data = np.genfromtxt(self.m_handler.filename, skip_header=2, delimiter=',')
        # self.plot_data(self.field_plot, data)
        field_pen = pg.mkPen(color=(0,105,80), width=2)
        x_pen = pg.mkPen(color=(255,0,0), width=2)
        y_pen = pg.mkPen(color=(0,0,255), width=2)
        self.plot_pyqt(self.field_plot, data[:,0]-data[0,0], data[:,1], field_pen, "B-Field", {'left': "B/mT", 'bottom': "t/s"})
        self.plot_pyqt(self.x_plot, data[:,1], data[:,3], x_pen, "X-Value", {'left': "V/V", 'bottom': "B/mT"})
        self.plot_pyqt(self.y_plot, data[:,1], data[:,4], y_pen, "Y-Value", {'left': "V/V", 'bottom': "B/mT"})
        
        

    def plot_data(self, plt_widget, data):
        pen = pg.mkPen(color=(0,105,80))
        plt_widget.plot(data[:,0], data[:,1], pen=pen)

    def plot_pyqt(self, plt_widget, x, y, pen=None, title=None, labels=None):
        plt_widget.plot(x, y, pen=pen)
        plt_widget.setTitle(title)
        plt_widget.setLabel('left', labels['left'])
        plt_widget.setLabel('bottom', labels['bottom'])
        plt_widget.showGrid(x=True, y=True)



    def make_start_button(self, start_widget):
        self.start_button = QPushButton("Start Measurement")
        self.start_button.setStyleSheet("font: bold 20px")
        self.start_button.clicked.connect(self.do_measure)
        start_widget.addWidget(self.start_button)
            

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
        tmp_id = str(self.m_handler.uuid)
        if tmp_p == "":
            tmp_p = "./results/{}/config_{}.yaml".format(tmp_id, tmp_id)
        else:
            tmp_p += "{}/config_{}.yaml".format(tmp_id, tmp_id)

        self.status_bar_info("wrote config to: %s" % os.path.abspath(tmp_p))
        self.disable_button(self.save_conf_button)

        os.makedirs(os.path.dirname(tmp_p), exist_ok=True)
        with open(tmp_p, 'w') as out:
            yaml.dump(self.conf, out)
        
        if self.m_handler.already_measured:
            self.m_handler = hall.HallHandler(self.conf)
        else: 
            self.m_handler.override_measure_config(self.conf)

            

    def load_conf_button_handler(self):
        f = QFileDialog.getOpenFileName(self, "Select Configuration File", filter="Configuration Files (*.yaml *.yml)")
        
        logging.debug("config file from %s" % f[0])
        self.status_bar_info("load config from: %s" %f[0])

        self.override_default_dict(f[0])
        self.make_config_tabs(self.conf_layout)
        

        if self.m_handler.already_measured:
            self.m_handler = hall.HallHandler(self.conf)
        else: 
            self.m_handler.override_measure_config(self.conf)
        

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

        self.meas["f"].setRange(0.001, 102000)
        self.meas["f"].setValue(self.default_conf["settings"]["f"])

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
        self.data = {"sample": QLineEdit(), "path": QLineEdit(), "comment": QLineEdit()}
        
        if "data" in self.default_conf:
            self.data["sample"].setText(self.default_conf["data"]["sample"])
            self.data["path"].setText(self.default_conf["data"]["path"])
            self.data["comment"].setText(self.default_conf["data"]["comment"])


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
        
        
