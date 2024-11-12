from abc import ABC, abstractmethod
from typing import Any, Optional


class SessionManager(ABC):
    def __init__(self, host_name: str) -> None:
        self.host_name = host_name
        self.parent_session: Optional["SessionManager"] = None

    def set_parent(self, parent_session: "SessionManager") -> None:
        self.parent_session = parent_session

    @abstractmethod
    def connect(self) -> Any:
        pass

    @abstractmethod
    def disconnect(self) -> None:
        pass

    @abstractmethod
    def send_command(self) -> str:
        pass
