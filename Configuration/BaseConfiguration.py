from Command.CommandProvider import CommandProvider


class BaseConfiguration(object):

    def __init__(self):
        self._for_command = ""
        self._command_provider = None

    def command_name(self):
        return self._for_command

    def on_init(self, command_provider: CommandProvider):
        self._command_provider = command_provider

    def update(self):
        self._command_provider.update_config(self)

    def load_dictionary(self, config_dictionary):
        raise NotImplementedError()
