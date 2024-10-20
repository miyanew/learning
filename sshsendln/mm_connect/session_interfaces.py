from abc import ABC, abstractmethod
from dataclasses import dataclass
from typing import Any

from typing_extensions import Protocol


class SessionStrategy(Protocol):
    def start_session(self) -> Any: ...

    def end_session(self) -> None: ...

    def send_command(self) -> str: ...


@dataclass
class SessionManager(ABC):
    host_name: str

    @abstractmethod
    def start_session(self) -> Any:
        pass

    @abstractmethod
    def end_session(self) -> None:
        pass

    @abstractmethod
    def send_command(self) -> str:
        pass
