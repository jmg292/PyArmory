import os
import json
import Command

from Security import AccessLevels
from Command.BaseCommand import BaseCommand
from Configuration.BaseConfiguration import BaseConfiguration


class DriveInfoObject(object):

    def __init__(self):
        self.drive_alias = ""
        self.volume_path = ""
        self.filesystem_type = ""
        self.is_encrypted = False
        self.required_access_level = AccessLevels.NotAuthenticated

    def to_dictionary(self):
        return {
            "drive_alias": self.drive_alias,
            "volume_path": self.volume_path,
            "is_encrypted": self.is_encrypted,
            "filesystem_type": self.filesystem_type,
            "required_access_level": self.required_access_level.value
        }

    @staticmethod
    def from_dictionary(info_dict):
        drive_info = DriveInfoObject()
        drive_info.drive_alias = info_dict["drive_alias"]
        drive_info.volume_path = info_dict["volume_path"]
        drive_info.is_encrypted = bool(info_dict["is_encrypted"])
        drive_info.filesystem_type = info_dict["filesystem_type"]
        drive_info.required_access_level = AccessLevels(info_dict["required_access_level"])
        return drive_info


@Command.ActiveProvider.register_configuration
class DriveInfoConfig(BaseConfiguration):

    def __init__(self):
        super().__init__()
        self.storage_file = ""
        self.drive_information = {}
        self._for_command = "drive_info"

    def save_drive_info(self):
        drive_info_dict = {}
        for drive_info_object in self.drive_information:
            drive_info_dict[drive_info_object.drive_alias] = drive_info_object.to_dictionary()
        with open(self.storage_file, "w") as outfile:
            outfile.write(json.dumps(self.drive_information, indent=4, sort_keys=True))

    def load_drive_info(self):
        with open(self.storage_file, "r") as infile:
            drive_info_dict = json.loads(infile.read())
        for drive_alias in drive_info_dict:
            drive_info = DriveInfoObject.from_dictionary(drive_info_dict[drive_alias])
            self.drive_information[drive_info.drive_alias] = drive_info

    def on_init(self, command_provider):
        if not os.path.isabs(self.storage_file):
            base_configuration = command_provider.resolve_configuration("Base")
            self.storage_file = os.path.join(base_configuration.plugin_data_dir, self.storage_file)
        if not os.path.isdir(os.path.dirname(self.storage_file)):
            os.mkdir(os.path.dirname(self.storage_file))
        if os.path.isfile(self.storage_file):
            self.load_drive_info()
        super(DriveInfoConfig, self).on_init(command_provider)

    def update(self):
        if not os.path.isdir(os.path.dirname(self.storage_file)):
            os.mkdir(os.path.dirname(self.storage_file))
        self.save_drive_info()
        super(DriveInfoConfig, self).update()

    def load_dictionary(self, config_dictionary):
        self.storage_file = config_dictionary["storage_file"]


@Command.ActiveProvider.register
class DriveInfoCommand(BaseCommand):

    def __init__(self):
        super().__init__()
        self._name = "drive_info"
        self._minimum_security_level = AccessLevels.NotAuthenticated

    def execute(self, *args, **kwargs):
        return_value = "{}"
        drive_information = Command.ActiveProvider.resolve_configuration(self._name).drive_information
        try:
            operand = args[0]
            alias = args[1].lower()
            if operand == "set":
                updated_drive_info = DriveInfoObject()
                updated_drive_info.drive_alias = alias
                updated_drive_info.volume_path = args[2]
                updated_drive_info.filesystem_type = args[3]
                updated_drive_info.is_encrypted = bool(args[4])
                updated_drive_info.required_access_level = AccessLevels(args[5])
                if Command.ActiveProvider.current_access_level <= updated_drive_info.required_access_level:
                    drive_information[alias] = updated_drive_info
                else:
                    return_value = "[DriveInfo] You must be authenticated at or above " \
                                   f"{updated_drive_info.required_access_level.name} in" \
                                   f" order to set it as a requirement."
            elif (operand == "get" or operand == "delete") and alias in drive_information:
                if operand == "get":
                    return_value = json.dumps(drive_information[alias])
                else:
                    if Command.ActiveProvider.current_access_level <= drive_information[alias].required_access_level:
                        del drive_information[alias]
                        return_value = f"[DriveInfo] All info pertaining to alias \"{alias}\" has been removed."
                    else:
                        return_value = "[DriveInfo] You do not have the required access level to delete alias " \
                                       f"\"{alias}\""
            else:
                return_value = "[DriveInfo] Invalid arguments supplied."
            if operand == "set" or operand == "delete":
                current_configuration = self._command_provider.resolve_configuration(self._name)
                current_configuration.drive_information = drive_information
                current_configuration.update()
        except IndexError:
            return_value = "[DriveInfo] Invalid number of arguments supplied."
        return return_value
