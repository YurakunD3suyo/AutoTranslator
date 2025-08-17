import logging

LEVEL = logging.DEBUG

# ロガー設定関数
def get_logger(name):
    # 各モジュールからの名前をロガー名に使用
    logger = logging.getLogger(name)
    # 重複を避けるために、ハンドラが未設定の場合のみ追加
    if not logger.hasHandlers():
        logger.setLevel(LEVEL)
        handler = logging.StreamHandler()
        formatter = logging.Formatter('[%(asctime)s] [%(levelname)s] (%(name)s) -> %(message)s', datefmt='%Y-%m-%d %H:%M:%S')
        handler.setFormatter(formatter)
        logger.addHandler(handler)
    return logger
