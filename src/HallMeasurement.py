import os, sys
import logging
import importlib

from pymeasure.instruments.srs import SR830

parentdir = os.path.dirname(os.path.dirname(os.path.realpath(__file__)))
sys.path.append(parentdir)
sys.path.append(parentdir + "/fmr-py/src")

import visa_devices as dev
import src.WaveForm as wave
import src.helpers as helper

class DaqHallTask(dev.NIUSB6259):
    """Additions to the NIUSB6259 class."""

    def __del__(self):
        if self.task._handle is None:
            return
        logging.INFO("Closed task.")
        self.task.close()

    def singleRead(self):
        """Read a single value from all ai-channels."""
        if not self.task.ai_channels():
            logging.DEBUG("DAQ read failure")
            raise TypeError("Cannot read on a task without registered inputs")
        return self.task.read()

    def singleWrite(self, v):
        """Write a single value to a output channel.
        
        Args:
        	v (num): value to write.
        """
        if not self.task.ao_channels():
            logging.DEBUG("DAQ write failure")
            raise TypeError("Cannot write -> no output channel registerd")
        self.task.write()

class HallHandler:
    def __init__(self):
        pass
    
    
    
class HallMeasurement:
    def __init__(self):
        self.params = helper.loadYAMLConfig("../config/devices.yaml")
        self.tasks = {'reader': DaqHallTask()}
        for k, v in self.params["devices"]["daq-card"]["ao"]:
            self.tasks.update({"{}-writer".format(k): DaqHallTask()})
    
