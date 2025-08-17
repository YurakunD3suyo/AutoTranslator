import os
import sys
import time
from modules.env import load_env
from modules.log import get_logger
from discord import Intents 
from discord.ext import commands
from logging import Logger, DEBUG
from os import getenv

# ディレクトリの取得
ROOT_DIR = os.path.dirname(__file__)

# bot用ロガーを作成
logger: Logger = get_logger(__name__)
if not logger:
    print("ロガーの生成に失敗しました。botの情報は出力できません。")

# log
logger.info("botを起動中...")

# インテンツの生成
intents = Intents.all()
#log
logger.debug("Intentsの設定完了")

# 設定のインポート
settings = load_env()
token = settings["TOKEN"]
prefix = settings["PREFIX"]

if token is None or prefix is None:
    logger.error(".envが正しく設定されていません。 詳細はREADME.txtをご覧ください。")
    sys.exit()

#log
logger.debug("設定ロード完了")

# Botクラスを作成
bot = commands.Bot(intents=intents, command_prefix=prefix)
#log
logger.debug("botクラス生成完了")

#ツリーを生成
tree = bot.tree
logger.debug("ツリー生成完了")

@bot.event
async def on_ready():
    loaded_cogs = 0
    exceptions_cogs = 0

    # cogファイルを読み込む(cogフォルダ内すべてのフォルダを検索)
    for dirpath, _, files in os.walk(os.path.join(ROOT_DIR, "cogs")):
        for file in files:
            name, ext = os.path.splitext(file)
            if ext == ".py":
                path = os.path.relpath(os.path.join(dirpath, file), ROOT_DIR)
                module = path.replace(os.sep, ".")[:-3]
                try:
                    await bot.load_extension(module)
                    logger.debug(f'読み込み完了: {module}')
                    loaded_cogs += 1
                except Exception as e:
                    logger.exception(f'読み込み失敗: {module}')
                    logger.exception(e)
                    exceptions_cogs += 1
            # pipでインストールされているものはその名前のファイルで検出
            elif not ext:
                try: 
                    await bot.load_extension(name)
                    logger.debug(f'読み込み完了: {name}')
                    loaded_cogs += 1
                except Exception as e:
                    logger.exception(f'読み込み失敗: {name}')
                    logger.exception(e)
                    exceptions_cogs += 1
    logger.info(f"cogを読み込みました(読み込み済: {loaded_cogs}、 エラー: {exceptions_cogs})")
    logger.debug("ツリーを同期します")
    await tree.sync()
    logger.info(f"起動処理完了 起動しました({bot.user})")

# 実行
bot.run(token)
    