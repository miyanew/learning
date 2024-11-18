import csv
from collections import defaultdict
from typing import DefaultDict, Dict, Iterator, List, TextIO, Tuple

SUCCESS_CASE = "PROC_SUCCESS"


class AggregationRecord:
    """集計対象の1レコードを表現するデータクラス"""

    def __init__(self, app: str, cc: str, rc: str):
        self.app = app
        self.cc = cc
        self.is_success = rc == SUCCESS_CASE


class RequestReader:
    # """CSVからリクエストレコードを読み出すクラス"""

    # @staticmethod
    # def from_csv(file_path: str) -> Iterator[AggregationRecord]:
    #     """CSVファイルからリクエストレコードのイテレータを生成"""
    #     with open(file_path, "r", encoding="utf-8") as f:
    #         reader = csv.DictReader(f)
    #         for line in reader:
    #             yield AggregationRecord(app=line["APP"], cc=line["CC"], rc=line["RC"])

    @staticmethod
    def from_file(file: TextIO) -> Iterator[AggregationRecord]:
        """ファイルオブジェクトからリクエストレコードのイテレータを生成"""
        reader = csv.DictReader(file)
        for line in reader:
            yield AggregationRecord(app=line["app"], cc=line["cc"], rc=line["rc"])


class RequestAggregator:
    """リクエスト結果の集計を行うクラス"""

    def __init__(self):
        self.app_cc_stats: DefaultDict[Tuple[str, str], Dict[str, int]] = defaultdict(
            lambda: {"total": 0, "success": 0}
        )

    def process(self, records: Iterator[AggregationRecord]) -> None:
        """リクエストの統計を集計"""
        for record in records:
            key = (record.app, record.cc)
            stats = self.app_cc_stats[key]
            stats["total"] += 1
            stats["success"] += record.is_success

    def summarize(self) -> List[Dict]:
        """ "集計結果のサマリーを返す"""
        stats = []
        for (app, cc), counts in sorted(self.app_cc_stats.items()):
            success_rate = self._calculate_success_rate(
                counts["total"], counts["success"]
            )
            stats.append(
                {
                    "APP": app,
                    "CC": cc,
                    "TotalCount": counts["total"],
                    "SuccessCount": counts["success"],
                    "SuccessRate": f"{success_rate:.2f}",
                }
            )
        return stats

    def _calculate_success_rate(self, total: int, success: int) -> float:
        """成功率を計算して浮動小数点数で返す"""
        return (success / total * 100) if total > 0 else 0

    # def get_app_statistics(self) -> List[Dict]:
    #     """appごとの集計結果を返す"""
    #     app_stats: DefaultDict[str, Dict[str, int]] = defaultdict(
    #         lambda: {"total": 0, "success": 0}
    #     )

    #     for (app, _), counts in self.app_cc_stats.items():
    #         app_stats[app]["total"] += counts["total"]
    #         app_stats[app]["success"] += counts["success"]

    #     return [
    #         {
    #             "app": app,
    #             "total": counts["total"],
    #             "success": counts["success"],
    #             "success_rate": f"{(counts['success'] / counts['total'] * 100):.2f}",
    #         }
    #         for app, counts in sorted(app_stats.items())
    #     ]
