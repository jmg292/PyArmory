import os
import uuid
import Command
import subprocess

from Security import AccessLevels
from Command.BaseCommand import BaseCommand
from Command.CommandProvider import CommandProvider
from Command.Server.DriveInfo import DriveInfoObject
from Configuration.BaseConfiguration import BaseConfiguration


@Command.ActiveProvider.register_configuration
class DriveUtilityConfig(BaseConfiguration):

    def __init__(self):
        super().__init__()
        self._for_command = "temp_manager"
        self.volume_storage = ""
        self.supported_filesystem_formats = {}

    def on_init(self, command_provider: CommandProvider):
        if not os.path.isabs(self.volume_storage):
            base_configuration = Command.ActiveProvider.resolve_configuration("Base")
            self.volume_storage = os.path.join(base_configuration.home_folder, self.volume_storage)
        super(DriveUtilityConfig, self).on_init(command_provider)

    def load_dictionary(self, config_dictionary):
        self.volume_storage = config_dictionary["volume_storage"]
        self.supported_filesystem_formats = config_dictionary["supported_filesystem_formats"]


@Command.ActiveProvider.register
class DriveUtility(BaseCommand):

    def __init__(self):
        super().__init__()
        self._name = "drive_utility"
        self._minimum_security_level = AccessLevels.Privileged

    @staticmethod
    def _get_free_space_bytes():
        base_config = Command.ActiveProvider.resolve_configuration("Base")
        storage_volume_stats = os.statvfs(base_config.storage_volume)
        return storage_volume_stats.f_frsize * storage_volume_stats.f_bfree

    @staticmethod
    def convert_string_to_bytes(input_string: str):
        units = {
            "B": 1,
            "KB": 10 ** 3,
            "MB": 10 ** 6,
            "GB": 10 ** 9,
            "TB": 10 ** 12
        }
        output_int = 0
        input_string = input_string.upper()
        for unit in units:
            if input_string.endswith(unit):
                output_int = int(float(input_string.replace(unit, "")) * units[unit])
        return output_int

    @staticmethod
    def _encrypt_drive(alias, required_access_level, volume_path):
        operation_successful = False
        response = Command.ActiveProvider.execute_command("keyring", ["create", alias, required_access_level])
        if "created successfully" in response:
            response = Command.ActiveProvider.execute_command("keyring", ["unlock", alias])
            if "Unable" not in response:
                cryptsetup = subprocess.Popen(["cryptsetup", "luksFormat", volume_path, "--key-file", response],
                                                stdout=subprocess.PIPE, stderr=subprocess.PIPE, stdin=subprocess.PIPE)
                stdout, stderr = cryptsetup.communicate(input="YES\r\n")
                operation_successful = not stderr
                shred = subprocess.Popen(["shred", "--remove", response], stdout=subprocess.PIPE)
                shred.communicate()
        return operation_successful

    @staticmethod
    def _unlock_encrypted_drive(alias, volume_path, mapper_assignment):
        if not os.path.exists(mapper_assignment):
            keyfile_location = Command.ActiveProvider.execute_command("keyring", ["unlock", alias])
            if "Unable" not in keyfile_location:
                cryptsetup = subprocess.Popen(["cryptsetup", "luksOpen", volume_path, mapper_assignment,
                                               "--key-file", keyfile_location], stdout=subprocess.PIPE,
                                              stderr=subprocess.PIPE)
                stdout, stderr = cryptsetup.communicate()
                mapper_assignment = f"/dev/mapper/{mapper_assignment}"
                if stderr or not os.path.exists(mapper_assignment):
                    mapper_assignment = ""
                shred = subprocess.Popen(["shred", "--remove", keyfile_location], stdout=subprocess.PIPE)
                shred.communicate()
            else:
                mapper_assignment = ""
        else:
            mapper_assignment = ""
        return mapper_assignment

    def _create_filesystem(self, volume_path, fs_type):
        if os.path.exists(volume_path):
            subprocess.Popen([self._command_config.supported_filesystem_formats[fs_type], volume_path]).communicate()
            return True
        return False

    def _can_create_drive(self, alias, size, required_access_level, fs_format):
        operation_successful = False
        space_remaining = self._get_free_space_bytes()
        space_requested = self.convert_string_to_bytes(size)
        if space_requested and space_requested <= space_remaining:
            drive_info = Command.ActiveProvider.resolve_configuration("drive_info")
            if alias not in drive_info.drive_information:
                if required_access_level <= Command.ActiveProvider.current_access_level:
                    if fs_format in self._command_config.supported_filesystem_formats:
                        operation_successful = True
        return operation_successful

    def _create_drive(self, alias, size, required_access_level, should_encrypt, fs_format):
        creation_successful = False
        volume_path = os.path.join(self._command_config.volume_storage, uuid.uuid4().hex)
        if not os.path.exists(volume_path):
            size = self.convert_string_to_bytes(size)
            dd = subprocess.Popen(["dd", "if=/dev/urandom", f"of={volume_path}", "bs=1B", f"count={size}"],
                                  stdout=subprocess.PIPE, stderr=subprocess.PIPE)
            dd.communicate()
            if should_encrypt and self._encrypt_drive(alias, required_access_level, volume_path):
                mapper_assignment = self._unlock_encrypted_drive(alias, volume_path, uuid.uuid4().hex)
                if mapper_assignment:
                    creation_successful = self._create_filesystem(mapper_assignment, fs_format)
            elif not should_encrypt:
                creation_successful = self._create_filesystem(volume_path, fs_format)
            if creation_successful:
                creation_successful = volume_path
        return creation_successful

    def execute(self, *args, **kwargs):
        return_value = ""
        try:
            operand = args[0]
            if operand == "f" or operand == "free_space":
                return_value = self._get_free_space_bytes()
            elif operand == "c" or operand == "create":
                drive_info = DriveInfoObject()
                drive_info.drive_alias = args[1]
                size = args[2]
                drive_info.fs_format = args[3]
                drive_info.is_encrypted = bool(args[4])
                drive_info.required_access_level = AccessLevels(args[5])
                if self._can_create_drive(drive_info.drive_alias, size,
                                          drive_info.required_access_level,
                                          drive_info.fs_format):
                    volume_path = self._create_drive(drive_info.drive_alias, size,
                                                     drive_info.required_access_level,
                                                     drive_info.is_encrypted,
                                                     drive_info.fs_format)
                    if volume_path:
                        drive_info.volume_path = volume_path
                        drive_info_config = Command.ActiveProvider.resolve_configuration("drive_info")
                        drive_info_config.drive_information[drive_info.drive_alias] = drive_info_config
                        drive_info_config.update()
                        return_value = f"[DriveUtility] Drive with alias {drive_info.drive_alias} " \
                                       "has been created successfully."
                    else:
                        return_value = f"[DriveUtility] Unable to create drive."
                else:
                    return_value = "[DriveUtility] Unable to create drive with requested settings."
            elif operand == "u" or operand == "unlock":
                alias = args[1]
                drive_information = Command.ActiveProvider.resolve_configuration("drive_info").drive_information
                if alias in drive_information:
                    volume_path = drive_information[alias]
                    mapper_assignment = self._unlock_encrypted_drive(alias, volume_path, uuid.uuid4().hex)
                    if mapper_assignment:
                        return_value = mapper_assignment
                    else:
                        return_value = "[DriveUtility] Unable to unlock drive."
                else:
                    return_value = "[DriveUtility] Unable to unlock drive, alias not found."
        except IndexError:
            return_value = "[DriveUtility] Invalid number of arguments supplied."
        return return_value
