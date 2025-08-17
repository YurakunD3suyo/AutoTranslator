import discord
import os
from discord.ext.commands import Cog, Bot
from discord import Message, FFmpegPCMAudio, PCMVolumeTransformer, VoiceClient, Guild
from typing import List
from modules.env import load_env
from modules.log import get_logger
from modules.vc.delete import delete_file_latency
from collections import deque, defaultdict

logger = get_logger(__name__)

class SynthData:
    def __init__(self, directory: str, length: float, volume: float):
        self.directory = directory
        self.length = length
        self.volume = volume

server_queue = defaultdict(deque)

def queue(filelist: SynthData, guild: Guild):
    """形式: [ディレクトリ、　レイテンシ、音量]"""
    
    queue = server_queue[guild.id]
    queue.append(filelist)

    logger.debug(f"Queue Added: [server_id: {guild.id}, file: {filelist.directory}]")

    if not guild.voice_client.is_playing():
        play(queue, guild.voice_client)
        

def play(queue: deque, voice_client: VoiceClient):

    if not voice_client or not queue:
        return
    if voice_client.is_playing():
        return
    
    source: SynthData = queue.popleft()
    
    pcmaudio_fixed = PCMVolumeTransformer(FFmpegPCMAudio(source.directory))
    pcmaudio_fixed.volume = source.volume

    voice_client.play(pcmaudio_fixed, after=lambda e:play(queue, voice_client))
    logger.debug(f"Playing: [server_id: {voice_client.guild.id}, file: {source.directory}]")

    if source.length != -1:
        ## 再生スタートが完了したら時間差でファイルを削除する。
        delete_file_latency(source.directory, source.length+1)