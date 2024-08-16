import fnmatch
import logging
import os
from datetime import datetime as dt

_current_dir = os.path.dirname(os.path.abspath(__file__))
_dir_base = os.path.join(_current_dir, "../log")
_log_dir = None
_initialized = False


def initialize_log_dir():
    global _initialized, _log_dir
    if not _initialized:
        _log_dir = os.path.join(_dir_base, dt.now().strftime("%Y%m%d"))
        _initialized = True


def setup_logger_common():
    initialize_log_dir()

    logger = logging.getLogger("common")
    logger.setLevel(logging.DEBUG)

    log_file = f"COMMON_{dt.now().strftime('%Y%m%d')}.log"
    log_path = os.path.join(_log_dir, log_file)
    file_handler = logging.FileHandler(log_path)

    formatter = logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s')
    file_handler.setFormatter(formatter)

    logger.addHandler(file_handler)

    return logger


logger_common = setup_logger_common()


def build_logger_app(host_name):
    logger = logging.getLogger(host_name)
    logger.setLevel(logging.DEBUG)

    log_file = f"{host_name}_{dt.now().strftime('%Y%m%d%H%M')}.log"
    log_path = os.path.join(_log_dir, log_file)
    file_handler = logging.FileHandler(log_path)

    formatter = logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s')
    file_handler.setFormatter(formatter)

    logger.addHandler(file_handler)

    return logger
