import os, sys
import logging

parentdir = os.path.dirname(os.path.dirname(os.path.realpath(__file__)))
sys.path.append(parentdir)
sys.path.append(parentdir + "/fmr-py/src")

import visa_devices as dev


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
