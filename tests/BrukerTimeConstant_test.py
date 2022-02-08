import os, sys
import numpy as np
import logging
import matplotlib.pyplot as plt
from time import sleep
import matplotlib.pyplot as plt

parentdir = os.path.dirname(os.path.dirname(os.path.realpath(__file__)))
sys.path.append(parentdir)

import src.helpers as helper
import src.BrukerTimeConstant as tconst


def measure():
    logging.basicConfig(filename='log/bruker.log', filemode='w', level=logging.INFO)
    bt = tconst.TimeConstant()
    bt.timing_loop()

def eval():
    data = np.genfromtxt("tests/results/bruker-time-constant.csv", delimiter=",", skip_header=1, names=True)
    plt.plot(data["setval"],data["reachedat"])
    plt.show()

if __name__ == "__main__":
    eval()