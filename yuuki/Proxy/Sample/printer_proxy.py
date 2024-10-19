import threading
from typing import Optional
from printable import Printable
from printer import Printer


class PrinterProxy(Printable):
    def __init__(self, name: Optional[str] = None) -> None:
        self.__name = name if name is not None else "No Name"
        self.__real: Optional[Printer] = None
        self.__lock = threading.Lock()

    def set_printer_name(self, name: str) -> None:
        with self.__lock:
            if self.__real is not None:
                # 「本人」にも設定する
                self.__real.set_printer_name(name)
            self.__name = name

    def get_printer_name(self) -> str:
        return self.__name

    def print(self, string: str) -> None:
        self.__realize()
        assert self.__real is not None  # for type checker
        self.__real.print(string)

    def __realize(self) -> None:
        with self.__lock:
            if self.__real is None:
                self.__real = Printer(self.__name)
