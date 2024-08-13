import logging

def setup_logger(name, normal_log_file, error_log_file, level=logging.INFO):
    # 共通のフォーマッタ
    formatter = logging.Formatter('%(asctime)s %(levelname)s %(message)s')

    # 正常系ログのハンドラ
    normal_handler = logging.FileHandler(normal_log_file)
    normal_handler.setFormatter(formatter)
    normal_handler.setLevel(logging.INFO)

    # 異常系（エラー）ログのハンドラ
    error_handler = logging.FileHandler(error_log_file)
    error_handler.setFormatter(formatter)
    error_handler.setLevel(logging.ERROR)

    # ロガーの設定
    logger = logging.getLogger(name)
    logger.setLevel(level)
    logger.addHandler(normal_handler)
    logger.addHandler(error_handler)

    return logger

# 共通のロガーを作成
common_logger = setup_logger('common_logger', 'normal.log', 'error.log')
