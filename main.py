import discord
from discord.ext import commands
from datetime import datetime
import asyncio
import asyncpraw
from discord.ui.item import V
from config import *
from utils import slash_util

class Bot(slash_util.Bot):
    def __init__(self,*args,**kwargs):
        super().__init__(*args,**kwargs)
        self.starttime=datetime.utcnow()
        self.botcogs=["cogs.errors","jishaku","cogs.info","cogs.usercommands"]
    

    async def on_ready(self):
        print("Logged in as",self.user)

    async def load_cogs(self):
        for i in self.botcogs:
            self.load_extension(i)
            print(f"Loaded {i}")

    async def get_invite(self):
        return "https://discord.com/api/oauth2/authorize?client_id=843071820878184458&permissions=415797472576&scope=bot"


bot=Bot(command_prefix=".",intents=discord.Intents.all())

bot.loop.create_task(bot.load_cogs())
bot.run(BOT_TOKEN)