from Command.BaseCommand import BaseCommand


class NotAuthorizedException(Exception):

    def __init__(self, command: BaseCommand):
        self._command = command

    def __str__(self):
        return f"{self._command.name()} requires a higher access level to execute."
