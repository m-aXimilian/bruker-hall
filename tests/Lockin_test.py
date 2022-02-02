import os, sys
from pymeasure.instruments.srs import SR830

parentdir = os.path.dirname(os.path.dirname(os.path.realpath(__file__)))
sys.path.append(parentdir)


import src.helpers as helper
import src.LookupFit as lookup
import src.HallMeasurement as hall
import src.Lockin as lock


def main():
    hm = hall.HallMeasurement()
    print(hm.lockin.xy)
    


if __name__ == "__main__":
    main()