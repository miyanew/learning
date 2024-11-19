```Mermaid
classDiagram
    class Main {
        +run(sftp_config_path)
        -_setup_logging()
        -_load_config(config_path)
        -_collect_files(sftp_config)
        -_build_receive_dir_path(remote_path)
    }

    class FileCollector {
        +collect_file(host, remote_path, local_dir)
        -_sftp_session(host)
        -_create_ssh_session(host)
    }

    class RequestReader {
        +from_file(file) $
    }

    class AggregationRecord {
        +app: str
        +cc: str
        +is_success: bool
    }

    class RequestAggregator {
        +app_cc_stats: DefaultDict
        +process(records)
        +summarize()
        -_calculate_success_rate(total, success)
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
    RequestAggregator --> AggregationRecord: processes
    RequestReader --> AggregationRecord: creates
    Main --> FileCollector: uses
    Main --> RequestAggregator: uses
    Main --> StatisticsExporter: uses
```