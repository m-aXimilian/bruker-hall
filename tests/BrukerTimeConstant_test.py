import os, sys
import numpy as np
import logging
import matplotlib.pyplot as plt
from time import sleep
from statistics import median
import matplotlib.pyplot as plt

parentdir = os.path.dirname(os.path.dirname(os.path.realpath(__file__)))
sys.path.append(parentdir)

import src.helpers as helper
import src.BrukerTimeConstant as tconst


def measure():
    logging.basicConfig(filename='log/bruker.log', filemode='w', level=logging.INFO)
    bt = tconst.TimeConstant()
    bt.timing_loop()

def step(a, lim):
    r = []
    for i in range(len(a)-1):
        tmp = round(abs(a[i+1]-a[i]))
        if tmp > lim:
            r.append(tmp)
    return r

def eval():
    data = np.genfromtxt("tests/results/2022-02-09_15-50-08bruker-time-constant_to599mT.csv", delimiter=",", skip_header=1, names=True)
    steps = np.array(step(data["setval"], 0.5))
    step_mean = steps.mean()
    hist_dat = data["reachedat"][20:-1]
    me = hist_dat.mean()
    md = median(hist_dat)

    # plt.plot(data["setval"],data["reachedat"])
    plt.title("Reaching times for {:.0f}mT steps\nmax(B) = {}mT".format(step_mean, round(max(data["setval"]))))
    plt.xlabel("time/s")
    plt.ylabel("counts")
    plt.hist(hist_dat, bins=20)
    plt.axvline(me, color='k', linestyle='dashed')
    plt.axvline(md, color='b', linestyle='dashed')
    min_y, max_y = plt.ylim()

    plt.text(me*1.2, max_y*0.9, "Mean {:.1f}s -> {:.1f}s/mT".format(me, me/step_mean))
    plt.text(me*1.2, max_y*0.85, "Median {:.1f}s -> {:.1f}s/mT".format(md, md/step_mean), color='b')
    plt.tight_layout()
    plt.show()

if __name__ == "__main__":
    eval()
