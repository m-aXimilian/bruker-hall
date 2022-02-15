from ast import arg
import src.HallMeasurement as hall
import src.helpers as helper
from src.main_ui import *
from enum import IntFlag


from concurrent import futures



def main():
    app = QApplication(sys.argv)
    app.setApplicationName("Bruker MR")

    window = MainWindow()

    window.show()

    app.exec()

if __name__ == "__main__":
    logging.basicConfig(filename='log/gui.log', filemode='w', level=logging.INFO)
    main()

