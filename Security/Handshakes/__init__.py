from enum import IntEnum, unique

from Security.Handshakes.BaseHandshake import BaseHandshake
from Security.Handshakes.DHKEHandshake import DHKEHandshakeProvider
from Security.Handshakes.ECDHHandshake import ECDHHandshakeProvider

@unique
class HandshakeState(IntEnum):

    Completed = 0
    AwaitingTransmission = 1
    AwaitingReceipt = 2
    NotAssociated = 3
