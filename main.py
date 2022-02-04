from ast import arg
import src.HallMeasurement as hall
from enum import IntFlag

import threading
import time

from concurrent import futures

class WRITEStatus(IntFlag):
    OK = 0
    TIMEOUT = 1

class STATUS(IntFlag):
    ERROR = -1
    OK = 0
    TIMEOUT = 7


class FIELDdir(IntFlag):
    DOWN = 0
    UP = 1

def thrd_f(res, i):
    time.sleep(1)
    res[i] = time.time_ns()


def rtrn_wr():
    return WRITEStatus.TIMEOUT


def main():

    res = [None]*2
    with futures.ThreadPoolExecutor(max_workers=2) as e:
        e.submit(thrd_f, res, 0)
        e.submit(thrd_f, res, 1)
        

    
    # t1 = threading.Thread(target=thrd_f, args=(res, 0))
    # t2 = threading.Thread(target=thrd_f, args=(res, 1))
    
    # t1.start()
    # t2.start()
    # t1.join()
    # t2.join()
    o = rtrn_wr()

    print(isinstance(o, WRITEStatus))
    print("%s not of %f" % (o, 1.2334))

    print(res[1]-res[0])

    frst = time.time_ns()
    time.sleep(1)
    scnd = time.time_ns()

    print(scnd-frst)

if __name__ == "__main__":
    main()
