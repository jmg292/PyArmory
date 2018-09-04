import os
import uuid
import Command
import subprocess

from Security import AccessLevels
from Command.BaseCommand import BaseCommand
from Command.Server.DriveUtility import DriveUtility
from Configuration.BaseConfiguration import BaseConfiguration


@Command.ActiveProvider.register_configuration
class TempManagerConfig(BaseConfiguration):

    def __init__(self):
        super().__init__()
        self.temp_size = ""
        self.volume_storage = ""
        self.temp_storage_location = ""
        self._for_command = "temp_manager"

    def load_dictionary(self, config_dictionary):
        self.temp_size = config_dictionary["temp_size"]
        self.volume_storage = config_dictionary["volume_storage"]
        self.temp_storage_location = config_dictionary["temp_storage_location"]


@Command.ActiveProvider.register
class TempManager(BaseCommand):

    def __init__(self):
        super().__init__()
        self._name = "temp_manager"
        self._minimum_security_level = AccessLevels.Locked

    def _encrypt_temp(self, temp_volume):
        mapper_assignment = uuid.uuid4().hex
        keyfile_path = os.path.join(self._command_config.volume_storage, uuid.uuid4().hex)
        with open(keyfile_path, "wb") as outfile:
            outfile.write(os.urandom(4096))
        subprocess.Popen(["cryptsetup", "luksFormat", temp_volume, "--key-file", keyfile_path], stdout=subprocess.PIPE,
                         stderr=subprocess.PIPE, stdin=subprocess.PIPE).communicate(input="YES\r\n")
        subprocess.Popen(["cryptsetup", "luksOpen", temp_volume, mapper_assignment, "--key-file", keyfile_path],
                         stdout=subprocess.PIPE, stderr=subprocess.PIPE).communicate()
        subprocess.Popen(["shred", "--remove", keyfile_path], stdout=subprocess.PIPE).communicate()
        return os.path.join("/dev", "mapper", mapper_assignment)

    def _create_temp(self):
        free_space_bytes = DriveUtility.convert_string_to_bytes(self._command_config.temp_size)
        if not os.path.exists(self._command_config.volume_storage):
            os.mkdir(self._command_config.volume_storage)
        volume_path = os.path.join(self._command_config.volume_storage, uuid.uuid4().hex)
        subprocess.Popen(["mount", "-t", "ramfs", "-o", "rw", "ramfs", self._command_config.volume_storage],
                         stdout=subprocess.PIPE, stderr=subprocess.PIPE).communicate()
        subprocess.Popen(["dd", "if=/dev/urandom", f"of={volume_path}", "bs=1B", f"count={free_space_bytes}"],
                         stdout=subprocess.PIPE, stderr=subprocess.PIPE).communicate()
        mapper_assignment = self._encrypt_temp(volume_path)
        subprocess.Popen(["mkfs.ext4", mapper_assignment], stdout=subprocess.PIPE).communicate()
        subprocess.Popen(["mount", "-t", "ext4", "-o", "rw", mapper_assignment,
                          self._command_config.temp_storage_location], stdout=subprocess.PIPE).communicate()

    def execute(self, *args, **kwargs):
        try:
            if args[0].lower() == "maketemp":
                self._create_temp()
                return_value = "[TempManager] Temp space successfully created, encrypted, and mounted."
            elif args[0].lower() == "gettemp":
                return_value = self._command_config.temp_storage_location
            else:
                return_value = f"[TempManager] Invalid argument: {args[0]}"
        except IOError as e:
            return_value = str(e)
        except IndexError:
            return_value = "[TempManager] Invalid number of arguments supplied."
        return return_value
