from ast import arg
import src.HallMeasurement as hall
from enum import IntFlag

import threading
import time

from concurrent import futures

class WRITEStatus(IntFlag):
    OK = 0
    TIMEOUT = 1


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
    print(rtrn_wr() == WRITEStatus.TIMEOUT)

    print(res[1]-res[0])

    frst = time.time_ns()
    time.sleep(1)
    scnd = time.time_ns()

    print(scnd-frst)

if __name__ == "__main__":
    main()
