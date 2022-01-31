import os, sys
import logging
import importlib

parentdir = os.path.dirname(os.path.dirname(os.path.realpath(__file__)))
sys.path.append(parentdir)
sys.path.append(parentdir + "/fmr-py/src")
import measurement
import visa_devices


class HallHandler:
    pass

class HallMeasurement:
    pass
