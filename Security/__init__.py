import os
import base64

from enum import unique, IntEnum

from cryptography.exceptions import InvalidKey
from cryptography.hazmat.primitives.hashes import SHA512
from cryptography.hazmat.primitives.kdf.hkdf import HKDF
from cryptography.hazmat.primitives.kdf.scrypt import Scrypt
from cryptography.hazmat.backends import default_backend


@unique
class AccessLevels(IntEnum):

    Maintenance = 0
    Privileged = 1
    Unprivileged = 2
    NotAuthenticated = 3
    Locked = 4


class Helpers:

    @staticmethod
    def get_random_int(max_value=2**10):
        intermediate_integer = 0
        while intermediate_integer <= 0:
            random_seed = bytearray(os.urandom(int(max_value)))
            intermediate_integer = int.from_bytes(random_seed, byteorder='big', signed=False)
            intermediate_integer *= (-1 if intermediate_integer < 0 else 1)
        return intermediate_integer % max_value

    @staticmethod
    def derive_key_for_storage(secret_key):
        if type(secret_key) is str:
            secret_key = bytes(secret_key, "utf-8")
        salt = os.urandom(32)
        kdf = Scrypt(
            salt=salt,
            length=64,
            n=2**7,
            r=8,
            p=1,
            backend=default_backend()
        )
        storable_key = kdf.derive(secret_key)
        return f"{base64.b64encode(salt)}:{base64.b64encode(storable_key)}"

    @staticmethod
    def keys_match(provided_key, stored_key):
        if type(provided_key) is str:
            provided_password = bytes(provided_key, "utf-8")
        salt, stored_key = stored_key.split(":")
        kdf = Scrypt(
            salt=base64.b64decode(salt),
            length=64,
            n=2**7,
            r=8,
            p=1,
            backend=default_backend()
        )
        try:
            kdf.verify(provided_key, base64.b64decode(stored_key))
            return True
        except InvalidKey:
            return False

    @staticmethod
    def derive_key(shared_secret, key_size=32, salt=None):
        if type(shared_secret) is int:
            shared_secret = str(shared_secret)
        if type(shared_secret) is str:
            shared_secret = bytes(shared_secret, "utf-8")
        return HKDF(
            algorithm=SHA512(),
            length=key_size,
            salt=salt,
            info=b'handshake data',
            backend=default_backend()
        ).derive(shared_secret)
