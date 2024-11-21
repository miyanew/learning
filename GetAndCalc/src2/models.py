import csv
from collections import defaultdict
from typing import DefaultDict, Dict, Iterator, List, TextIO, Tuple

CSV_HEADER_END_TIME = "End Time Local"
CSV_HEADER_SITE = "Site"
CSV_HEADER_APP = "APP"
CSV_HEADER_RC = "RC"

SUCCESS_CASE = "PROC_SUCCESS"


class AggregationRecord:
    """集計対象の1レコードを表現するデータクラス"""

    def __init__(self, endtime: str, site: str, app: str, rc: str):
        self.endtime = endtime
        self.site = site
        self.app = app
        self.is_success = rc == SUCCESS_CASE


class RequestReader:
    # """CSVからリクエストレコードを読み出すクラス"""
    # @staticmethod
    # def from_csv(file_path: str) -> Iterator[AggregationRecord]:
    #     """CSVファイルからリクエストレコードのイテレータを生成"""
    #     with open(file_path, "r", encoding="utf-8") as f:
    #         reader = csv.DictReader(f)
    #         for line in reader:
    #             yield AggregationRecord(
    #                 endtime=line[CSV_HEADER_END_TIME], 
    #                 site=line[CSV_HEADER_SITE],
    #                 app=line[CSV_HEADER_APP], 
    #                 rc=line[CSV_HEADER_RC],
    #             )

    @staticmethod
    def from_file(file: TextIO) -> Iterator[AggregationRecord]:
        """ファイルオブジェクトからリクエストレコードのイテレータを生成"""
        reader = csv.DictReader(file)
        for line in reader:
            yield AggregationRecord(
                endtime=line[CSV_HEADER_END_TIME], 
                site=line[CSV_HEADER_SITE],
                app=line[CSV_HEADER_APP], 
                rc=line[CSV_HEADER_RC],
            )


class RequestAggregator:
    """リクエスト結果の集計を行うクラス"""

    def __init__(self):
        self.site_app_stats: DefaultDict[Tuple[str, str, str], Dict[str, int]] = defaultdict(
            lambda: {"total": 0, "success": 0}
        )

    def process(self, records: Iterator[AggregationRecord]) -> None:
        """リクエストの統計を集計"""
        for record in records:
            key = (record.endtime, record.site, record.app)
            stats = self.site_app_stats[key]
            stats["total"] += 1
            stats["success"] += record.is_success

    def summarize(self) -> List[Dict]:
        """ "集計結果のサマリーを返す"""
        stats = []
        for (endtime, site, app), counts in sorted(self.site_app_stats.items()):
            stats.append(
                {
                    "EndTime": endtime,
                    "Site": site,
                    "App": app,
                    "TotalCount": counts["total"],
                    "SuccessCount": counts["success"],
                }
            )
        return stats
    
    def format_summary(self) -> List[Dict]:
        """集計結果のサマリーをCSV出力用に整形する"""
        site_app_stats = self.summarize()
        site_stats = defaultdict(lambda: defaultdict(int))

        for stat in site_app_stats:
            site = stat["Site"]
            app = stat["App"]
            sr = f"{self._calculate_sr(stat["TotalCount"], stat["SuccessCount"]):.2f}"

            site_stats[site]["Site"] = site
            site_stats[site]["EndTime"] = stat["EndTime"]
            site_stats[site][f"{app}_Total"] = stat["TotalCount"]
            site_stats[site][f"{app}_Success"] = stat["SuccessCount"]
            site_stats[site][f"{app}_SR"] = sr
        
        header = self._generate_header()
        result = []

        return result



    def _calculate_sr(self, total: int, success: int) -> float:
        """成功率を計算して浮動小数点数で返す"""
        return success / total * 100 if total else 0

    def _generate_header(self):
        """出力するCSVのヘッダーを生成する"""
        ini_header = ["EndTime", "Site"]
        app_order = ["app1", "app2", "app3", "app4", "app5", "app6"]
        metric_order = ["Total", "Success", "SR"]
        cols_metric = [f"{app}_{met}" for app in app_order for met in metric_order]
        return ini_header + cols_metric

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
