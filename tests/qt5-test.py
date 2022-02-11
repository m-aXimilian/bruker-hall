import os, sys, yaml

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
    QLineEdit
)

parentdir = os.path.dirname(os.path.dirname(os.path.realpath(__file__)))
sys.path.append(parentdir)

import src.helpers as helper

# Subclass QMainWindow to customize your application's main window
class MainWindow(QWidget):
    def __init__(self):
        super().__init__()
        if os.name == 'posix':
            self.conf = helper.loadYAMLConfig("../config/measurement.yaml")
        else:
            self.conf = helper.loadYAMLConfig("config/measurement.yaml")
        self.setWindowTitle("My App")
        self.setGeometry(100, 100, 600, 400)

        outer_layout = QVBoxLayout()
        self.setLayout(outer_layout)
        
        conf_layout = QTabWidget()
        conf_layout.addTab(self.wave_conf(), "Wave")
        conf_layout.addTab(self.measurement_conf(), "Measurement")
        conf_layout.addTab(self.data_conf(), "Data")
        outer_layout.addWidget(conf_layout)


    def wave_conf(self):
        tab = QWidget()
        t_l = QFormLayout()
        w = self.conf["wave"]
        form = QLineEdit()
        form.setText(w["form"])
        zero = QDoubleSpinBox()
        zero.setRange(0.0,1.0)
        zero.setSingleStep(0.1)
        zero.setValue(w["zero"])
        amp = QSpinBox()
        amp.setRange(-10, 1200)
        amp.setValue(w["amp"])
        n = QSpinBox()
        n.setRange(10, 100000)
        n.setValue(w["N"])
        t_l.addRow("Form", form)
        t_l.addRow("Zero", zero)
        t_l.addRow("Amplitude", amp)
        t_l.addRow("N", n)
        tab.setLayout(t_l)
        return tab

    def measurement_conf(self):
        tab = QWidget()
        t_l = QFormLayout()
        meas = {}

        for k, v in self.conf["settings"].items():
            meas[k] = QDoubleSpinBox()
            meas[k].setValue(v)
            t_l.addRow(k, meas[k])


        tab.setLayout(t_l)
        return tab

    def data_conf(self):
        tab = QWidget()
        t_l = QFormLayout()
        t_l.addRow("Sample", QLineEdit())
        t_l.addRow("Path", QLineEdit())
        tab.setLayout(t_l)
        return tab
        



def main():
    app = QApplication(sys.argv)

    window = MainWindow()

    window.show()

    app.exec()

if __name__ == "__main__":
    main()
