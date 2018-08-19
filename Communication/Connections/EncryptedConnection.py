from Security.Handshakes import HandshakeState
from Communication.Connections.BaseConnection import BaseConnection
from Security.Handshakes.BaseHandshake import BaseHandshake
from Security.MessageCiphers.BaseCipherProvider import BaseCipherProvider


class EncryptedConnection(BaseConnection):

    def __init__(self, address, timeout, connection_mode):
        super().__init__(address, timeout)
        self._connection_mode = connection_mode
        self.cipher_provider = BaseCipherProvider()
        self.handshake_provider = BaseHandshake(self._connection_mode)

    def __enter__(self):
        raise NotImplementedError()

    def __exit__(self):
        raise NotImplementedError()

    def _transmit(self, message):
        raise NotImplementedError()

    def _receive(self):
        raise NotImplementedError()

    def connect(self, host):
        if self._connection_handle is None:
            raise ConnectionError("Connection handle does not exist.")
        while self.handshake_provider.current_state() != HandshakeState.Completed:
            if self.handshake_provider.current_state() == HandshakeState.NotAssociated:
                self.handshake_provider.increment_state()
            elif self.handshake_provider.current_state() == HandshakeState.AwaitingTransmission:
                self._transmit(self.handshake_provider.public_key())
                self.handshake_provider.increment_state()
            elif self.handshake_provider.current_state() == HandshakeState.AwaitingReceipt:
                peer_public_key = self._receive()
                self.handshake_provider.increment_state(peer_public_key)
        self.cipher_provider.encryption_key(self.handshake_provider.encryption_key())

    def close(self):
        raise NotImplementedError()

    def send(self, message):
        message = self.cipher_provider.encrypt_message(message)
        self._transmit(message)

    def recv(self):
        message = self._receive()
        if message is not None:
            message = self.cipher_provider.decrypt_message(message)
        return message
