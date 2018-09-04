import json

from Security import AccessLevels
from Security.MessageCiphers.ChaChaMessageCipher import ChaChaCipherProvider


class EncryptionKeyWrapper(object):

    def __init__(self, encryption_key):
        self._locked = False
        self.key_name = ""
        self.key_contents = ""
        self._encryption_key = encryption_key
        self.required_access_level = AccessLevels.Maintenance

    def __str__(self):
        if not self._locked:
            self._encrypt_key_contents()
        return json.dumps({
            "key_name": self.key_name,
            "required_access_level": str(self.required_access_level),
            "key_contents": self.key_contents
        })

    def _encrypt_key_contents(self):
        provider = ChaChaCipherProvider()
        provider.encryption_key(self._encryption_key)
        self.key_contents = provider.encrypt_message(self.key_contents)
        self._locked = True

    def _decrypt_contents(self):
        provider = ChaChaCipherProvider()
        provider.encryption_key(self._encryption_key)
        self.key_contents = provider.decrypt_message(self.key_contents)
        self._locked = False

    @staticmethod
    def from_string(serialized_key_wrapper, encryption_key):
        key_wrapper_contents = json.loads(serialized_key_wrapper)
        key_wrapper = EncryptionKeyWrapper(encryption_key)
        key_wrapper.key_name = key_wrapper_contents["key_name"]
        key_wrapper.required_access_level = AccessLevels(key_wrapper_contents["required_access_levels"])
