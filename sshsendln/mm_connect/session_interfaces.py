from abc import ABC, abstractmethod
from dataclasses import dataclass
from typing import Optional, List, Any

from typing_extensions import Protocol


class SessionStrategy(Protocol):
    def start_session(self) -> Any: ...

    def end_session(self) -> None: ...

    def send_command(self) -> str: ...


@dataclass
class SessionManager(ABC):
    host_name: str

    def __init__(self):
        self.parent_session = None

    def set_parent(self, parent_session) -> None:
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

    def get_session_chain(self) -> List["SessionManager"]:
        """
        現在のノードまでのセッションチェーンを取得する

        Returns:
            List[SessionManager]: 最初のゲートウェイから現在のノードまでのSessionManagerのリスト
        """
        chain: List[SessionManager] = []
        current_session: Optional[SessionManager] = self

        while current_session:
            chain.insert(0, current_session)
            current_session = current_session.parent_session

        return chain

    def end_session_all(self) -> None:
        """
        現在のノードから親方向に遡って、すべてのセッションを終了する
        終了は末端（現在のノード）から開始する
        """
        for session in reversed(self.get_session_chain()):
            session.end_session()
