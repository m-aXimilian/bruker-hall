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

    def singleRead(self):
        """Read a single value from all ai-channels."""
        if not self.task.channel_names[0].find("ai"): 
            logging.DEBUG("DAQ read failure")
            raise TypeError("Cannot read on a task without registered inputs")
        return self.task.read()

    def singleWrite(self, v):
        """Write a single value to a output channel.
        
        Args:
        	v (num): value to write.
        """
        if not self.task.channel_names[0].find("ao"):
            logging.DEBUG("DAQ write failure")
            raise TypeError("Cannot write -> no output channel registerd")
        self.task.write(v)

class HallHandler:
    def __init__(self):
        pass
    
    
    
class HallMeasurement:
    def __init__(self):
        self.params = helper.loadYAMLConfig("config/devices.yaml")
        self.tasks = {"reader": DaqHallTask()}
        self.tasks["reader"].add_channels(
            self.params["devices"]["daq-card"]["id"],
            self.params["devices"]["daq-card"]["ai"], _type="ai"
        )
        for k, v in self.params["devices"]["daq-card"]["ao"].items():
            self.tasks.update({"{}-writer".format(k): DaqHallTask()})
            self.tasks["{}-writer".format(k)].add_channels(
                self.params["devices"]["daq-card"]["id"],
                v, _type="ao")
            

    def __del__(self):
        for t in self.tasks.values():
            t.task.close()
