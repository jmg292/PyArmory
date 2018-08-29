import json
import Command

from Configuration.BaseConfiguration import BaseConfiguration


class ConfigurationObject(BaseConfiguration):

    def __init__(self):
        super().__init__()
        self.home_folder = ""
        self.key_storage_file = ""
        self.temp_storage_location = ""
        self.enabled_plugins = ""
        self.totp_token = ""
        self._for_command = "Base"

    def load_dictionary(self, config_dictionary):
        validate_set = [
            "home_folder",
            "key_storage_file",
            "temp_storage_location",
            "enabled_plugins",
            "totp_token"
        ]
        for setting_name in validate_set:
            if setting_name not in config_dictionary:
                raise KeyError(f"Required key is missing from configuration: {setting_name}")
        self.totp_token = config_dictionary["totp_token"]
        self.home_folder = config_dictionary["home_folder"]
        self.key_storage_file = config_dictionary["key_storage_file"]
        self.temp_storage_location = config_dictionary["temp_storage_location"]
        for plugin_name in config_dictionary["enabled_plugins"]:
            plugin_config = Command.ActiveProvider.get_config_object_for_command(plugin_name)
            plugin_config.load_json(config_dictionary["enabled_plugins"][plugin_name])
            Command.ActiveProvider.initialize_configuration(plugin_config)
