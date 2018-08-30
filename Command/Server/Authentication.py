import os
import json
import base64
import Command

from Security import AccessLevels
from Command.BaseCommand import BaseCommand
from Configuration.BaseConfiguration import BaseConfiguration


@Command.ActiveProvider.register_configuration
class AuthenticationConfig(BaseConfiguration):

    def __init__(self):
        super().__init__()
        self.auth_file = ""
        self.available_keys = {}
        self.authentication_dict = {}

    def on_init(self, command_provider):
        super(AuthenticationConfig, self).on_init(command_provider)
        if not os.path.isabs(self.auth_file):
            base_config = Command.ActiveProvider.resolve_configuration("Base")
            self.auth_file = os.path.join(base_config.home_folder, self.auth_file)
        if os.path.isfile(self.auth_file):
            with open(self.auth_file, "r") as infile:
                self.authentication_dict = json.loads(infile.read())

    def load_dictionary(self, config_dictionary):
        self.auth_file = config_dictionary["auth_file"]