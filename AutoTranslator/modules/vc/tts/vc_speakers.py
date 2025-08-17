import requests
import os

from discord import app_commands
from modules.log import get_logger
from discord.app_commands import Choice
from dotenv import load_dotenv

VC_HOST = "localhost"
VC_PORT = 50021

class VoiceVoxSpeaker:
    def __init__(self, name: str, uuid: int, styles: list = []):
        self.name = name
        self.uuid = uuid
        self.styles = styles if styles else []

    def display_name(self):
        return self.name
    
class VoiceVoxStyle:
    def __init__(self, name: str, id: int, speaker: int, type: str):
        self.name = name
        self.id = id
        self.speaker = speaker
        self.type = type

    def display_name(self):
        return f"{self.name}"

logger = get_logger(__name__)

# Choiceリストを作る-----------------------------------------------------------
# VOICEVOXアプリから話者を取得し、リスト形式で返すメソッド-----------------
def load_from_voicevox_app():
    #スピーカー情報を取得し、jsonに変換
    try:   
        #VOICEVOXにリクエスト
        spk_req = requests.get(url=f"http://{VC_HOST}:{VC_PORT}/speakers")
        des_spks = spk_req.json()

        spk_list: list[VoiceVoxSpeaker] = []

        #jsonから話者名とidを取得
        for spk in des_spks:
            vxspk = VoiceVoxSpeaker(
                name=spk["name"],
                uuid=spk["speaker_uuid"]
            )
            #話者のスタイルを取得
            for style in spk["styles"]:
                vxstyle = VoiceVoxStyle(
                    name=style["name"],
                    id=style["id"],
                    speaker=spk["name"],
                    type=style["type"]
                )
                vxspk.styles.append(vxstyle)

            #話者をリストに追加
            spk_list.append(vxspk)

        logger.info(f"読み込み完了: {len(spk_list)}人の話者をロードしました")
        return spk_list
    except:
        logger.exception("VOICEVOXアプリから話者の読み込みに失敗")
        return None


            