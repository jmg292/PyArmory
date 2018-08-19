from Security import AccessLevels
from Command import NotAuthorizedException


class CommandProvider(object):

    def __init__(self):
        self._registered_commands = {}
        self._uninitialized_commands = {}
        self._registered_configurations = {}
        self._current_access_level = AccessLevels.NotAuthenticated

    def initialize(self):
        for command_name in self._uninitialized_commands:
            command = self._uninitialized_commands[command_name]()
            command.initialize(self)
            self._registered_commands[command_name] = command

    def resolve_configuration(self, command_name):
        if command_name in self._registered_configurations:
            return self._registered_configurations[command_name]

    def register(self, command_class_pointer):
        self._uninitialized_commands[command_class_pointer().name()] = command_class_pointer
        return command_class_pointer

    def execute_command(self, command_name, *args):
        return_value = ""
        if command_name in self._registered_commands:
            command_object = self._registered_commands[command_name]
            if command_object.minimum_access_level() < self._current_access_level:
                return_value = str(NotAuthorizedException(command_object))
            else:
                return_value = command_object.execute(*args)
        return return_value
