from .logger_config import common_logger

# Logging HOWTO
# https://docs.python.org/ja/3/howto/logging.html#logging-basic-tutorial

def function_a():
    common_logger.info("This is a normal log from lib1")
    common_logger.error("This is an error log from lib1")
    return True
