import json
import logging
import os
import traceback
from datetime import datetime
from typing import List

from exceptions import CollectionError
from exporters import CSVFormatter, StatisticsExporter
from file_collector import FileCollector
from models import RequestAggregator, RequestReader

BASE_DIR = ""

current_datetime = datetime.now()
current_date = current_datetime.strftime("%Y%m%d")
current_hhmm = current_datetime.strftime("%H%M")


class Main:
    def __init__(self):
        self._setup_logging()

    def _setup_logging(self):
        log_dir = os.path.join(BASE_DIR, "LOG")
        os.makedirs(log_dir, exist_ok=True)

        log_file = f"calc_rate_{current_date}_{current_hhmm}.log"
        log_path = os.path.join(log_dir, log_file)

        logging.basicConfig(
            level=logging.INFO,
            format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
            handlers=[
                logging.FileHandler(log_path, encoding="utf-8"),
                logging.StreamHandler(),  # コンソールにも出力
            ],
        )
        self.logger = logging.getLogger(__name__)
        self.logger.info(f"Logging initialized. Log file: {log_path}")

    def run(self, sftp_config_path):
        sftp_config = self._load_config(sftp_config_path)

        try:
            self.logger.info("Starting file collection")
            collected_files = self._collect_files(sftp_config)

            self.logger.info("Starting aggregate")
            summary_records = self._aggregate_records(collected_files)

            self.logger.info("Starting statistics export")
            app_cc_stats_path = os.path.join(
                os.path.join(BASE_DIR, "PM"),
                f"success_rate_summary_{current_date}{current_hhmm}.csv",
            )
            exporter = StatisticsExporter(CSVFormatter())
            exporter.export(summary_records, app_cc_stats_path)

            self.logger.info("Aggregate completed successfully")
        except Exception as e:
            self.logger.error(f"Unexpected failed: {e}")
            self.logger.error(traceback.format_exc())
            raise

    def _load_config(self, config_path):
        try:
            with open(config_path, "r", encoding="utf-8") as f:
                return json.load(f)
        except Exception as e:
            self.logger.error(f"Failed to load config: {e}")
            raise

    def _collect_files(self, sftp_config) -> List[str]:
        with FileCollector(sftp_config) as collector:
            for host, config in sftp_config.items():
                for remote_path in config["remote_paths"]:
                    local_dir = self._build_receive_dir_path(remote_path)
                    os.makedirs(local_dir, exist_ok=True)
                    try:
                        collector.collect_file(host, remote_path, local_dir)
                        self.logger.info(f"Collection successfully: {remote_path}")
                    except CollectionError as e:
                        self.logger.warning(f"Collection failed: {remote_path}: {e}")
                    except Exception as e:
                        self.logger.warning(f"Session error: {host}: {e}")
                        self.logger.debug("Detailed traceback:", exc_info=True)
                        break
        return collector.collected_files

    def _build_receive_dir_path(self, remote_path: str) -> str:
        base_dir = os.path.join(BASE_DIR, "RECEIVE", current_date, current_hhmm)
        child_dir = os.path.basename(os.path.dirname(remote_path))
        return os.path.join(base_dir, child_dir)

    def _aggregate_records(self, local_files):
        aggregator = RequestAggregator()
        for fp in local_files:
            try:
                with open(fp, "r", encoding="utf-8") as f:
                    records = RequestReader.from_textio(f)
                    aggregator.process(records)
                self.logger.info(f"Successfully aggregated file: {fp}")
            except IOError as e:
                self.logger.error(f"Failed to open file {fp}: {e}")
                continue
        return aggregator.format_summary()


if __name__ == "__main__":
    script_dir = os.path.dirname(os.path.abspath(__file__))
    config_dir = os.path.join(script_dir, "../config")
    sftp_config = os.path.join(config_dir, "sftp_config.json")

    manager = Main()
    manager.run(sftp_config)
