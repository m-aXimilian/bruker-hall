from enum import IntFlag


class STATUS(IntFlag):
    ERROR = -1
    OK = 0
    TIMEOUT = 7


class DIRECTION(IntFlag):
    DOWN = -1
    NONE = 0
    UP = 1
