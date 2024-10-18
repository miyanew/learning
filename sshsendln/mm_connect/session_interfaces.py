from abc import ABC, abstractmethod

from typing import Any, Dict, List
from typing_extensions import Protocol


class SessionStrategy(Protocol):
    def connect(self) -> Any:
        ...

    def disconnect(self) -> None:
        ...

    def send_command(self) -> str:
        ...


class SessionManager(ABC):
    @abstractmethod
    def connect(self) -> Any:
        pass

    @abstractmethod
    def disconnect(self) -> None:
        pass

    @abstractmethod
    def send_command(self) -> str:
        pass
