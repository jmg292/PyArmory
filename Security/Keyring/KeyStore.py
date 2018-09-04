import json
import pyotp

from Security import Helpers
from Security import AccessLevels
from Security.MessageCiphers.ChaChaMessageCipher import ChaChaCipherProvider


class KeyStore:

    def __init__(self):
        self._otp_token = ""
        self._otp_times_authenticated = 0
        self._locked_key_store = ""
        self._available_keys = {}
        self._locked_access_levels = {}
        for access_level in AccessLevels:
            self._available_keys[access_level] = ""

    def _regenerate_key_store(self):
        can_regenerate_key_store = True
        for access_level in AccessLevels:
            if access_level not in self._available_keys or not self._available_keys[access_level.name]:
                can_regenerate_key_store = False
        if can_regenerate_key_store:
            self._locked_access_levels = {}
            for access_level in AccessLevels:
                cipher_provider = ChaChaCipherProvider()
                cipher_provider.encryption_key(self._available_keys[access_level.name])
                for i in range(access_level.value, 0):
                    encrypted_key = cipher_provider.encrypt_message(self._available_keys[AccessLevels(i).name])
                    if AccessLevels(i).name not in self._locked_access_levels[access_level.name]:
                        self._locked_access_levels[access_level.name] = {}
                    self._locked_access_levels[access_level.name][AccessLevels(i).name] = encrypted_key

    def _lock_key_store(self, regenerate_key_store=False):
        otp_token = pyotp.hotp.HOTP(self._otp_token, digits=32).at(self._otp_times_authenticated)
        encryption_key = Helpers.derive_key(otp_token)
        storable_key = Helpers.derive_key_for_storage(otp_token)
        if regenerate_key_store:
            self._regenerate_key_store()
        cipher_provider = ChaChaCipherProvider()
        cipher_provider.encryption_key(encryption_key)
        keystore_contents = {
            "otp_token": self._otp_token,
            "otp_times_authenticated": self._otp_times_authenticated,
            "keystore_contents": self._locked_access_levels
        }
        return json.dumps({
            "contents": cipher_provider.encrypt_message(json.dumps(keystore_contents)),
            "encryption_key": storable_key
        })

    def create_key_store(self, *args):
        self._otp_token = pyotp.random_base32(64)