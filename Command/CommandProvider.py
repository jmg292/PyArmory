from Security import AccessLevels
from Command import NotAuthorizedException


class CommandProvider(object):

    def __init__(self):
        self._registered_commands = {}
        self._uninitialized_commands = {}
        self._registered_configurations = {}
        self._uninitialized_configurations = {}
        self._current_access_level = AccessLevels.NotAuthenticated

    def initialize(self):
        for command_name in self._uninitialized_commands:
            command = self._uninitialized_commands[command_name]()
            command.initialize(self)
            self._registered_commands[command_name] = command

    def initialize_configuration(self, initialized_config_object):
        self._uninitialized_configurations[initialized_config_object.command_name()] = initialized_config_object

    def resolve_configuration(self, command_name):
        if command_name in self._registered_configurations:
            return self._registered_configurations[command_name]

    def get_config_object_for_command(self, command_name):
        if command_name in self._uninitialized_configurations:
            return self._uninitialized_configurations[command_name]

    def register(self, command_class_pointer):
        self._uninitialized_commands[command_class_pointer().name()] = command_class_pointer
        return command_class_pointer

    def register_configuration(self, config_class_pointer):
        self._uninitialized_configurations[config_class_pointer().command_name()] = config_class_pointer
        return config_class_pointer

    def execute_command(self, command_name, *args):
        return_value = ""
        if command_name in self._registered_commands:
            command_object = self._registered_commands[command_name]
            if command_object.minimum_access_level() < self._current_access_level:
                return_value = str(NotAuthorizedException(command_object))
            else:
                return_value = command_object.execute(*args)
        return return_value
