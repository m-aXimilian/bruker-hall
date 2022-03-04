from locale import currency
import os, sys
import logging
import time
from PyQt5.QtCore import pyqtSignal, QObject


import uuid
from concurrent import futures


parentdir = os.path.dirname(os.path.dirname(os.path.realpath(__file__)))
sys.path.append(parentdir)
sys.path.append(parentdir + "/fmr-py/src")

from src.HallMeasurement import HallMeasurement
import src.helpers as helper
from src.WaveForm import WaveForm
from src.States import STATUS, DIRECTION


class UiSignals(QObject):
    new_b_field = pyqtSignal()
    new_data_available = pyqtSignal()


class HallHandler:
    def __init__(self, config_file=""):
        if os.name == "posix":
            self.measure = helper.loadYAMLConfig("config/measurement.yaml")
        else:
            self.measure = helper.loadYAMLConfig("config/measurement.yaml")

        if config_file:
            self.measure = config_file

        self.steps = self.measure["wave"]["N"]
        self.m_hall = HallMeasurement(self.measure)
        self.last_b = 0

        self.already_measured = False

        self.signaller = UiSignals()
        self.update_id()

<<<<<<< HEAD
=======

>>>>>>> write phase, sensitivity and time to csv-comment
    def update_id(self):
        self.uuid = uuid.uuid1()

    def override_measure_config(self, conf):
        self.measure = conf
        self.m_hall = HallMeasurement(self.measure)

<<<<<<< HEAD
=======

>>>>>>> write phase, sensitivity and time to csv-comment
    def measure_with_wave(self):
        # pass the first value of the set-field vector to the reach_field_coarse function
        # to prevent an out-of-reach jump

        if not self.reach_field_coarse(self.m_hall.set_field[0]) == STATUS.OK:
            logging.error("Aborting in %s" % HallHandler.measure_with_wave.__name__)
            return

        self.last_b = self.m_hall.set_field[0]

        buffer = []
        for v in self.m_hall.set_field:
            buf_size = len(buffer)
            self.reach_field_fine(v)
            tmp = self.read_concurrently()
            if buf_size < 51:
                buffer.append(tmp)
            else:
                self.write_buffer(buffer)
                # UI: signal new data
                self.signaller.new_data_available.emit()
                buffer.clear()
                buffer.append(tmp)

        # ensure remaining data is written out in case the buffer is not full!
        buf_size = len(buffer)
        if not buf_size == 0:
            self.write_buffer(buffer)
            # UI: signal new data
            self.signaller.new_data_available.emit()
            buffer.clear()

    def reach_field_fine(self, b) -> STATUS:
        """Writes translated B-field set-values to the xantrex power supply
        and the PID-controller. While the field is not reached and the timeout
        is not exceeded, the function will block the calling thread.

        Args:
                b (num): B-field value to reach (mT)

        Returns:
                [:class:`~STATUS`]: Status info of"""
        c = abs(abs(b) - abs(self.last_b))
        if c > self.measure["settings"]["max-inc"]:
            e = "Field increment with {}mT higher than the allowed {}mT".format(
                c, self.measure["settings"]["max-inc"]
            )
            logging.error(e)
            raise ValueError(e)

        direction = self.field_diection(self.last_b, b)

        self.last_b = b

        self.current_field = self.m_hall.read_field()
        delta_tmp = abs(b - self.current_field)

        # UI: signal new b_field
        self.signaller.new_b_field.emit()

        xan_set = self.m_hall.single_xanterx_set(b, direction)
        pid_set = self.m_hall.single_pid_set(b)
        time.sleep(self.measure["settings"]["bruker-const"] * c)

        self.m_hall.writeVolt(self.m_hall.tasks["xantrex-writer"], xan_set)
        self.m_hall.writeVolt(self.m_hall.tasks["pid-writer"], pid_set)

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

        logging.debug("Reached set field of {:10.2f} mT".format(b))
        return STATUS.OK

    def reach_field_coarse(self, b) -> STATUS:
        """Pass any B-field value to this function. It will generate a linear vector based on the current B-field measurement and hand it over value by value to the :meth:`~HallHandler.reach_field_fine` method if it is within the configured boundaries.

        Returns:
                [:class:`~STATUS`]: status of the field-reach process"""
        tmp_inc = self.measure["settings"]["max-inc"]
        min_b, max_b = (
            self.measure["settings"]["min-field"],
            self.measure["settings"]["max-field"],
        )
        current_field = self.m_hall.read_field()

        if abs(current_field) < 0.005:
            # B-field value smaller than 5µT hints issues with the hall probe rather than sufficient measurement
            # don't try to reach b in that case
            logging.error("Power supply to the hall probe turned on???")
            return STATUS.ERROR

        if b < min_b or b > max_b:
            raise ValueError("Desired b field not in valid range!")

        if (abs(current_field - b)) < tmp_inc:
            return STATUS.OK

        self.last_b = round(current_field)
        
        reach_vector = WaveForm.linear(round(current_field), b, tmp_inc)
        fine_reach_ok = True

        for v in reach_vector:
            try:
                status = self.reach_field_fine(v)
                if not status == STATUS.OK:
                    fine_reach_ok = False
            except ValueError:
                return STATUS.ERROR

        if not fine_reach_ok:
            logging.warning(
                "Some errors occured during coarse reaching of the base B-field."
            )

        return STATUS.OK

    @staticmethod
    def field_diection(b_current, b_next) -> DIRECTION:
        """Calculates a direction based on a current and a next value.

        Args:
                b_current (num): current value
                b_next (num): next value

        Returns:
                [:class:`~DIRECTION`]: A direction of type"""

        tmp = DIRECTION.NONE

        s = b_next - b_current

        if s > 0:
            tmp = DIRECTION.UP
        if s < 0:
            tmp = DIRECTION.DOWN

        return tmp


    def read_concurrently(self):
        res_f = [None]*2
        res_xy = [None]*3
        with futures.ThreadPoolExecutor(max_workers=2) as e:
            e.submit(HallHandler.async_field_handle, res_f, self.m_hall)
            e.submit(HallHandler.async_xy_handle, res_xy, self.m_hall)
        tmp = [res_f, res_xy]
        return [i for s in tmp for i in s]


    @staticmethod
    def async_field_handle(r, hall):
        time.sleep(0.005)  # xy read from gpib is slower than daq-read
        tmp = hall.read_field()
        r[0] = time.time()
        r[1] = tmp


    @staticmethod
    def async_xy_handle(r, hall):
        tmp = hall.lockin.xy
        r[0] = time.time()
        r[1] = tmp[0]
        r[2] = tmp[1]


    def write_buffer(self, data):
        tmp_p = self.measure["data"]["path"]
        tmp_id = str(self.uuid)
        if tmp_p == "":
            self.filename = "./results/{}/data_{}.csv".format(tmp_id, tmp_id)
        else:
            self.filename = tmp_p + "{}/data_{}.csv".format(tmp_id, tmp_id)
        helper.write_data(
            self.filename, 
            data, 
            "time field, field mT, time lockin, x, y", 
            "{com}, phase={ph}, sensitivity={sens}, time constant={tc}"
                .format(
                    com = self.measure["data"]["comment"],
                    ph = self.m_hall.lockin.phase,
                    sens = self.m_hall.lockin.sensitivity,
                    tc = self.m_hall.lockin.time_constant
                )
            )
