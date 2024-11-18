import csv
from collections import defaultdict
from typing import DefaultDict, Dict, Iterator, List, Set, TextIO, Tuple

SUCCESS_CASE = "PROC_SUCCESS"


class RequestRecord:
    """リクエストの1レコードを表現するデータクラス"""

    def __init__(self, app: str, cc: str, rc: str):
        self.app = app
        self.cc = cc
        self.is_success = rc == SUCCESS_CASE


class RequestReader:
    """CSVからリクエストレコードを読み出すクラス"""

    @staticmethod
    def from_csv(file_path: str) -> Iterator[RequestRecord]:
        """CSVファイルからリクエストレコードのイテレータを生成"""
        with open(file_path, "r", encoding="utf-8") as f:
            reader = csv.DictReader(f)
            for line in reader:
                yield RequestRecord(app=line["app"], cc=line["cc"], rc=line["rc"])

    # @staticmethod
    # def from_file(file: TextIO) -> Iterator[RequestRecord]:
    #     """ファイルオブジェクトからリクエストレコードのイテレータを生成"""
    #     reader = csv.DictReader(file)
    #     for line in reader:
    #         yield RequestRecord(app=line["app"], cc=line["cc"], rc=line["rc"])


class RequestAggregator:
    """リクエスト結果の集計を行うクラス"""

    def __init__(self):
        self.app_cc_stats: DefaultDict[Tuple[str, str], Dict[str, int]] = defaultdict(
            lambda: {"total": 0, "success": 0}
        )

    def process(self, records: Iterator[RequestRecord]) -> None:
        """リクエストレコードを集計"""
        for record in records:
            key = (record.app, record.cc)
            stats = self.app_cc_stats[key]
            stats["total"] += 1
            stats["success"] += record.is_success

    def get_app_cc_statistics(self) -> List[Dict]:
        """app/ccの組み合わせごとの統計を返す"""
        stats = []
        for (app, cc), counts in sorted(self.app_cc_stats.items()):
            success_rate = (
                (counts["success"] / counts["total"] * 100)
                if counts["total"] > 0
                else 0
            )
            stats.append(
                {
                    "app": app,
                    "cc": cc,
                    "total": counts["total"],
                    "success": counts["success"],
                    "success_rate": f"{success_rate:.2f}",
                }
            )
        return stats

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
