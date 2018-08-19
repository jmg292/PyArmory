from enum import IntEnum, unique


@unique
class ConnectionMode(IntEnum):

    Client = 0
    Server = 1
