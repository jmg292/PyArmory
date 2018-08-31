import os
import json
import Command

from Security import Helpers
from Security import AccessLevels
from Command.BaseCommand import BaseCommand
from Configuration.BaseConfiguration import BaseConfiguration


@Command.ActiveProvider.register_configuration
class AuthenticationConfig(BaseConfiguration):

    def __init__(self):
        super().__init__()
        self._for_command = "authenticate"
        self.auth_file_path = ""
        self.stored_keys = {}
        self.unlocked_keys = {}

    def on_init(self, command_provider):
        super(AuthenticationConfig, self).on_init(command_provider)
        if not os.path.isabs(self.auth_file_path):
            base_config = Command.ActiveProvider.resolve_configuration("Base")
            self.auth_file_path = os.path.join(base_config.home_folder, self.auth_file_path)
        if os.path.isfile(self.auth_file_path):
            with open(self.auth_file_path, "r") as infile:
                self.stored_keys = json.loads(infile.read())

    def update(self):
        super(AuthenticationConfig, self).update()
        if Command.ActiveProvider.resolve_configuration("keyring") is not None:
            Command.ActiveProvider.execute_command("keyring", ["auth_config_updated"])

    def load_dictionary(self, config_dictionary):
        self.auth_file_path = config_dictionary["auth_file_path"]


@Command.ActiveProvider.register
class AuthenticationCommand(BaseCommand):

    def __init__(self):
        super().__init__()
        self._name = "authenticate"
        self._minimum_security_level = AccessLevels.Locked

    def execute(self, *args, **kwargs):
        return_value = "0"
        try:
            auth_level_requested = AccessLevels(args[0])
            if auth_level_requested <= Command.ActiveProvider.current_access_level:
                auth_config = Command.ActiveProvider.resolve_configuration("authenticate")
                if auth_level_requested not in auth_config.unlocked_keys:
                    if auth_level_requested in auth_config.stored_keys:
                        if Helpers.keys_match(args[1], auth_config.stored_keys[auth_level_requested]["stored_key"]):
                            derived_key = Helpers.derive_key(args[1], auth_config.stored_keys[auth_level_requested]["salt"])
                            auth_config.unlocked_keys[auth_level_requested] = derived_key
                            auth_config.update()
                            return_value = "1"
        except ValueError:
            pass
        except IndexError:
            pass
        return return_value

