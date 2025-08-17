import discord
import datetime
from discord.ext.commands import Bot

def make_embed(bot: Bot = None, 
               title: str = None, 
               description: str = None,
               color: discord.Color = discord.Color.default()):
    
    """Embedを作成する関数"""
    embed = discord.Embed(
        title=title,
        description=description,
        color=color
    )

    time_now = datetime.datetime.now(tz=datetime.timezone(datetime.timedelta(hours=9)))  # JST
    embed.timestamp = time_now

    if bot:
        embed.set_footer(text=f"{bot.user.name} | Made by yurq.", icon_url=bot.user.avatar.url if bot.user.avatar else None)

    return embed

def make_error_embed(bot: Bot = None, 
               title: str = None, 
               description: str = None,
               color: discord.Color = discord.Color.red(),
               error: str = None):
    """エラーメッセージのEmbedを作成する関数"""
    embed = discord.Embed(
        title=title,
        description=description,
        color=color
    )

    community_link = "https://discord.gg/JUWyJKV9Aw"
    embed.add_field(name=f"お問い合わせ", value=community_link)
    
    if error:
        embed.add_field(name="エラー内容", value=error, inline=False)

    time_now = datetime.datetime.now(tz=datetime.timezone(datetime.timedelta(hours=9)))  # JST
    embed.timestamp = time_now

    if bot:
        embed.set_footer(text=f"{bot.user.name} | Made by yurq.", icon_url=bot.user.avatar.url if bot.user.avatar else None)

    return embed