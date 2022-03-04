import os, sys
from pymeasure.instruments.srs import SR830

parentdir = os.path.dirname(os.path.dirname(os.path.realpath(__file__)))
sys.path.append(parentdir)

import src.helpers as helper


class Lockin(SR830):
    """GPIB communication with a Stanford Research SR830 Lockin amplifier."""

    def __init__(self, resourceName, params, **kwargs):
        super().__init__(resourceName, **kwargs)
        self.params = params
        self.__setup()

    def __setup(self):
        """Sets a frequency configured in a measurement config-file and does a quick_range to ensure,
        the amplifier is not in overload."""
        # self.quick_range()
        self.frequency = self.params["f"]
