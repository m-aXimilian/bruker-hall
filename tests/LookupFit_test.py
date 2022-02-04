import os, sys
import numpy as np
import logging
import matplotlib.pyplot as plt

parentdir = os.path.dirname(os.path.dirname(os.path.realpath(__file__)))
sys.path.append(parentdir)

import src.helpers as h
import src.LookupFit as lookup
import src.HallMeasurement as hall


def main():
    # logging.basicConfig(filename='../log/hall.log', filemode='w', level=logging.DEBUG)
    data = h.loadYAMLConfig("../config/B-field-lookup.yaml")
    H = np.linspace(0, 1100, 1000)

    up_x = np.array(data["rampup"][1])*100
    up_y = np.array(data["rampup"][0])

    down_x = np.array(data["rampdown"][1])*100
    down_y = np.array(data["rampdown"][0])

    up = lookup.LookupFit(np.array(data["rampup"][1])*100, up_y, 3)
    down = lookup.LookupFit(down_x, down_y,3)

    plt.plot(np.array(data["rampup"][1])*100,up_y, "bo", label="data ramp up")
    plt.plot(H,up.getValue(H), "--b", label="fit ramp up")

    plt.plot(down_x,down_y, "ro", label="data ramp down")
    plt.plot(H,down.getValue(H), "--r", label="fit ramp down")

    plt.grid(which='major',axis='both')
    plt.xlabel("B-field (mT)")
    plt.ylabel("Voltage (V)")
    plt.legend(loc="best")
    plt.legend()
    plt.title("Field-set functions from Lookup-tables")
    plt.tight_layout()
    plt.show()


    test = [0, 164.59, 327.6, 491.2, 651.2, 806.1, 941.7, 1033.9]

    for v in test:
        print("{}mT correspond to: \n\tup: {}V\n\tdown:{}"
              .format(v, up.getValue(v), down.getValue(v)))    



if __name__ == "__main__":
    main()
