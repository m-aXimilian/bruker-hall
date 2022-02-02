from ast import arg
import src.HallMeasurement as hall

import threading
import time


def thrd_f(res, i):
    time.sleep(1)
    res[i] = time.time_ns()


def main():
    d = { 'a': 10, 'b': 20, 'c': 30}
    tmp = None
    for i, v in enumerate(d):
        print(v)
        if v.find("b") != -1:
            tmp=i
    
    print(tmp)
                

    # res = [None]*2   
    
    # t1 = threading.Thread(target=thrd_f, args=(res, 0))
    # t2 = threading.Thread(target=thrd_f, args=(res, 1))
    
    # t1.start()
    # t2.start()
    # t1.join()
    # t2.join()

    # print(res[1]-res[0])

    # frst = time.time_ns()
    # time.sleep(1)
    # scnd = time.time_ns()

    # print(scnd-frst)

if __name__ == "__main__":
    main()