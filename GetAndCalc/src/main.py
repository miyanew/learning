import json
import logging
import os
import sys
import traceback
from datetime import datetime

project_root = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
sys.path.insert(0, project_root)
from src.analyzer.exporters import CSVFormatter, StatisticsExporter
from src.analyzer.models import RequestAggregator, RequestReader
from src.collecter.file_collecter import FileCollector
from src.exceptions import CollectionError

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

    def run(self, config_path, sftp_config_path):
        try:
            self.logger.info("Starting directory created/confirmed")
            self._setup_directories()

            self.logger.info("Starting file collection")
            ssh_config = self._load_config(config_path)
            sftp_config = self._load_config(sftp_config_path)

            collector = FileCollector(ssh_config)
            local_paths = collector.collect_files(sftp_config)

            self.logger.info("Starting aggregate")
            aggregator = RequestAggregator()
            for fp in local_paths:
                try:
                    with open(fp, "r", encoding="utf-8") as f:
                        records = RequestReader.from_file(f)
                        aggregator.process(records)
                    self.logger.info(f"Successfully processed file: {fp}")
                except IOError as e:
                    self.logger.error(f"Failed to open file {fp}: {e}")
                    continue

            app_cc_stats_path = os.path.join(
                os.path.join(BASE_DIR, "PM"),
                f"success_rate_summary_{current_date}_{current_hhmm}.csv",
            )
            self.logger.info(f"App/CC statistics exporting to {app_cc_stats_path}")
            exporter = StatisticsExporter(CSVFormatter())
            exporter.export(aggregator.summarize(), app_cc_stats_path)

            self.logger.info("Aggregate completed successfully")
        except CollectionError as e:
            self.logger.error(f"SFTP collection failed: {e}")
            self.logger.debug("Detailed traceback:", exc_info=True)
            raise
        except Exception as e:
            self.logger.error(f"Unexpected failed: {e}")
            self.logger.error(traceback.format_exc())
            raise

    def _setup_directories(self):
        dirs = [
            os.path.join(BASE_DIR, "INPUT"),
            os.path.join(BASE_DIR, "PM"),
        ]
        for dir_path in dirs:
            os.makedirs(dir_path, exist_ok=True)
            self.logger.info(f"Directory created/confirmed: {dir_path}")

    def _load_config(self, config_path):
        try:
            with open(config_path, "r", encoding="utf-8") as f:
                return json.load(f)
        except Exception as e:
            self.logger.error(f"Failed to load config: {e}")
            raise


if __name__ == "__main__":
    script_dir = os.path.dirname(os.path.abspath(__file__))
    config_dir = os.path.join(script_dir, "../config")
    ssh_config = os.path.join(config_dir, "ssh_host.json")
    sftp_config = os.path.join(config_dir, "sftp_file.json")

    manager = Main()
    manager.run(ssh_config, sftp_config)
