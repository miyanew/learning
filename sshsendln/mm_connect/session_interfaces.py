from abc import ABC, abstractmethod
from dataclasses import dataclass
from typing import Any

from typing_extensions import Protocol


class SessionStrategy(Protocol):
    def connect(self) -> Any:
        ...

    def disconnect(self) -> None:
        ...

    def send_command(self) -> str:
        ...


@dataclass
class SessionManager(ABC):
    host_name: str

    @abstractmethod
    def connect(self) -> Any:
        pass

    @abstractmethod
    def disconnect(self) -> None:
        pass

    @abstractmethod
    def send_command(self) -> str:
        pass
