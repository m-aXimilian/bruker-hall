import os, sys
import numpy as np
import logging
import matplotlib.pyplot as plt

parentdir = os.path.dirname(os.path.dirname(os.path.realpath(__file__)))
sys.path.append(parentdir)

import src.helpers as helper
import src.LookupFit as lookup
import src.HallMeasurement as hall


def main():
    hm = hall.HallMeasurement()
    print(hm.tasks)
    print(
        hm.tasks["xantrex-writer"].task.channel_names
    )
    print(
        hm.tasks["pid-writer"].task.channel_names
    )
    print(
        hm.tasks["reader"].task.channel_names
    )
    hm.tasks["xantrex-writer"].singleWrite(0)
    hm.tasks["pid-writer"].singleWrite(0)

    print(hm.tasks["reader"].singleRead())

    hm.tasks["xantrex-writer"].singleWrite(0)
    hm.tasks["pid-writer"].singleWrite(0)



if __name__ == "__main__":
    main()
