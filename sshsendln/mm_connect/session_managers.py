from .session_interfaces import SessionManager, SessionStrategy


class TargetNode(SessionManager):
    def __init__(self, host_name: str, session_strategy: SessionStrategy):
        self.host_name = host_name
        self.session_strategy = session_strategy
        self.session = None

    def start_session(self) -> None:
        self.session = self.session_strategy.start_session(self.session)

    def end_session(self) -> None:
        self.session = self.session_strategy.end_session(self.session)

    def send_command(self, command: str) -> str:
        if self.session is None:
            raise ConnectionError("Not connected")
        return self.session_strategy.send_command(self.session, command)


class BastionNode(SessionManager):
    def __init__(self, host_name: str, session_strategy: SessionStrategy):
        self.host_name = host_name
        self.session_strategy = session_strategy
        self.session = None
        self.next_hops = []

    def start_session(self) -> None:
        self.session = self.session_strategy.start_session(self.session)

    def start_session_all(self) -> None:
        self.start_session()
        for next_hop in self.next_hops:
            next_hop.start_session()

    def end_session(self) -> None:
        self.session = self.session_strategy.end_session(self.session)

    def end_session_all(self) -> None:
        for next_hop in self.next_hops:
            next_hop.end_session()
        self.end_session()

    def send_command(self, command: str) -> str:
        if self.session is None:
            raise ConnectionError("Not connected")
        return self.session_strategy.send_command(self.session, command)

    def add(self, session_manager: SessionManager) -> None:
        self.next_hops.append(session_manager)
