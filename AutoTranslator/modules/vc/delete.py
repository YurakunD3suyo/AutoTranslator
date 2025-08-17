import threading
import time
import os
import sys

from modules.log import get_logger

# loggerの設定
logger = get_logger(__name__)

def delete_file_latency(file_name, latency):
    task = threading.Thread(target=_delete_file_latency, args=(file_name, latency))
    task.start()

def _delete_file_latency(file_name, latency):
    try:
        time.sleep(latency+2.0)
        os.remove(file_name)
        
    except Exception as e:
        exception_type, exception_object, exception_traceback = sys.exc_info()
        line_no = exception_traceback.tb_lineno
        filename = exception_traceback.tb_frame.f_code.co_filename
        logger.error(f"ファイル削除エラー: {e} {filename} {line_no}")