from ast import arg
import src.HallMeasurement as hall
import src.helpers as helper
from src.main_ui import *
from enum import IntFlag

import threading
import time

from concurrent import futures

def thrd_f(res, i):
    time.sleep(1)
    res[i] = time.time_ns()

def test():

    res = [None]*2
    with futures.ThreadPoolExecutor(max_workers=2) as e:
        e.submit(thrd_f, res, 0)
        e.submit(thrd_f, res, 1)
        
    param = helper.loadYAMLConfig("config/devices.yaml")
    print(param)
    
    # t1 = threading.Thread(target=thrd_f, args=(res, 0))
    # t2 = threading.Thread(target=thrd_f, args=(res, 1))
    
    # t1.start()
    # t2.start()
    # t1.join()
    # t2.join()

    print(res[1]-res[0])

    frst = time.time_ns()
    time.sleep(1)
    scnd = time.time_ns()

    print(scnd-frst)

def main():
    app = QApplication(sys.argv)
    app.setApplicationName("Bruker MR")

    window = MainWindow()

    window.show()

    app.exec()

if __name__ == "__main__":
    logging.basicConfig(filename='log/gui.log', filemode='w', level=logging.INFO)
    main()

