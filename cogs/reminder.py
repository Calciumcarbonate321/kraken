import discord
from discord.ext import commands
import asyncio
from discord import app_commands

class Reminder(commands.Cog):
    def __init__(self,bot):
        self.bot=bot

    @app_commands.command(name="remind",description="Reminder command, give time in seconds.")
    async def remind(self,interaction,time:str,message:str=None):
        await interaction.response.send_message(f"Okay I will remind you about `{message}` in {time}")
        await asyncio.sleep(time)
        self.bot.dispatch('remind',interaction.user,interaction.channel,message)
    
    @commands.Cog.listener()
    async def on_remind(self,author,channel,message):
        await channel.send(f"{author.mention} you told me to remind about `{message}`")

async def setup(bot):
    await bot.add_cog(Reminder(bot))