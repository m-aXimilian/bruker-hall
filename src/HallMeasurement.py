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


class STATUS(IntFlag):
    ERROR = -1
    OK = 0
    TIMEOUT = 7


class DIRECTION(IntFlag):
    DOWN = -1
    NONE = 0
    UP = 1


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

        delta_tmp = abs(b - self.m_hall.read_field())
        start = time.time()

        xan_set = self.m_hall.single_xanterx_set(b, direction)
        pid_set = self.m_hall.single_pid_set(b)

        self.m_hall.writeVolt(self.m_hall.tasks["xantrex-writer"], xan_set)
        self.m_hall.writeVolt(self.m_hall.tasks ["pid-writer"], pid_set)

        logging.debug("%f to xantrex AO, %f to pid AO" % (xan_set, pid_set))

        while delta_tmp > self.measure["settings"]["delta-start"]:
            timeout = (time.time() - start) > self.measure["settings"]["timeout"]
            if timeout:
                logging.warning("Timeout for set field %f mT" % b)
                return STATUS.TIMEOUT

            time.sleep(self.measure["settings"]["wait-b"])
            delta_tmp = abs(b - self.m_hall.read_field())

        logging.info("Reached set field of %f mT" % b)
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
    

    
        
class HallMeasurement:
    """Container for Bruker Measurement."""
    def __init__(self):
        if os.name == 'posix':
            self.params = helper.loadYAMLConfig("../config/devices.yaml")
            self.lookup = helper.loadYAMLConfig("../config/B-field-lookup.yaml")
            self.measure = helper.loadYAMLConfig("../config/measurement.yaml")
        else:
            self.params = helper.loadYAMLConfig("config/devices.yaml")
            self.lookup = helper.loadYAMLConfig("config/B-field-lookup.yaml")
            self.measure = helper.loadYAMLConfig("config/measurement.yaml")

        #self.lockin = sr830.Lockin(self.params["devices"]["lockin"]["id"])

        self.__generateLookups()
        self.__generateWave()
        self.__makeSetVXantrex()
        self.__makeSetVPID()
        # self.__generateTasks()


    @staticmethod
    def writeVolt(t, v):
        """Write to a DaqHallTask Type task.

        Args:
        	t (:class`~DaqHallTask`): task
		v (num): value to write"""
        if abs(v) > 10:
            e = "Value %f is beyond the analog channel range." % v
            logging.error(e)
            raise ValueError(e)
        
        logging.debug("Wrote {}V to on task {}".format(v, t.task_name))
        t.singleWrite(v)


    @staticmethod
    def readVolt(t):
        """Read a single value from a given task.
        
        Args:
        	t (:class`~DaqHallTask`): task to read from"""
        logging.debug("Reading from task {}".format(t.task_name))
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

        return self.readVolt(self.tasks["reader"])[self.measure_index] / self.lookup["pid-scale"]



    def __generateTasks(self):
        """For the devices specified in the config-file it generates 
        - one task for all analog inputs
        - one task for EACH analog output
        
        Attention: 
        	- There must be an AI, that has ``measure'' in the name
        	- There must be one AO with ``pid'' and one with ``xantrex'' in the name
        """
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
        """From the lookup table specified in the H-field-lookup config, create a lookup 
        dictionary with V_{up}(H) and V_{down}(H) (:class`~LookupFit.LookupFit`) representing fit-functions for up- and downramps of
        the magnetic field. Corresponding power supply voltages for a given filed in mT can be retrieved.
        A simple linear scale is initialized allowing to get back a set-voltage for a given field in mT for the PID controller.
        (:class`~LookupFit.LinearFit`)."""
        self.xantrex_lookup = {
            "rampup": look.LookupFit(
                np.array(self.lookup["rampup"][1])/self.lookup["pid-scale"],
                np.array(self.lookup["rampup"][0]),
                self.lookup["deg"]),
            "rampdown": look.LookupFit(
                np.array(self.lookup["rampdown"][1])/self.lookup["pid-scale"],
                np.array(self.lookup["rampdown"][0]),
                self.lookup["deg"]
                               )}

        self.pid_lookup = look.LinearFit(self.lookup["pid-scale"])


    def __generateWave(self):
        """Generates a waveform from the values specified in the measurement config based on :class`~WaveForm`"""
        self.wave_handle = wave.WaveForm(
            self.measure["wave"]["amp"], self.measure["wave"]["N"],
            self.measure["wave"]["zero"]
        )
        
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


    def single_xanterx_set(self, v, d) -> float:
        """From the lookup tables created in :meth`~HallMeasurement.__generateLookups` a set-value for the xantrex
        power supply is calculated based on the direction (up or down) specified.
        
        Args:
        	d (:class`~DIRECTION`): direction of the B-field w.r.t. the previous set-value
        	v (num): B-field value to look up
        
        Returns:
        	A single voltage value that can be directly fed to the xantrex power supply"""

        if not isinstance(d, DIRECTION):
            e = "%s not of type DIRECTION" % d
            logging.error(e)
            raise TypeError(e)

        if d == DIRECTION.UP or d == DIRECTION.NONE:
            return self.xantrex_lookup["rampup"].getValue(v) / self.params["devices"]["xantrex"]["range"]["high"] * 10

        return self.xantrex_lookup["rampdown"].getValue(v) / self.params["devices"]["xantrex"]["range"]["high"] * 10


    def single_pid_set(self, v) -> float:
        """From the linear scaler created in :meth`~HallMeasurement.__generateLookups` a set-value for the PID controller
        is calculated based on the direction (up or down) specified.
        
        Args:
        	v (num): B-field value to look up
        
        Returns:
        	A single voltage value that can be directly fed to the xantrex power supply"""

        return self.pid_lookup.scaler(v)


    def __makeSetVXantrex(self):
        """Calculates a set-voltage VECTOR for the xantrex power supply based on the set_field created in 
        :meth`~HallMeasurement.__generateWave`."""
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
        """Calculates a set-voltage VECTOR for the PID-controller based on the set_field created in 
        :meth`~HallMeasurement.__generateWave`."""
        self.pid_set = self.pid_lookup.scaler(self.set_field)

                
    def __del__(self):
        try:
            for t in self.tasks.values():
                t.task.close()
        except Exception:
            pass
        
