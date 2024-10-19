from abc import ABC, abstractmethod


class Printable(ABC):
    @abstractmethod
    def set_printer_name(self, name: str) -> None:
        """名前の設定"""
        pass

    @abstractmethod
    def get_printer_name(self) -> str:
        """名前の取得"""
        pass

    @abstractmethod
    def print(self, string: str) -> None:
        """文字列表示(プリントアウト)"""
        pass
