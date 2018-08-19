from Security.MessageCiphers.BaseCipherProvider import BaseCipherProvider
from cryptography.hazmat.primitives.ciphers.aead import ChaCha20Poly1305


class ChaChaCipherProvider(BaseCipherProvider):

    def __init__(self):
        super().__init__()
        self._iv_length = 12

    def cipher_provider(self):
        if self._cipher_provider is None:
            self._cipher_provider = ChaCha20Poly1305(self.encryption_key())
        return self._cipher_provider