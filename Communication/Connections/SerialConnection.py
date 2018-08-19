import time
from serial import Serial

from Communication.Connections.EncryptedConnection import EncryptedConnection
from Security.Handshakes.ECDHHandshake import ECDHHandshakeProvider
from Security.MessageCiphers.ChaChaMessageCipher import ChaChaCipherProvider


class SerialConnection(EncryptedConnection):

    def __init__(self, address, connection_mode, timeout_seconds=5):
        super().__init__(address, timeout_seconds, connection_mode)
        self.handshake_provider = ECDHHandshakeProvider(connection_mode)
        self.cipher_provider = ChaChaCipherProvider()

    def __enter__(self):
        self.connect()

    def __exit__(self):
        self.close()
        del self._connection_handle

    def _transmit(self, message):
        self._connection_handle.write(message)
        self._connection_handle.flush()

    def _receive(self):
        received_message = None
        timeout_remaining = self._timeout
        while not self._connection_handle.in_waiting and timeout_remaining:
            time.sleep(0.5)
            timeout_remaining -= 1
        if self._connection_handle.in_waiting:
            received_message = self._connection_handle.read_all()
        return received_message

    def connect(self, address=None):
        if address is not None:
            self._address = address
        self._connection_handle = Serial(
            port=self._address,
            timeout=self._timeout
        )
        super(SerialConnection, self).connect(self._address)

    def close(self):
        self._connection_handle.close()
        del self._connection_handle
