from abc import ABC, abstractmethod
from typing import Any, Optional


class SessionManager(ABC):
    def __init__(self, host_name: str) -> None:
        self.host_name = host_name
        self.parent_session: Optional["SessionManager"] = None

    def set_parent(self, parent_session: "SessionManager") -> None:
        self.parent_session = parent_session

    @abstractmethod
    def start_session(self) -> Any:
        pass

    @abstractmethod
    def end_session(self) -> None:
        pass

    @abstractmethod
    def send_command(self) -> str:
        pass

    # def get_session_chain(self) -> List["SessionManager"]:
    #     chain: List["SessionManager"] = []
    #     current_session: Optional["SessionManager"] = self
    #     while current_session:
    #         chain.insert(0, current_session)
    #         current_session = current_session.parent_session
    #     return chain

    # def end_session_all(self) -> None:
    #     for session in reversed(self.get_session_chain()):
    #         session.end_session()
