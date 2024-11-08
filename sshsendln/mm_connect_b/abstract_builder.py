from abc import ABC, abstractmethod


class SessionBuilder(ABC):
    def __init__(self, host_name: str):
        self.host_name = host_name

    @abstractmethod
    def get_config(self) -> dict:
        pass

    @abstractmethod
    def create_hosts(self):
        pass

    @abstractmethod
    def establish_connection(self):
        pass
