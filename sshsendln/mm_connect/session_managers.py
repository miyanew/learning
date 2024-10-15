from abc import ABC, abstractmethod

from typing_extensions import Protocol


class SessionStrategy(Protocol):
    def connect(self) -> None: ...

    def disconnect(self) -> None: ...


class SessionManager(ABC):
    @abstractmethod
    def connect(self):
        pass

    @abstractmethod
    def disconnect(self):
        pass


class LeafServer(SessionManager):
    def __init__(self, host_name: str, session_strategy: SessionStrategy):
        self.host_name = host_name
        self.session_strategy = session_strategy
        self.session = None

    def connect(self) -> None:
        self.session = self.session_strategy.connect(self.session)

    def disconnect(self) -> None:
        self.session = self.session_strategy.disconnect(self.session)


class BastionServer(SessionManager):
    def __init__(self, host_name: str, session_strategy: SessionStrategy):
        self.host_name = host_name
        self.session_strategy = session_strategy
        self.next_hops = []
        self.session = None

    def add(self, server: SessionManager) -> None:
        self.next_hops.append(server)

    def connect(self) -> None:
        self.session = self.session_strategy.connect(self.session)

    def connect_all(self) -> None:
        self.connect()
        for next_hop in self.next_hops:
            next_hop.connect()

    def disconnect(self) -> None:
        self.session = self.session_strategy.disconnect(self.session)

    def disconnect_all(self) -> None:
        for next_hop in self.next_hops:
            next_hop.disconnect()
        self.disconnect()
