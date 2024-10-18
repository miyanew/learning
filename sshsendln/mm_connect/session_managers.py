from .session_interfaces import SessionManager, SessionStrategy


class LeafServer(SessionManager):
    def __init__(self, host_name: str, session_strategy: SessionStrategy):
        self.host_name = host_name
        self.session_strategy = session_strategy
        self.session = None

    def connect(self) -> None:
        self.session = self.session_strategy.connect(self.session)

    def disconnect(self) -> None:
        self.session = self.session_strategy.disconnect(self.session)

    def send_command(self, command: str) -> str:
        if self.session is None:
            raise ConnectionError("Not connected")
        return self.session_strategy.send_command(self.session, command)


class BastionServer(SessionManager):
    def __init__(self, host_name: str, session_strategy: SessionStrategy):
        self.host_name = host_name
        self.session_strategy = session_strategy
        self.session = None
        self.next_hops = []

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

    def send_command(self, command: str) -> str:
        if self.session is None:
            raise ConnectionError("Not connected")
        return self.session_strategy.send_command(self.session, command)

    def add(self, session_manager: SessionManager) -> None:
        self.next_hops.append(session_manager)
