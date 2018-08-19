from Security import Helpers
from Security.Handshakes.BaseHandshake import BaseHandshake

from cryptography.hazmat.backends import default_backend
from cryptography.hazmat.primitives.asymmetric import ec


class ECDHHandshakeProvider(BaseHandshake):

    def __init__(self, connection_mode):
        super().__init__(connection_mode)
        self._shared_secret = None

    def private_key(self):
        if self._private_key is None:
            self._private_key = ec.generate_private_key(
                ec.SECP521R1(), default_backend()
            )
        return self._private_key

    def public_key(self):
        if self._public_key is None:
            self._public_key = self.private_key().public_key()
        return self._public_key

    def increment_state(self, peer_message=None):
        super(ECDHHandshakeProvider, self).increment_state(peer_message)
        if not self._shared_secret and peer_message is not None:
            self._shared_secret = self.private_key().exchange(ec.ECDH(), peer_message)

    def encryption_key(self):
        if self._shared_secret is None:
            raise ValueError("Handshake secret is currently unavailable.")
        return Helpers.derive_key(self._shared_secret)