class MMConnectError(Exception):
    """Base exception for mm_connect"""

    pass


class ConfigurationError(MMConnectError):
    """Configuration related errors"""

    pass


class ConnectionError(MMConnectError):
    """Connection related errors"""

    pass


class CommandError(MMConnectError):
    """Command execution related errors"""

    pass
