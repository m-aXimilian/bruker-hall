import os, sys
import numpy as np
import logging
import matplotlib.pyplot as plt

parentdir = os.path.dirname(os.path.dirname(os.path.realpath(__file__)))
sys.path.append(parentdir)

import src.helpers as helper
import src.LookupFit as lookup
import src.HallMeasurement as hall


def main():
    hm = hall.HallMeasurement()

    fig, ax1 = plt.subplots()
    ax1.set_ylim(-10,1100)
    color = "tab:red"
    ax1.set_xlabel("index")
    ax1.set_ylabel("B-Field (mT)", color=color)
    ax1.plot(hm.set_field, color=color, linestyle='dashed', label="Set Field")
    ax1.tick_params(axis='y', labelcolor=color)

    color = "tab:blue"
    ax2 = ax1.twinx()
    ax2.set_ylim(-0.1,11)
    ax2.set_ylabel("Set Voltage (V)", color=color)
    ax2.plot(hm.xantrex_set, color=color, label="Set Volt Xantrex")
    ax2.plot(hm.pid_set, color=color, linestyle='dotted', label="Set Volt PID")
    ax2.tick_params(axis='y', labelcolor=color)

    ax1.grid()
    ax1.legend(loc="upper left")
    ax2.legend(loc="upper right")
    plt.tight_layout
    plt.title("Set values Xantrex + PID range 0 to 1T")
    plt.show()

    print(hm.pid_lookup.scaler(100))
    print(hm.xantrex_lookup["rampup"].getValue(100))



if __name__ == "__main__":
    main()
