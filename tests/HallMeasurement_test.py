import os, sys
import numpy as np
import logging
import matplotlib.pyplot as plt
from time import sleep

parentdir = os.path.dirname(os.path.dirname(os.path.realpath(__file__)))
sys.path.append(parentdir)

import src.helpers as helper
import src.LookupFit as lookup
import src.HallMeasurement as hall


def main():
    if os.name == "posix":
        logging.basicConfig(filename='../log/hall.log', filemode='w', level=logging.DEBUG)
    else:
        logging.basicConfig(filename='log/hall.log', filemode='w', level=logging.DEBUG)
    hm = hall.HallMeasurement()

    
    res = [[]]
    for i, v in enumerate(hm.set_field):
        tmp_read = hm.readVolt(hm.tasks["reader"])[1]*100
        hm.writeVolt(hm.tasks["pid-writer"],round(hm.pid_set[i], 4))
        while abs(tmp_read - v) > 0.5:
            sleep(0.5)
            tmp_read = hm.readVolt(hm.tasks["reader"])[1]*100
        res[0].append(tmp_read)
    
    print(res)

    # print(hm.tasks)
    # print(
    #     hm.tasks["xantrex-writer"].task.channel_names
    # )
    # print(
    #     hm.tasks["pid-writer"].task.channel_names
    # )
    # print(
    #     hm.tasks["reader"].task.channel_names
    # )
    # hm.tasks["xantrex-writer"].singleWrite(0)
    # hm.tasks["pid-writer"].singleWrite(0)

    # print(hm.tasks["reader"].singleRead())

    # hm.tasks["xantrex-writer"].singleWrite(0)
    # hm.tasks["pid-writer"].singleWrite(0)
    
    


if __name__ == "__main__":
    main()
