import requests
import json
import random
import string
import wave
import os

from modules.log import get_logger 
from modules.vc.queues import SynthData

# loggerの設定
logger = get_logger(__name__)

VC_OUTPUT = "./tts_cache/"
FS = 24000
VC_HOST = "127.0.0.1"
VC_PORT = 50021

if not os.path.exists(VC_OUTPUT):
    os.mkdir(VC_OUTPUT)

def make_id(n):
   randlst = [random.choice(string.ascii_letters + string.digits) for i in range(n)]
   return ''.join(randlst)

def synthesis(content: str, spkID: int, speed: float = 1):
    logger.debug(f'Creating audio: {content}')
    logger.debug(f'Using speaker ID: {spkID}')
    logger.debug(f'Using speed: {speed}')

    params = (
        ('text', content),
        ('speaker', spkID)
    )
    _query = requests.post(
        f'http://{VC_HOST}:{VC_PORT}/audio_query',
        params=params
    )
    query = _query.json()
    query["speedScale"] = speed

    synthesis = requests.post(
        f'http://{VC_HOST}:{VC_PORT}/synthesis',
        headers = {"Content-Type": "application/json"},
        params = params,
        data = json.dumps(query)
    )
    voice_byte = synthesis.content

    # ランダムなIDを生成する
    random_id = make_id(12)
    file_dir = os.path.join(VC_OUTPUT, f"{random_id}.wav")

    if synthesis.status_code == 200:
        with open(file_dir, "wb") as f:
            f.write(voice_byte)
    else:
        logger.error(f"音声合成エラー: {synthesis.status_code} {synthesis.text}")
        return None

    with wave.open(file_dir,  'rb') as f:
        # 情報取得
        framerate = f.getframerate()
        frames = f.getnframes()
        length = frames / framerate

    tts_list = SynthData(file_dir, length, 1) # volumeは1

    return tts_list
