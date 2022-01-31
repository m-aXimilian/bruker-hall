import os, sys
import numpy as np
import logging
import matplotlib.pyplot as plt

parentdir = os.path.dirname(os.path.dirname(os.path.realpath(__file__)))
sys.path.append(parentdir)

import src.helpers as h
import src.LookupFit as lookup

def main():
    logging.basicConfig(filename='../log/hall.log', filemode='w', level=logging.DEBUG)
    data = h.loadYAMLConfig("../config/H-field-lookup.yaml")
    H = np.linspace(0, 1100, 1000)

    up = lookup.LookupFit(data["rampup"][1], data["rampup"][0], 3)
    down = lookup.LookupFit(data["rampdown"][1], data["rampdown"][0],3)

    plt.plot(data["rampup"][1],data["rampup"][0], "bo", label="data up")
    plt.plot(H,up.getValue(H), "--b", label="fit up")

    plt.plot(data["rampdown"][1],data["rampdown"][0], "ro", label="data down")
    plt.plot(H,down.getValue(H), "--r", label="fit down")

    plt.grid(which='major',axis='y')
    plt.legend(loc="best")
    plt.legend()
    plt.show()


    test = [0, 164.59, 327.6, 491.2, 651.2, 806.1, 941.7, 1033.9]

    for v in test:
        print("{}mT correspond to: \n\tup: {}V\n\tdown:{}"
              .format(v, up.getValue(v), down.getValue(v)))

if __name__ == "__main__":
    main()
