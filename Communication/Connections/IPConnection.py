import socket
import select

from Communication.Connections import ConnectionMode
from Communication.Connections.EncryptedConnection import EncryptedConnection
from Security.Handshakes.ECDHHandshake import ECDHHandshakeProvider
from Security.MessageCiphers.ChaChaMessageCipher import ChaChaCipherProvider


class IPConnection(EncryptedConnection):

    def __init__(self, address, connection_mode, timeout_seconds=5):
        self._connection_mode = connection_mode
        super().__init__(address, timeout_seconds, connection_mode)
        self.handshake_provider = ECDHHandshakeProvider(connection_mode)
        self.cipher_provider = ChaChaCipherProvider()

    def __enter__(self):
        self.connect(self._address)

    def __exit__(self):
        self.close()

    def _transmit(self, message):
        self._connection_handle.sendall(message)

    def _receive(self):
        message = None
        while True:
            data_available = select.select([self._connection_handle], [], [], self._timeout)
            if not data_available[0]:
                break
            message += self._connection_handle.recv(4096)
        return message

    def connect(self, address=None):
        if address is None:
            address = self._address
        self._connection_handle = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        if self._connection_mode == ConnectionMode.Server:
            self._connection_handle.bind(address)
            self._connection_handle.listen(1)
            self._connection_handle, _ = self._connection_handle.accept()
        else:
            self._connection_handle.connect(address)
        self._connection_handle.setblocking(0)
        super(IPConnection, self).connect(address)

    def close(self):
        self._connection_handle.close()
        del self._connection_handle
