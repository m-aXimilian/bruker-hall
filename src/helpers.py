import yaml
import logging
import numpy as np
import os


def loadYAMLConfig(_f):
    """Saveload yaml-config file

    Args:
        _f (str): complete path to the configuration file (can be relative).
    """
    with open(_f, "r") as f:
        try:
            logging.debug("Config file {} loaded".format(_f))
            return yaml.safe_load(f)
        except yaml.YAMLError as e:
            logging.debug("Cannot open config file {}".format(e))


def write_data(f, d, c="", m=""):
    """Write provided data to a file.

    Args:
        f (string): filename
        d (array like): data to write
        c (string): comma separated column names (must match the columns of the data) defaults to \"\"
        m (string): metadata to write to the header defaults to \"\" """

    ex = os.path.isfile(f)
    os.makedirs(os.path.dirname(f), exist_ok=True)
    with open(f, "a") as f_:
        if ex:
            np.savetxt(f_, np.array(d), delimiter=",")
        else:
            logging.info("Created file {}".format(os.path.abspath(f)))
            np.savetxt(
                f_, np.array(d), delimiter=",", header="{m}\n{c}".format(m=m, c=c)
            )
