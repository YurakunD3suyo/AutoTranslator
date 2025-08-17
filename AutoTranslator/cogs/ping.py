# import discord
from discord import app_commands, Interaction, Embed, Color
from discord.ext import commands


class Ping( commands.Cog ):
    def __init__(self, bot: commands.Bot):
        self.bot = bot

    @app_commands.command(name="ping", description="Pingコマンド")
    async def ping(self, interact: Interaction):
        embed = Embed(color=Color.green(), title="Pongなのだ", description=f"レイテンシ: {self.bot.latency*1000:.2f}ms")
        await interact.response.send_message(embed=embed)

async def setup(bot: commands.Bot) -> None:
    await bot.add_cog(Ping(bot))