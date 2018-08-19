class BaseConnection(object):

    def __init__(self, address, timeout):
        self._address = address
        self._timeout = timeout
        self._connection_handle = None

    def __enter__(self):
        raise NotImplementedError()

    def __exit__(self):
        raise NotImplementedError()

    def connect(self, host):
        raise NotImplementedError()

    def close(self):
        raise NotImplementedError()

    def send(self, message):
        raise NotImplementedError()

    def recv(self):
        raise NotImplementedError()
