import mariadb
import dotenv
import time
import sys
import os

parent_dir = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
sys.path.append(parent_dir)

import log

class GeneralManager:
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
        """データベースに接続（存在しなければ作成）"""
        try:
            # まず通常の接続を試す
            self.conn = mariadb.connect(**self.db_config, database=self.database)
            self.cursor = self.conn.cursor()
            self.logger.info(f"MariaDBに接続しました（データベース: {self.database}）")
        except mariadb.Error as e:
            if "Unknown database" in str(e):
                self.logger.info(f"データベース '{self.database}' が存在しません。作成します...")
                self.create_database()
            else:
                self.logger.error(f"データベース接続エラー: {e}")
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
                self.logger.error(f"接続エラー: {e}")
                self.conn = None
                self.cursor = None
                time.sleep(1)
            except mariadb.Error as e:
                self.logger.exception(f"SQLエラー: {e}")
                return None

        print("リトライ回数を超過しました。クエリ実行を中止します。")
        return None

    def table_exists(self, table_name: str) -> bool:
        """テーブルが存在するかチェック"""
        self.logger.debug(f"Checking table '{table_name}' exists...")
        result = self.execute_query(f"SHOW TABLES LIKE '{table_name}'", fetch=True)
        return bool(result)

    def get_setting(self, table_name: str, primary_id: int, name: str) -> any:
        """データベースから設定を取得し、存在しなければデフォルト値で作成"""
        self.logger.debug(f"Getting setting '{name}' from table '{table_name}' for ID {primary_id}...")

        # クエリを動的に作成
        query = f"SELECT {name} FROM {table_name} WHERE id = %s"
        
        # クエリ実行
        result = self.execute_query(query, [primary_id], fetch=True)

        if result:
            return result[0][0]  # 1列目の値を返す

        # 設定がない場合、デフォルト値で作成
        self.logger.info(f"Setting '{name}' not found for ID {primary_id}. Creating with default value...")
        self.save_setting(table_name, primary_id, None)

        # 再取得
        result = self.execute_query(query, [primary_id], fetch=True)
        return result[0][0] if result else None  # 念のためチェック


    def save_setting(self, table_name: str, primary_id: int, settings: any):
        """データベースへ設定を保存（既存なら更新、なければ追加）"""
        """例: settings = {"welcome_message": 1234567890, "url_to_embed": 1}"""

        if settings:  # 設定データがある場合
            self.logger.debug(f"Saving settings for ID {primary_id} in table '{table_name}'...")
            placeholders = ", ".join([f"{k}=%s" for k in settings.keys()])
            query = f"""
                INSERT INTO {table_name} (id, {", ".join(settings.keys())})
                VALUES (%s, {", ".join(["%s"] * len(settings))})
                ON DUPLICATE KEY UPDATE {", ".join([f"{k}=%s" for k in settings.keys()])} 
            """
            values = [primary_id] + list(settings.values()) + list(settings.values())
        else:  # 設定データが空の場合、IDのみでINSERT
            self.logger.debug(f"Creating the table '{table_name}'...")
            query = f"""
                INSERT INTO {table_name} (id) VALUES (%s)
            """
            values = [primary_id]

        self.execute_query(query, values)

    def get_existing_columns(self, table_name):
        """データベースから既存のカラムリストを取得"""
        self.logger.debug(f"Getting existing columns for table '{table_name}'...")
        result = self.execute_query(f"SHOW COLUMNS FROM {table_name}", fetch=True)
        return {row[0]: row[1] for row in result} if result else {}

    def create_or_update_table(self, table_name: str, columns: list[tuple[str, str]]):
        """テーブル作成 & スキーマ更新（型が異なる場合はログのみ出力）"""

        if not self.table_exists(table_name):
            self.logger.info(f"テーブル {table_name} を作成中...")
            create_query = f"""
                CREATE TABLE {table_name} (
                    {", ".join([f"{col[0]} {col[1]}" for col in columns])}
                )
            """
            self.execute_query(create_query)
            return

        existing_columns = self.get_existing_columns(table_name)
        new_columns = {col[0]: col[1] for col in columns}

        for column, new_col_type in new_columns.items():
            if column not in existing_columns:
                self.logger.info(f"カラム追加: {column} {new_col_type}")
                self.execute_query(f"ALTER TABLE {table_name} ADD COLUMN {column} {new_col_type}")

    def close(self):
        """データベース接続を閉じる"""
        if self.conn:
            self.cursor.close()
            self.conn.close()
            self.logger.info("データベース接続を閉じました")


# ==============================
# 設定リスト
# ==============================
other_settings = [
    ("id", "BIGINT PRIMARY KEY"),  # PRIMARY KEY
    ("welcome_message", "BIGINT DEFAULT NULL"),     # [Welcome Message ID] Null or ID Default Null
    ("url_to_embed", "TINYINT NOT NULL DEFAULT 0"),   # [URL to Embed (Discord)] 0 or 1 Default 0
]

# ==============================
# 使い方
# ==============================
# if __name__ == "__main__":

#     dotenv.load_dotenv()
#     # DB接続情報
#     db = GeneralManager(
#         user=os.getenv("DB_USER"),
#         password=os.getenv("DB_PASS"),
#         host=os.getenv("DB_HOST"),
#         port=3306,
#         database="test"
#     )

#     db.create_or_update_table("tts_settings", tts_settings)
#     db.create_or_update_table("user_settings", user_settings)

#     print(type(db.get_setting("tts_settings", 1, "speed")))

#     # 接続を閉じる
#     db.close()
