from typing import Any, Optional

from .abstract_session_manager import SessionManager


class TargetNode(SessionManager):
    def __init__(self, host_name: str, session_strategy, send_command_strategy):
        self.host_name = host_name
        self.session_strategy = session_strategy
        self.send_command_strategy = send_command_strategy
        self.session = None
        self.parent_session = None

    def start_session(self, parent_session: Optional[Any] = None) -> None:
        self.session = self.session_strategy.start_session(parent_session)

    def end_session(self) -> None:
        self.session = self.session_strategy.end_session(self.session)

    def send_command(self, command: str, timeout: float = 30.0) -> str:
        if self.session is None:
            raise ConnectionError("Not connected")
        return self.send_command_strategy.send_command(self.session, command, timeout)
