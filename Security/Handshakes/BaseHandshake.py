from Communication import Connections
from Security import Handshakes


class BaseHandshake(object):

    def __init__(self, connection_mode=Connections.ConnectionMode.Client):
        self._peer_key = None
        self._public_key = None
        self._private_key = None
        self._connection_mode = connection_mode
        self._current_state = Handshakes.HandshakeState.NotAssociated

    def current_state(self):
        return self._current_state

    def increment_state(self, peer_message=None):
        if self._current_state == Handshakes.HandshakeState.Completed:
            raise ValueError("Handshake already completed.")
        if self._current_state == Handshakes.HandshakeState.AwaitingReceipt and not peer_message:
            raise ValueError("Awaiting receipt, peer message must not be None.")
        if self._connection_mode == Connections.ConnectionMode.Client:
            if self._current_state == Handshakes.HandshakeState.NotAssociated:
                self._current_state = Handshakes.HandshakeState.AwaitingTransmission
            elif self._current_state == Handshakes.HandshakeState.AwaitingReceipt:
                self._current_state = Handshakes.HandshakeState.Completed
        else:
            self._current_state = Handshakes.HandshakeState(int(self._current_state) - 1)

    def public_key(self):
        if self._public_key is None:
            raise ValueError("Public key is not available.")

    def private_key(self):
        if self._private_key is None:
            raise ValueError("Private key not available.")

    def encryption_key(self):
        raise NotImplementedError()
