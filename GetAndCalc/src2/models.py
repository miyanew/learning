import csv
from collections import defaultdict
from datetime import datetime, timedelta
from typing import DefaultDict, Dict, Iterator, List, TextIO, Tuple

CSV_HEADER_END_TIME = "End Time Local"
CSV_HEADER_SITE = "Site"
CSV_HEADER_APP = "APP"
CSV_HEADER_RC = "RC"
DEFAULT_SUCCESS_RATE = 100.00


class AggregationRecord:
    """集計対象の1レコードを表現するデータクラス"""

    APP_SUCCESS_RESULTS = {
        "app1": ["PROC_SUCCESS", "PROC_OK"],
        "app2": ["PROC_COMPLETED"],
    }
    APP_NAMES = list(APP_SUCCESS_RESULTS.keys())

    def __init__(self, endtime: str, site: str, app: str, rc: str):
        self.endtime = endtime
        self.site = site
        self.app = app
        self.is_success = rc in self.APP_SUCCESS_RESULTS.get(self.app, [])


class RecordReader:
    """CSVからレコードを読み出すクラス"""

    @staticmethod
    def from_textio(textio: TextIO) -> Iterator[AggregationRecord]:
        """
        ファイルオブジェクトからレコードのイテレータを生成

        - ヘッダに取得対象キーの一部でも欠損する場合は処理しない
        - データ行にフォーマット不正を含むレコード群は処理しない
        """
        reader = csv.DictReader(textio)
        RecordReader.validate_lines(reader)

        textio.seek(0)  # ファイルポインタを先頭に戻す
        reader = csv.DictReader(textio)
        for line in reader:
            yield AggregationRecord(
                endtime=RecordReader.normalize_time(line[CSV_HEADER_END_TIME]),
                site=line[CSV_HEADER_SITE],
                app=line[CSV_HEADER_APP],
                rc=line[CSV_HEADER_RC],
            )

    @staticmethod
    def validate_lines(reader: csv.DictReader) -> None:
        """
        各行を検証して不正なフォーマットがあれば例外を発生させる

        Raises:
            ValueError: 必要なフィールドが欠けている場合
        """
        required_fields = [
            CSV_HEADER_END_TIME,
            CSV_HEADER_SITE,
            CSV_HEADER_APP,
            CSV_HEADER_RC,
        ]

        header = reader.fieldnames
        missing_headers = [field for field in required_fields if field not in header]
        if missing_headers:
            raise ValueError(f"Missing required headers: {', '.join(missing_headers)}")

        line_count = 0
        for line_num, line in enumerate(reader):
            line_count += 1
            missing_fields = [field for field in required_fields if not line.get(field)]
            if missing_fields:
                raise ValueError(
                    f"Missing fields Line{line_num + 1}: {', '.join(missing_fields)}"
                )

        if line_count == 0:
            raise ValueError("No data rows found in the file")

    @staticmethod
    def normalize_time(time_str: str) -> str:
        """
        秒を基準に時刻を分単位で丸める。
        30秒未満は切り捨て、30秒以上は切り上げ。
        """
        dt = datetime.strptime(time_str, "%Y/%m/%d %H:%M:%S")
        if dt.second >= 30:
            dt += timedelta(minutes=1)
        dt = dt.replace(second=0)
        return dt.strftime("%Y/%m/%d %H:%M:%S")

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


class RecordAggregator:
    """レコードの集計を行うクラス"""

    def __init__(self):
        self.site_app_stats: DefaultDict[
            Tuple[str, str, str], Dict[str, int]
        ] = defaultdict(lambda: {"total": 0, "success": 0})

    def process(self, records: Iterator[AggregationRecord]) -> None:
        """レコードを数え上げる"""
        for record in records:
            key = (record.endtime, record.site, record.app)
            stats = self.site_app_stats[key]
            stats["total"] += 1
            stats["success"] += record.is_success

    def summarize(self) -> List[Dict]:
        """レコードを集計する"""
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

        site_stats = {}
        for site_app_stat in site_app_stats:
            site = site_app_stat["Site"]
            app = site_app_stat["App"]
            sr = self._calculate_sr(
                site_app_stat["TotalCount"], site_app_stat["SuccessCount"]
            )

            site_stat = site_stats.get(site)
            if site_stat is None:
                site_stats[site] = {
                    "Site": site,
                    "EndTime": site_app_stat["EndTime"],
                }

            site_stats[site].update(
                {
                    f"{app}_Total": site_app_stat["TotalCount"],
                    f"{app}_Success": site_app_stat["SuccessCount"],
                    f"{app}_SR": sr,
                }
            )

        header = self._generate_header()

        # ヘッダーに基づいて各行を生成し、存在しないキーにはデフォルト値をセット
        result = []
        for stats in site_stats.values():
            row = {}
            for col in header:
                if col.endswith("_SR"):
                    row[col] = format(stats.get(col, DEFAULT_SUCCESS_RATE), ".2f")
                else:
                    row[col] = stats.get(col, "0")
            result.append(row)
        return result

    def _calculate_sr(self, total: int, success: int) -> float:
        """成功率を計算して浮動小数点数で返す"""
        return success / total * 100 if total else DEFAULT_SUCCESS_RATE

    def _generate_header(self):
        """出力するCSVのヘッダーを生成する"""
        ini_header = ["EndTime", "Site"]
        app_order = AggregationRecord.APP_NAMES
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
