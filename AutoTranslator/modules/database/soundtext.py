import mariadb
import dotenv
import logging
import time
import sys
import os

parent_dir = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
sys.path.append(parent_dir)

import log

class SoundtextManager:
    def __init__(self, user, password, host, port, database, max_retries=3):

        self.logger = log.get_logger(__name__)

        self.db_config = {
            "user": user,
            "password": password,
            "host": host,
            "port": port,
        }
        self.database = database
        self.max_retries = max_retries
        self.conn = None
        self.cursor = None
        self.connect_db()

    def connect_db(self):
        """データベースに接続（存在しなければ作成)"""
        try:
            # まず通常の接続を試す
            self.conn = mariadb.connect(**self.db_config, database=self.database)
            self.cursor = self.conn.cursor()
            self.logger.info(f"MariaDBに接続しました（データベース: {self.database}）")

        except mariadb.Error as e:
            if "Unknown database" in str(e):
                self.logger.info("データベースを生成中")
                self.create_database()
            else:
                self.logger.error("データベース接続エラー: %s", e)
                self.conn = None
                self.cursor = None

    def create_database(self):
        """データベースを作成して再接続"""
        try:
            # データベースなしで接続（データベース作成のため）
            temp_conn = mariadb.connect(**self.db_config)
            temp_cursor = temp_conn.cursor()
            temp_cursor.execute(f"CREATE DATABASE {self.database}")
            temp_conn.commit()
            temp_cursor.close()
            temp_conn.close()
            self.logger.info(f"データベース '{self.database}' を作成しました")

            # 再接続
            self.connect_db()
        except mariadb.Error as e:
            self.logger.error(f"データベース作成エラー: {e}")

    def execute_query(self, query, params=None, fetch=False):
        """SQLクエリを実行し、必要に応じて結果を取得"""
        for attempt in range(1, self.max_retries + 1):
            try:
                if not self.conn or not self.cursor:
                    self.logger.info(f"データベースに再接続中... ({attempt}/{self.max_retries})")
                    self.connect_db()

                if not self.conn or not self.cursor:
                    raise mariadb.OperationalError("データベースに接続できません")

                self.cursor.execute(query, params or ())
                self.conn.commit()

                # `SHOW` クエリや `SELECT` の場合のみ fetch する
                if fetch:
                    return self.cursor.fetchall()

                return None

            except mariadb.OperationalError as e:
                self.logger.error("データベース接続エラー: %s", e)
                self.conn = None
                self.cursor = None
                time.sleep(1)
            except mariadb.Error as e:
                self.logger.error(f"クエリエラー: {e} \n クエリ: {query}")
                return None

        self.logger.error("リトライ回数を超過しました。クエリ実行を中止します。")
        return None

    def table_exists(self, table_name):
        """テーブルが存在するかチェック"""
        self.logger.debug(f"Checking table '{table_name}' exists...")
        result = self.execute_query(f"SHOW TABLES LIKE '{table_name}'", fetch=True)
        return bool(result)
    
    def create_table(self, server_id, columns):
        """""テーブルを作成"""
        self.logger.debug (f"Creating table '{server_id}'...")
        query = f"""
            CREATE TABLE `{server_id}` (
                {", ".join([f"{col[0]} {col[1]}" for col in columns])   }
            )
        """
        
        if self.execute_query(query):
            self.logger.info(f"テーブル '{server_id}' を作成しました")
    
    def init_server_dict(self, server_id):
        """サーバー用の辞書テーブルを準備"""
        self.logger.debug(f"Initializing dictionary table for server '{server_id}'...")
        if not self.table_exists(server_id):
            self.create_table(server_id, soundtext_settings)


    def get_dict(self, server_id):
        """サーバー用の辞書を取得"""
        self.logger.debug(f"Getting dictionary for server '{server_id}'...")
        self.init_server_dict(server_id)
        
        query = f"SELECT * FROM `{server_id}`"

        result = self.execute_query(query, fetch=True)

        return result if result else None
    
    def save_dict(self, server_id, settings):
        """サーバー用の辞書を保存"""
        self.logger.debug(f"Saving dictionary for server '{server_id}'...")
        self.init_server_dict(server_id)

        query = f"""
            INSERT INTO `{server_id}` ({", ".join(settings.keys())})
            VALUES ({", ".join(["%s"] * len(settings))})
            ON DUPLICATE KEY UPDATE {", ".join([f"{k}=%s" for k in settings.keys()])} 
        """
        params = list(settings.values()) + list(settings.values())

        self.execute_query(query, params)

    def close(self):
        """データベース接続を閉じる"""
        if self.conn:
            self.cursor.close()
            self.conn.close()
            print("データベース接続を閉じました")


# ==============================
# 設定リスト
# ==============================
soundtext_settings = [
    ("id", "INTEGER AUTO_INCREMENT PRIMARY KEY"),
    ("word", "TEXT NOT NULL UNIQUE"),
    ("file", "TEXT NOT NULL"),
    ("user_id", "BIGINT NOT NULL"),
    ("updated_at", "DATETIME DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP"),
]

# ==============================
# 使い方
# ==============================
# if __name__ == "__main__":

#     dotenv.load_dotenv()
#     # DB接続情報
#     db = DictionaryManager(
#         user=os.getenv("DB_USER"),
#         password=os.getenv("DB_PASS"),
#         host=os.getenv("DB_HOST"),
#         port=3306,
#         database="test2"
#     )

#     db.save_dict(114514, {
#         "word": "test",
#         "yomi": "てすと",
#         "user_id": 1234567890,
#     })

#     print(db.get_dict(114514))

#     # 接続を閉じる
#     db.close()
