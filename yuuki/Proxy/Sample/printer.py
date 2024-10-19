import time
from typing import Optional
from printable import Printable


class Printer(Printable):
    def __init__(self, name: Optional[str] = None) -> None:
        if name:
            self.__heavy_job(f"Printerのインスタンス({name})を生成中")
            self.__name = name
        else:
            self.__heavy_job("Printerのインスタンスを生成中")
            self.__name = ""

    def set_printer_name(self, name: str) -> None:
        self.__name = name

    def get_printer_name(self) -> str:
        return self.__name

    def print(self, string: str) -> None:
        print(f"=== {self.__name} ===")
        print(string)

    def __heavy_job(self, msg: str) -> None:
        print(msg, end="", flush=True)
        for _ in range(5):
            time.sleep(1)
            print(".", end="", flush=True)
        print("完了。")
