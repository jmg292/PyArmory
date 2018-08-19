import os

from enum import unique, IntEnum

from cryptography.hazmat.primitives.hashes import SHA512
from cryptography.hazmat.primitives.kdf.hkdf import HKDF
from cryptography.hazmat.backends import default_backend


@unique
class AccessLevels(IntEnum):

    Maintenance = 0
    Privileged = 1
    Unprivileged = 2
    NotAuthenticated = 3


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
    def derive_key(shared_secret, key_size=32):
        if type(shared_secret) is int:
            shared_secret = str(shared_secret)
        if type(shared_secret) is str:
            shared_secret = bytes(shared_secret, "utf-8")
        return HKDF(
            algorithm=SHA512(),
            length=key_size,
            salt=None,
            info=b'handshake data',
            backend=default_backend()
        ).derive(shared_secret)
