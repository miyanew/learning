import json
import logging
import os
import traceback
from datetime import datetime

BASE_DIR = ""

from exceptions import CollectionError

from .analyzer.exporters import CSVFormatter, StatisticsExporter
from .analyzer.models import RequestAggregator, RequestReader
from .collecter.file_collecter import FileCollector


class Main:
    def __init__(self, config_path):
        self.ssh_config = self._load_config(config_path)
        self.collector = FileCollector(self.ssh_config)
        self._setup_logging()

    def _load_config(self, config_path):
        try:
            with open(config_path, "r", encoding="utf-8") as f:
                return json.load(f)
        except Exception as e:
            print(f"Failed to load config: {e}")  # ログ設定前なのでprintを使用
            raise

    def _setup_logging(self):
        log_dir = os.path.join(BASE_DIR, "LOG")
        os.makedirs(log_dir, exist_ok=True)

        log_file = os.path.join(
            log_dir, f"calc_rate_{datetime.now().strftime('%Y%m%d_%H%M00')}.log"
        )

        logging.basicConfig(
            level=logging.INFO,
            format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
            handlers=[
                logging.FileHandler(log_file, encoding="utf-8"),
                logging.StreamHandler(),  # コンソールにも出力
            ],
        )
        self.logger = logging.getLogger(__name__)
        self.logger.info(f"Logging initialized. Log file: {log_file}")

    def run(self, sftp_config_path):
        try:
            self.logger.info("Starting directory created/confirmed")
            self._setup_directories()

            self.logger.info("Starting file collection")
            sftp_config = self._load_config(sftp_config_path)
            local_paths = self.collector.collect_files(sftp_config)

            self.logger.info("Starting analysis")
            self.analyze(local_paths)

            self.logger.info("Analysis completed successfully")
        except CollectionError as e:
            self.logger.error(f"SFTP collection failed: {e}")
            self.logger.debug("Detailed traceback:", exc_info=True)
            raise
        except Exception as e:
            self.logger.error(f"Process failed: {e}")
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

    def analyze(self, filepaths):
        try:
            aggregator = RequestAggregator()
            for fp in filepaths:
                self.logger.info(f"Processing {fp}")
                records = RequestReader.from_csv(fp)
                aggregator.process(records)

            exporter = StatisticsExporter(CSVFormatter())
            output_dir = os.path.join(BASE_DIR, "PM")

            app_cc_stats_path = os.path.join(output_dir, "app_cc_statistics.csv")
            exporter.export(aggregator.get_app_cc_statistics(), app_cc_stats_path)
            self.logger.info(f"App/CC statistics exported to {app_cc_stats_path}")
        except Exception as e:
            self.logger.error(f"Analysis failed: {e}")
            raise


if __name__ == "__main__":
    script_dir = os.path.dirname(os.path.abspath(__file__))
    config_dir = os.path.join(script_dir, "../config")
    ssh_config = os.path.join(config_dir, "ssh_host.json")
    sftp_config = os.path.join(config_dir, "sftp_file.json")

    manager = Main(ssh_config)
    manager.run(sftp_config)
