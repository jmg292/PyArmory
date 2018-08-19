import os
import base64


class BaseCipherProvider(object):

    def __init__(self):
        self._iv_length = 0
        self._encryption_key = None
        self._cipher_provider = None

    def _get_init_vector(self, ciphertext=None):
        if ciphertext is None:
            iv = bytes(os.urandom(32))
        else:
            iv = ciphertext[:self._iv_length]
        return iv[:self._iv_length]

    def encryption_key(self, new_key=None):
        if self._encryption_key is None and new_key is None:
            raise ValueError("Encryption key not set.")
        elif self._encryption_key is None:
            self._encryption_key = new_key
        return self._encryption_key

    def cipher_provider(self):
        raise NotImplementedError()

    def encrypt_message(self, message):
        if type(message) is str:
            message = bytes(message, 'utf-8')
        iv = self._get_init_vector()
        ciphertext = self.cipher_provider().encrypt(
            nonce=iv,
            data=message,
            associated_data=None
        )
        return base64.b64encode(iv + ciphertext)

    def decrypt_message(self, message):
        message = base64.b64decode(message)
        iv = self._get_init_vector(message)
        message = message[self._iv_length:]
        return self.cipher_provider().decrypt(
            nonce=iv,
            data=message,
            associated_data=None
        ).decode('utf-8')
