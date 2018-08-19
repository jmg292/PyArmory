from Security.MessageCiphers.BaseCipherProvider import BaseCipherProvider
from cryptography.hazmat.primitives.ciphers.aead import AESGCM


class AesCipherProvider(BaseCipherProvider):

    def __init__(self):
        super().__init__()
        self._iv_length = 16

    def cipher_provider(self):
        if self._cipher_provider is None:
            self._cipher_provider = AESGCM(self.encryption_key())
        return self._cipher_provider
