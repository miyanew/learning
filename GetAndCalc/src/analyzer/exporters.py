from abc import ABC, abstractmethod
from pathlib import Path
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


class StatisticsExporter:
    """統計結果のエクスポートを担当するクラス"""

    def __init__(self, formatter: StatisticsFormatter):
        self.formatter = formatter

    def export(self, statistics: List[Dict], output_path: str) -> None:
        """統計結果をファイルに出力"""
        formatted_data = self.formatter.format(statistics)
        Path(output_path).write_text(formatted_data, encoding="utf-8")
