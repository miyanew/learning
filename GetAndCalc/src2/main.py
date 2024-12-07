import json
import logging
import os
from datetime import datetime
from typing import Dict, List

from exporters import CSVFormatter, StatisticsExporter
from file_collector import FileCollector
from models import RecordAggregator, RecordReader

from exceptions import CollectionError

BASE_DIR = ""

start_datetime = datetime.now()
start_date = start_datetime.strftime("%Y%m%d")
start_hhmm = start_datetime.strftime("%H%M")


class Main:
    """
    データ収集、集計、エクスポートを行うメイン処理クラス。
    """

    def __init__(self):
        self.logger = logging.getLogger(__name__)
        self.log_file_path = self._get_log_file_path()
        self._setup_logging()
        self._setup_paramiko_logging()

    def _get_log_file_path(self) -> str:
        """
        ログファイルのパスを生成する。
        """
        log_dir = os.path.join(BASE_DIR, "LOG")
        os.makedirs(log_dir, exist_ok=True)

        log_file = f"calc_rate_{start_date}_{start_hhmm}.log"
        return os.path.join(log_dir, log_file)

    def _setup_logging(self) -> None:
        """
        アプリケーション全体のログ設定を行う。
        """
        logging.basicConfig(
            level=logging.INFO,
            format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
            handlers=[
                logging.FileHandler(self.log_file_path, encoding="utf-8"),
                logging.StreamHandler(),  # コンソールにも出力
            ],
        )

    def _setup_paramiko_logging(self) -> None:
        """
        Paramikoログを親ロガーに伝播させない。無視する
        """
        paramiko_logger = logging.getLogger("paramiko")
        paramiko_logger.setLevel(logging.ERROR)
        paramiko_null_handler = logging.NullHandler()
        paramiko_logger.addHandler(paramiko_null_handler)
        paramiko_logger.propagate = False

    def run(self, sftp_config_path: str) -> None:
        """
        メイン処理を実行する。

        Raises:
            Exception: 処理中に発生した予期せぬエラー
        """
        try:
            self.logger.info("Starting config load")
            sftp_config = self._load_config(sftp_config_path)

            self.logger.info("Starting file collection")
            collected_files = self._collect_files(sftp_config)
            if not collected_files:
                self.logger.warning("No files were collected")
                return

            self.logger.info("Starting aggregate")
            summary_records = self._aggregate_records(collected_files)
            if not summary_records:
                self.logger.warning("No properly formatted records found")
                return

            self.logger.info("Starting statistics export")
            self._export_csv(summary_records)

            self.logger.info("Aggregate completed successfully")
        except Exception as e:
            self.logger.error(f"Unexpected error: {e}", exc_info=True)

    def _load_config(self, config_path: str) -> Dict:
        """
        設定ファイルを読み込む。

        Raises:
            json.JSONDecodeError: JSON形式が不正な場合
            FileNotFoundError: 設定ファイルが存在しない場合
        """
        with open(config_path, "r", encoding="utf-8") as f:
            return json.load(f)

    def _collect_files(self, sftp_config: Dict) -> List[str]:
        """
        SFTPサーバーからファイルを収集する。
        """
        with FileCollector(sftp_config) as collector:
            for host, config in sftp_config.items():
                for remote_path in config["remote_paths"]:
                    local_dir = self._build_receive_dir_path(remote_path)
                    os.makedirs(local_dir, exist_ok=True)
                    try:
                        collector.collect_file(host, remote_path, local_dir)
                        self.logger.info(f"Collection successfully: {remote_path}")
                    except ConnectionError as e:
                        self.logger.warning(str(e))
                        break
                    except CollectionError as e:
                        self.logger.warning(str(e))
        return collector.collected_files

    def _build_receive_dir_path(self, remote_path: str) -> str:
        """
        ローカルの受信ディレクトリパスを構築する。
        """
        base_dir = os.path.join(BASE_DIR, "INPUT", start_date, start_hhmm)
        child_dir = os.path.basename(os.path.dirname(remote_path))
        return os.path.join(base_dir, child_dir)

    def _aggregate_records(self, local_files: List[str]) -> List[Dict]:
        """
        収集したファイルからレコードを集計する。
        """
        aggregator = RecordAggregator()
        for fp in local_files:
            try:
                with open(fp, "r", encoding="utf-8") as f:
                    records = RecordReader.from_textio(f)
                    aggregator.process(records)
                self.logger.info(f"Successfully aggregated file: {fp}")
            except OSError as e:
                self.logger.warning(f"Failed to open file {fp}: {e}")
            except ValueError as e:
                self.logger.warning(f"Invalid format file, nocounted {fp}: {e}")
            except Exception as e:
                self.logger.warning(f"Failed aggregate {fp}: {e}")
        return aggregator.format_summary()

    def _export_csv(self, summary_records: List[Dict]) -> None:
        """
        集計結果をCSVファイルにエクスポートする。

        Raises:
            FileWriteError: ファイル書き込みエラー
        """

        stats_path = os.path.join(
            os.path.join(BASE_DIR, "OUTPUT"),
            f"success_rate_summary_{start_date}{start_hhmm}.csv",
        )
        exporter = StatisticsExporter(CSVFormatter())
        exporter.export(summary_records, stats_path)
        self.logger.info(f"Exported successfully: {stats_path}")


if __name__ == "__main__":
    script_dir = os.path.dirname(os.path.abspath(__file__))
    config_dir = os.path.join(script_dir, "../config")
    sftp_config = os.path.join(config_dir, "sftp_config.json")

    manager = Main()
    manager.run(sftp_config)
