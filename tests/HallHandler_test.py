import os, sys
import numpy as np
import logging
import matplotlib.pyplot as plt
from time import sleep

parentdir = os.path.dirname(os.path.dirname(os.path.realpath(__file__)))
sys.path.append(parentdir)

import src.helpers as helper
import src.LookupFit as lookup
import src.HallHandler as hall

if __name__ == "__main__":
    logging.basicConfig(filename='log/hall-handler-test.log', filemode='w', level=logging.INFO)

    handle = hall.HallHandler()

    for v in handle.m_hall.set_field:
        handle.reach_field_fine(v)
        print("reaching {:10.3f} mT".format(v), end="\r")
    
    