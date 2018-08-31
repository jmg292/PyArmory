import os
import json
import pyotp
import base64
import Command

from Security import Helpers
from Security import AccessLevels
from Command.BaseCommand import BaseCommand
from Configuration.BaseConfiguration import BaseConfiguration


class KeyringKey(object):

    def __init__(self):
        self.otp_token = ""
        self.otp_times_utilized = ""


@Command.ActiveProvider.register_configuration
class KeyringConfiguration(BaseConfiguration):

    def __init__(self):
        super().__init__()
        self._for_command = "keyring"
        self._locked_contents = ""
        self._keyfile_path = ""
        self._unlocked_keys = {}

    def update(self):
