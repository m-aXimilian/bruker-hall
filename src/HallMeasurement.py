import os, sys
import logging
import importlib
import numpy as np
import time

from enum import IntFlag
from concurrent import futures
from pymeasure.instruments.srs import SR830

parentdir = os.path.dirname(os.path.dirname(os.path.realpath(__file__)))
sys.path.append(parentdir)
sys.path.append(parentdir + "/fmr-py/src")

import visa_devices as dev
import src.WaveForm as wave
import src.helpers as helper
import src.LookupFit as look
import src.Lockin as sr830


class READStatus(IntFlag):
    OK = 0
    TIMEOUT = 7



class DaqHallTask(dev.NIUSB6259):
    """Additions to the NIUSB6259 class."""
    def __init__(self) -> None:
        super().__init__()
        self.task_name = self.task.channel_names

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
        if os.name == 'posix':
            self.measure = helper.loadYAMLConfig("../config/measurement.yaml")
        else:
            self.measure = helper.loadYAMLConfig("config/measurement.yaml")
        
        self.steps = self.measure["wave"]["N"]
        self.m_hall = HallMeasurement()
        self.last_b = 0


    def reach_field_fine(self, b) -> READStatus:
        c = abs(b - self.last_b)
        if c > self.measure["settings"]["max-inc"]:
            e = "Field increment with {}mT higher than the allowed {}mT".format(c, self.measure["settings"]["max-inc"])
            logging.error(e)
            raise TypeError(e)

        self.last_b = b

        delta_tmp = abs(b - self.m_hall.read_field())
        start = time.time()
        
        # 1. add write out 2 set values

        while delta_tmp > self.measure["settings"]["delta-start"]:
            timeout = (time.time() - start) > self.measure["settings"]["timeout"]
            if timeout:
                return READStatus.TIMEOUT

            time.sleep(self.measure["settings"]["wait-b"])
            delta_tmp = abs(b - self.m_hall.read_field())



    def __write_out(self):
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

        self.lockin = sr830.Lockin(self.params["devices"]["lockin"]["id"])

        self.__generateLookups()
        self.__generateWave()
        self.__makeSetVXantrex()
        self.__makeSetVPID()
        self.__generateTasks()


    @staticmethod
    def writeVolt(t, v):
        """Write to a DaqHallTask Type task.

        Args:
        	t (DaqHallTask): task
		v (num): value to write"""
        logging.info("Wrote {}V to on task {}".format(v, t.task_name))
        t.singleWrite(v)


    @staticmethod
    def readVolt(t):
        logging.info("Reading from task {}".format(t.task_name))
        return t.singleRead()


    def read_field(self):
        """Reads a single value, selects the measure_index and scales by pid-scale from 
        the lookup config file.

        Returns: B-field value in mT
        """
        if self.tasks == None:
            e = "No task to read B-field from"
            logging.error(e)
            raise TypeError(e)

        return readVolt(self.tasks["reader"])[self.measure_index] / self.lookup["pid-scale"]



    def __generateTasks(self):
        self.tasks = {"reader": DaqHallTask()}
        self.tasks["reader"].add_channels(
            self.params["devices"]["daq-card"]["id"],
            self.params["devices"]["daq-card"]["ai"], _type="ai"
        )
        tmp = None
        for i, v in enumerate(self.params["devices"]["daq-card"]["ai"]):
            if v.find("measure") != -1:
                tmp = i
        self.measure_index = tmp

        if self.measure_index == None:
            e = "In the list of AI-channels one with <>-\"measure\" must be provided!"
            logging.error(e)
            raise TypeError(e)
        
        self.tasks["reader"].task_name = self.tasks["reader"].task.channel_names
        
        for k, v in self.params["devices"]["daq-card"]["ao"].items():
            tmp_name = "{}-writer".format(k)
            self.tasks.update({tmp_name: DaqHallTask()})
            self.tasks[tmp_name].add_channels(
                self.params["devices"]["daq-card"]["id"],
                v, _type="ao")
            self.tasks[tmp_name].task_name = self.tasks[tmp_name].task.channel_names


        self.pid_index = None
        self.xantrex_index = None

        for i, v in enumerate(self.params["devices"]["daq-card"]["ao"]):
            if v.find("xantrex") != -1:
                self.xantrex_index = i
            if v.find("pid") != -1:
                self.pid_index = i

        if self.pid_index == None or self.xantrex_index == None:
            e = "In the list of AO-channels one with \"xantrex\" and one with \"pid\" must be provided!"
            logging.error(e)
            raise TypeError(e)




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
            e = "Field increment with {}mT higher than the allowed {}mT".format(check, self.measure["settings"]["max-inc"])
            logging.error(e)
            raise TypeError(e)
        
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
        
