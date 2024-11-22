import csv
import json
import os
from abc import ABC, abstractmethod
from io import StringIO
from typing import Dict, List


class StatisticsFormatter(ABC):
    """統計結果のフォーマッタの基底クラス"""

    @abstractmethod
    def format(self, statistics: List[Dict]) -> str:
        pass


class CSVFormatter(StatisticsFormatter):
    """CSV形式でフォーマットするクラス"""

    def format(self, statistics: List[Dict]) -> str:
        if not statistics:
            return ""

        output = StringIO()
        headers = statistics[0].keys()
        writer = csv.DictWriter(output, headers)
        writer.writeheader()
        writer.writerows(statistics)
        return output.getvalue()


class JSONFormatter(StatisticsFormatter):
    """JSON形式でフォーマットするクラス"""

    def format(self, statistics: List[Dict]) -> str:
        return json.dumps(statistics, ensure_ascii=False, indent=2)


class StatisticsExporter:
    """統計結果のエクスポートを担当するクラス"""

    def __init__(self, formatter: StatisticsFormatter):
        self.formatter = formatter

    def export(self, statistics: List[Dict], output_path: str) -> None:
        """統計結果をファイルに出力"""
        formatted_data = self.formatter.format(statistics)
        self._ensure_directory(output_path)

        with open(output_path, "w", encoding="utf-8") as file:
            file.write(formatted_data)

    def _ensure_directory(self, file_path: str) -> None:
        directory = os.path.dirname(file_path)
        os.makedirs(directory, exist_ok=True)
