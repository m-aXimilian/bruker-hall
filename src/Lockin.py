import os, sys
from pymeasure.instruments.srs import SR830

parentdir = os.path.dirname(os.path.dirname(os.path.realpath(__file__)))
sys.path.append(parentdir)

import src.helpers as helper


class Lockin(SR830):
    def __init__(self, resourceName, **kwargs):
        super().__init__(resourceName, **kwargs)
        self.params = helper.loadYAMLConfig("config/measurement.yaml")["lockin"]
        self.__setup()

    def __setup(self):
        self.quick_range()
        self.frequency = self.params["f"]
        


