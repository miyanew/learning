import json
import os
from abc import ABC, abstractmethod
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

        headers = statistics[0].keys()
        lines = [",".join(headers)]

        for stat in statistics:
            lines.append(",".join(str(stat[h]) for h in headers))

        return "\n".join(lines)


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
        directory = os.path.dirname(output_path)
        os.makedirs(directory, exist_ok=True)

        with open(output_path, "w", encoding="utf-8") as file:
            file.write(formatted_data)
