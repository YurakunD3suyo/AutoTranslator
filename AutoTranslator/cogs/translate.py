import deepl
import langdetect
import threading
import os

from discord.ext import commands
from discord import app_commands, Interaction, Message, Embed, Color, File
from discord.app_commands import Choice

class Translate( commands.Cog ):
    def __init__(self, bot: commands.Bot):
        self.bot = bot
        self.auth = os.getenv("DEEPL_AUTH_KEY")
        self.translator = deepl.Translator(self.auth) 

    @commands.Cog.listener()
    async def on_message(self, message: Message):
        #ignore bot
        if message.author.bot:
            return
        
        if (self.translator):
            try:
                sentence = message.content
                
                target_lang = None
                try:
                    # detect language
                    detected_lang = langdetect.detect(sentence)
                    
                    # translate
                    if (detected_lang == "ja"):
                        target_lang = "EN-US"
                    elif (detected_lang == "en"):
                        target_lang = "JA"
                except:
                    return
                
                if target_lang:
                    result = self.translator.translate_text(sentence, target_lang=target_lang)
                else:
                    result = sentence
                
                if result:
                    embed = Embed(title=result, description=f"{sentence}", color=Color.green())
                    
                    if not target_lang:
                        lang_convert = "original message"
                    else:
                        lang_convert = f"{detected_lang} -> {target_lang}"
                       
                    embed.set_author(name=f"Sended by {message.author.display_name}", icon_url=message.author.display_avatar.url)
                    
                    embed.set_footer(text=lang_convert)
                    
                else:
                    embed = Embed(title="Failed to Translate...", description="oh, my bot stopped working.")
                    
                await message.channel.send(embed=embed)
                return
            
            except Exception as e:
                embed = Embed(title="Failed to Translate...", description=f"oh, my bot stopped working.\n ```{e}```")     
                await message.channel.send(embed=embed)
                
    @app_commands.command(name="translate", description="翻訳コマンドなのだ")
    @app_commands.choices(target_lang=[
        Choice(name="English (US)", value="EN-US"),
        Choice(name="English (UK)", value="EN-GB"),
        Choice(name="Chinese (簡体)", value="ZN-HANS"),
        Choice(name="Chinese (繁体)", value="ZN-HANT"),
        Choice(name="Korean", value="KO"),
        Choice(name="Japanese", value="JA")
    ])
    @app_commands.rename(target_lang="target_language")
    async def translate(self, interact: Interaction, sentence: str, target_lang: str):
        if (self.translator):
            result = self.translator.translate_text(sentence, target_lang=target_lang)

        embed = Embed(
            title="Done!",
            description="Translated Succesfully.",
            color=Color.green()
        )
        embed.add_field(
            name="Before",
            value=sentence,
            inline=False
        )
        embed.add_field(
            name="After",
            value=result,
            inline=False
        )
        embed.set_thumbnail(url=f"attachment://boticon_zunda.png")
        embed.set_footer(text=f"DeepL Translate", icon_url="https://cdn.freelogovectors.net/wp-content/uploads/2022/01/deepl-logo-freelogovectors.net_.png")

        await interact.response.send_message(embed=embed)

async def setup(bot: commands.Bot) -> None:
    await bot.add_cog(Translate(bot))

