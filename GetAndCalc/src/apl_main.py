import json
import logging
from pathlib import Path

import paramiko

from .analyzer.exporters import CSVFormatter, StatisticsExporter
from .analyzer.models import RequestAggregator, RequestReader

# ロギングの設定
logging.basicConfig(
    level=logging.INFO, format="%(asctime)s - %(name)s - %(levelname)s - %(message)s"
)
logger = logging.getLogger(__name__)


class LogAnalyzer:
    """ログ分析の実行を制御するクラス"""

    def __init__(self, config_path: str):
        self.config = self._load_config(config_path)
        self._setup_directories()

    def _load_config(self, config_path: str) -> dict:
        """設定ファイルを読み込む"""
        try:
            with open(config_path, "r") as f:
                return json.load(f)
        except Exception as e:
            logger.error(f"Failed to load config: {e}")
            raise

    def _setup_directories(self) -> None:
        """入出力ディレクトリの準備"""
        Path(self.config["input_dir"]).mkdir(parents=True, exist_ok=True)
        Path(self.config["output_dir"]).mkdir(parents=True, exist_ok=True)

    def collect_files(self) -> None:
        """SFTPでファイルを収集"""
        try:
            transport = paramiko.Transport(
                (self.config["sftp_host"], self.config["sftp_port"])
            )
            transport.connect(
                username=self.config["sftp_user"], password=self.config["sftp_password"]
            )

            sftp = paramiko.SFTPClient.from_transport(transport)

            for remote_path in self.config["target_files"]:
                local_path = Path(self.config["input_dir"]) / Path(remote_path).name
                logger.info(f"Collecting {remote_path} to {local_path}")
                sftp.get(remote_path, str(local_path))

            sftp.close()
            transport.close()
        except Exception as e:
            logger.error(f"SFTP collection failed: {e}")
            raise

    def analyze(self) -> None:
        """ログの分析を実行"""
        try:
            aggregator = RequestAggregator()
            input_dir = Path(self.config["input_dir"])

            # CSVファイルの処理
            for csv_file in input_dir.glob("*.csv"):
                logger.info(f"Processing {csv_file}")
                records = RequestReader.from_csv(str(csv_file))
                aggregator.process(records)

            # 結果の出力
            exporter = StatisticsExporter(CSVFormatter())
            output_dir = Path(self.config["output_dir"])

            # app_stats_path = output_dir / "app_statistics.csv"
            # exporter.export(aggregator.get_app_statistics(), str(app_stats_path))
            # logger.info(f"App statistics exported to {app_stats_path}")

            app_cc_stats_path = output_dir / "app_cc_statistics.csv"
            exporter.export(aggregator.get_app_cc_statistics(), str(app_cc_stats_path))
            logger.info(f"App/CC statistics exported to {app_cc_stats_path}")

        except Exception as e:
            logger.error(f"Analysis failed: {e}")
            raise


def main():
    """メインの実行関数"""
    try:
        config_path = Path(__file__).parent.parent / "config" / "settings.json"
        analyzer = LogAnalyzer(str(config_path))

        logger.info("Starting file collection")
        analyzer.collect_files()

        logger.info("Starting analysis")
        analyzer.analyze()

        logger.info("Analysis completed successfully")
    except Exception as e:
        logger.error(f"Process failed: {e}")
        raise


if __name__ == "__main__":
    main()
