from enum import unique, IntEnum
from Security import AccessLevels
from Security.MessageCiphers.ChaChaMessageCipher import ChaChaCipherProvider


@unique
class AccessLevels(IntEnum):

    Maintenance = 0
    Privileged = 1
    Unprivileged = 2
    NotAuthenticated = 3
    Locked = 4


class Keyring:

    def __init__(self):
        self._available_keys = {}
        for access_level in AccessLevels:
            self._available_keys[access_level] = {}

    @staticmethod
    def create_new_keyring(*args):
        keyring = {}
        for access_level in AccessLevels:
            available_keys = {}
            cipher_provider = ChaChaCipherProvider()
            cipher_provider.encryption_key(access_level.value)
            for i in range(access_level.value, 0):
                available_keys[AccessLevels(i)] = cipher_provider.encrypt_message(args[i])
            keyring[access_level.name] = available_keys
        return keyring
