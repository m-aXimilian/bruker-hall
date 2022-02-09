from locale import currency
import os, sys
import logging
import time

parentdir = os.path.dirname(os.path.dirname(os.path.realpath(__file__)))
sys.path.append(parentdir)
sys.path.append(parentdir + "/fmr-py/src")

from src.HallMeasurement import HallMeasurement
import src.helpers as helper
from src.States import STATUS, DIRECTION


class HallHandler:
    def __init__(self):
        if os.name == 'posix':
            self.measure = helper.loadYAMLConfig("../config/measurement.yaml")
        else:
            self.measure = helper.loadYAMLConfig("config/measurement.yaml")
        
        self.steps = self.measure["wave"]["N"]
        self.m_hall = HallMeasurement()
        self.last_b = 0


    def reach_field_fine(self, b) -> STATUS:
        """Writes translated B-field set-values to the xantrex power supply 
        and the PID-controller. While the field is not reached and the timeout
        is not exceeded, the function will block.

        Args:
        	b (num): B-field value to reach (mT)
        
        Returns:
        	Status info of :class`~STATUS`"""
        c = abs(b - self.last_b)
        if c > self.measure["settings"]["max-inc"]:
            e = "Field increment with {}mT higher than the allowed {}mT".format(c, self.measure["settings"]["max-inc"])
            logging.error(e)
            raise TypeError(e)
        
        direction = self.field_diection(self.last_b, b)

        self.last_b = b

        self.current_field = self.m_hall.read_field()
        delta_tmp = abs(b - self.current_field)

        xan_set = self.m_hall.single_xanterx_set(b, direction)
        pid_set = self.m_hall.single_pid_set(b)
        time.sleep(self.measure["settings"]["bruker-const"]*c)

        self.m_hall.writeVolt(self.m_hall.tasks["xantrex-writer"], xan_set)
        self.m_hall.writeVolt(self.m_hall.tasks ["pid-writer"], pid_set)

        logging.debug("%f to xantrex AO, %f to pid AO" % (xan_set, pid_set))
        
        start = time.time()
        while delta_tmp > self.measure["settings"]["delta-start"]:
            timeout = (time.time() - start) > self.measure["settings"]["timeout"]
            if timeout:
                logging.warning("Timeout for set field %f mT" % b)
                return STATUS.TIMEOUT

            time.sleep(self.measure["settings"]["wait-b"])
            self.current_field = self.m_hall.read_field()
            delta_tmp = abs(b - self.current_field)

        logging.info("Reached set field of {:10.2f} mT".format(b))
        return STATUS.OK


    @staticmethod
    def field_diection(b_current, b_next) -> DIRECTION:
        """Calculates a direction based on a current and a next value.

        Args:
        	b_current (num): current value
        	b_next (num): next value
        
        Returns:
        	A direction of type :class`~DIRECTION`"""
        
        tmp = DIRECTION.NONE

        s = b_next - b_current

        if s > 0:
            tmp = DIRECTION.UP
        if s < 0:
            tmp = DIRECTION.DOWN

        return tmp


    def __write_out(self):
        pass
    
