# クラス図

```mermaid
classDiagram
    class Main {
        +run(sftp_config_path)
        -_setup_logging()
        -_load_config(config_path)
        -_collect_files(sftp_config)
        -_aggregate_records(local_files)
        -_export_csv(summary_records)
    }

    class FileCollector {
        +collect_file(host, remote_path, local_dir)
        -_sftp_session(host)
        -_create_ssh_session(host)
        -_close_all_sessions()
    }

    class RecordReader {
        +from_textio(textio) $
    }

    class AggregationRecord {
        +endtime: str
        +site: str
        +app: str
        +is_success: int
    }

    class RecordAggregator {
        +site_app_stats: DefaultDict
        +process(records)
        +format_summary()
        -summarize()
        -_calculate_sr(total, success)
    }

    class StatisticsFormatter {
        <<abstract>>
        +format(statistics) *
    }

    class CSVFormatter {
        +format(statistics)
    }

    class JSONFormatter {
        +format(statistics)
    }

    class StatisticsExporter {
        +export(statistics, output_path)
    }

    class AuthenticationError {
        <<exception>>
    }

    class CollectionError {
        <<exception>>
    }

    StatisticsFormatter <|-- CSVFormatter: implements
    StatisticsFormatter <|-- JSONFormatter: implements
    StatisticsExporter --> StatisticsFormatter: uses
    RecordAggregator --> AggregationRecord: processes
    RecordReader --> AggregationRecord: creates
    Main --> FileCollector: uses
    Main --> RecordAggregator: uses
    Main --> StatisticsExporter: uses
```
