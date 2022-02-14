import os, sys
from statistics import mean
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

    # for v in handle.m_hall.set_field:
    #     handle.reach_field_fine(v)
    #     print("reaching {:10.3f} mT".format(v), end="\r")

        
    times = []
    for i in range(1000): # -> -0.0019304201602935792s mean
        tmp = handle.read_concurrently()
        times.append(tmp)
        logging.info("%f s skew" % tmp)

    # res_f = [None]*2
    # res_xy = [None]*3   
    # times = []

    # for i in range(1000): # -> 0,02560444s mean
    #     hall.HallHandler.async_field_handle(res_f, handle.m_hall)
    #     hall.HallHandler.async_xy_handle(res_xy, handle.m_hall)
    #     tmp = res_xy[0] - res_f[0]
    #     res_f = [None]*2
    #     res_xy = [None]*3           
    #     times.append(tmp)
    #     logging.info("%f s skew" % tmp)    
    
    print(times)
    print(mean(times))
