class Proxy:

    def __init__(self, protocol, host, port, username, password):
        self._protocol = protocol
        self._host = host
        self._port = port
        self._username = username
        self._password = password

    def get_proxy_address(self):
        """
            protocol://username:password@host:port
            e.g., https://don.johnson:mr1@#zx@103.150.238.218:8080
        """
        return self._protocol + "://" + self._username + ":" + self._password + "@" + self._host + ":" + self._port,
