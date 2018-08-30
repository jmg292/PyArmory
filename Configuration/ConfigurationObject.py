import json
import Command

from Configuration.BaseConfiguration import BaseConfiguration


class ConfigurationObject(BaseConfiguration):

    def __init__(self):
        super().__init__()
        self.home_folder = ""
        self.plugin_data_dir = ""
        self.key_storage_file = ""
        self.storage_volume = ""
        self.temp_storage_location = ""
        self.enabled_plugins = ""
        self._for_command = "Base"

    @staticmethod
    def from_file(config_file_path):
        with open(config_file_path, "r") as infile:
            config_dict = json.loads(infile.read())
        config_object = ConfigurationObject()
        config_object.load_dictionary(config_dict)
        return config_object

    def load_dictionary(self, config_dictionary):
        validate_set = [
            "home_folder",
            "key_storage_file",
            "storage_volume"
            "temp_storage_location",
            "enabled_plugins",
            "plugin_data_dir",
        ]
        for setting_name in validate_set:
            if setting_name not in config_dictionary:
                raise KeyError(f"Required key is missing from configuration: {setting_name}")
        self.home_folder = config_dictionary["home_folder"]
        self.storage_volume = config_dictionary["storage_volume"]
        self.key_storage_file = config_dictionary["key_storage_file"]
        self.temp_storage_location = config_dictionary["temp_storage_location"]
        self.plugin_data_dir = config_dictionary["plugin_data_dir"]
        Command.ActiveProvider.initialize_configuration(self)
        for plugin_name in config_dictionary["enabled_plugins"]:
            plugin_config = Command.ActiveProvider.get_config_object_for_command(plugin_name)
            plugin_config.load_json(config_dictionary["enabled_plugins"][plugin_name])
            Command.ActiveProvider.initialize_configuration(plugin_config)
