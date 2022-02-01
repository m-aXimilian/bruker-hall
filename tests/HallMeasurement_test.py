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

if __name__ == "__main__":
    main()
