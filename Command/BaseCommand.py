from Security import AccessLevels
from Command.CommandProvider import CommandProvider


class BaseCommand(object):

    def __init__(self):
        self._name = ""
        self._command_config = None
        self._command_provider = None
        self._minimum_security_level = AccessLevels.Maintenance

    def minimum_access_level(self):
        return self._minimum_security_level

    def name(self):
        return self._name

    def execute(self, *args, **kwargs) -> str:
        raise NotImplementedError()

    def initialize(self, provider: CommandProvider):
        self._command_provider = provider
        self._command_config = provider.resolve_configuration(self.name())
