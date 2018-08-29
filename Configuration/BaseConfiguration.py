class BaseConfiguration(object):

    def __init__(self):
        self._for_command = ""

    def command_name(self):
        return self._for_command

    def load_dictionary(self, config_dictionary):
        raise NotImplementedError()