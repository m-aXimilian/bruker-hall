import os, sys
import logging
import importlib
import threading
import numpy as np

from pymeasure.instruments.srs import SR830

parentdir = os.path.dirname(os.path.dirname(os.path.realpath(__file__)))
sys.path.append(parentdir)
sys.path.append(parentdir + "/fmr-py/src")

import visa_devices as dev
import src.WaveForm as wave
import src.helpers as helper
import src.LookupFit as look



class DaqHallTask(dev.NIUSB6259):
    """Additions to the NIUSB6259 class."""

    def singleRead(self):
        """Read a single value from all ai-channels."""
        if not self.task.channel_names[0].find("ai"): 
            logging.DEBUG("DAQ read failure")
            raise TypeError("Cannot read on a task without registered inputs")
        return self.task.read()

    def singleWrite(self, v):
        """Write a single value to an output channel.
        
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
        if os.name == 'posix':
            self.params = helper.loadYAMLConfig("../config/devices.yaml")
            self.lookup = helper.loadYAMLConfig("../config/H-field-lookup.yaml")
            self.measure = helper.loadYAMLConfig("../config/measurement.yaml")
        else:
            self.params = helper.loadYAMLConfig("config/devices.yaml")
            self.lookup = helper.loadYAMLConfig("config/H-field-lookup.yaml")
            self.measure = helper.loadYAMLConfig("config/measurement.yaml")

        self.__generateLookups()
        self.__generateWave()
        self.__makeSetVXantrex()
        self.__makeSetVPID()
        # self.__generateTasks()


    @staticmethod
    def writeVolt(t, v):
        """Write to a DaqHallTask Type task.

        Args:
        	t (DaqHallTask): task
		v (num): value to write"""
        logging.info("Wrote {}V to on task {}".format(v, t.task.channel_names))
        t.singleWrite(v)


    @staticmethod
    def readVolt(t):
        logging.info("Reading from task {}".format(t.task.channel_names))
        return t.singleRead()


    def __generateTasks(self):
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


    def __generateLookups(self):
        self.xantrex_lookup = {
            "rampup": look.LookupFit(
                self.lookup["rampup"][1],
                self.lookup["rampup"][0],
                self.lookup["deg"]),
            "rampdown": look.LookupFit(
                self.lookup["rampdown"][1],
                self.lookup["rampdown"][0],
                self.lookup["deg"]
                               )}

        self.pid_lookup = look.LinearFit(self.lookup["pid-scale"])


    def __generateWave(self):
        self.wave_handle = wave.WaveForm(
            self.measure["wave"]["amp"], self.measure["wave"]["N"],
            self.measure["wave"]["zero"]
        )
        
        # self.set_field = self.wave_handle.triangle()
        tmp = self.wave_handle.triangle()
        check = 0
        for i in range(len(tmp)-1):
            inc = round(abs(tmp[i+1] - tmp[i]), 3)
            if inc > check:
                check = inc

        if check > self.measure["settings"]["max-inc"]:
            logging.error("Field increment with {}mT higher than the allowed {}mT".format(check, self.measure["settings"]["max-inc"]))
            raise TypeError("Field increment too high ({}mT)! \naborting...".format(check))
        
        logging.info("H-field vector ok. Dim: {}, increment: {}".format(tmp.shape, check))
        self.set_field = tmp


    def __makeSetVXantrex(self):
        tmp = np.zeros(len(self.set_field))

        for i, v in enumerate(self.set_field[:-1]):
            if v == self.set_field[i+1] or v < self.set_field[i+1]:
                tmp[i] = self.xantrex_lookup["rampup"].getValue(v)
            if v > self.set_field[i+1]:
                tmp[i] = self.xantrex_lookup["rampdown"].getValue(v)

        # scale the xantrex voltate tmp with its maximum range (150V)
        # to the 10V output range of the DAQ card
        self.xantrex_set = tmp / self.params["devices"]["xantrex"]["range"]["high"] * 10

    def __makeSetVPID(self):
        self.pid_set = self.pid_lookup.scaler(self.set_field)

                
    def __del__(self):
        try:
            for t in self.tasks.values():
                t.task.close()
        except Exception:
            pass
        
