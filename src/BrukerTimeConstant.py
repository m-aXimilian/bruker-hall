from locale import currency
import os, sys
import logging
import time
import numpy as np

parentdir = os.path.dirname(os.path.dirname(os.path.realpath(__file__)))
sys.path.append(parentdir)
sys.path.append(parentdir + "/fmr-py/src")

from src.HallMeasurement import HallMeasurement
from src.HallHandler import HallHandler
import src.helpers as helper
from src.States import STATUS, DIRECTION

class TimeConstant(HallHandler):
    def __init__(self):
        if os.name == 'posix':
            self.measure = helper.loadYAMLConfig("../config/measurement.yaml")
        else:
            self.measure = helper.loadYAMLConfig("config/measurement.yaml")
        
        self.steps = self.measure["wave"]["N"]
        self.m_hall = HallMeasurement()
        self.last_b = 0

    def timing_loop(self):
        res = []
        for v in self.m_hall.set_field:
            print("reaching {:10.3f}".format(v), end="\r")
            tmp = [self.set_xantrex(v), v]
            res.append(tmp)
        
        helper.write_data("tests/results/bruker-time-constant.csv", np.array(res), "reached-at,set-val")
            
            
            


    def set_xantrex(self, b):
        c = abs(b - self.last_b)
        if c > self.measure["settings"]["max-inc"]:
            e = "Field increment with {}mT higher than the allowed {}mT".format(c, self.measure["settings"]["max-inc"])
            logging.error(e)
            raise TypeError(e)

        direction = self.field_diection(self.last_b, b)

        self.last_b = b

        self.current_field = self.m_hall.read_field()
        
        start = time.time()
        xan_set = self.m_hall.single_xanterx_set(b, direction)
        self.m_hall.writeVolt(self.m_hall.tasks["xantrex-writer"], xan_set)

        # tmp_diff = abs(self.current_field - self.m_hall.read_field())
        tmp_diff = 6

        while tmp_diff > 0.1:
            timeout = (time.time() - start) > 120
            if timeout:
                logging.warning("Timeout for set field %f mT" % b)
                return STATUS.TIMEOUT
            self.current_field = self.m_hall.read_field()
            time.sleep(0.2)
            tmp_diff = abs(self.current_field - self.m_hall.read_field())

        return time.time() - start
    
        
