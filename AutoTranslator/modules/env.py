import os
import dotenv
from logging import DEBUG
from modules.log import get_logger

logger = get_logger(__name__)

# 設定をロードする変数
def load_env():
    # .envを取得
    path = dotenv.find_dotenv(".env")
    logger.debug(f"envファイルのパス: {path}")
    # .envから設定をロード
    dotenv.load_dotenv(path)
    result = dotenv.dotenv_values(path)

    return result