import discord
from discord.ext import commands
from discord.ext.commands import Cog
from random import choice
import time
from datetime import datetime,timedelta
from main import *

class General(commands.Cog):
    '''This cog has the general commands which aren't categorised'''

    def __init__(self,client):
        self.client=client
        self.stopwatches={}
  
    @commands.command(aliases=["sw"])
    async def stopwatch(self, ctx):
        author = ctx.author
        if str(author.id) not in self.stopwatches:
            self.stopwatches[str(author.id)] = int(time.perf_counter())
            await ctx.send(author.mention + (" Stopwatch started!"))
        else:
            tmp = abs(self.stopwatches[str(author.id)] - int(time.perf_counter()))
            tmp = str(timedelta(seconds=tmp))
            await ctx.send(author.mention + (" Stopwatch stopped! Time: **{seconds}**").format(seconds=tmp))
            self.stopwatches.pop(str(author.id), None)

    @commands.command(name="uptime")
    async def uptime(self,ctx):
        now=datetime.utcnow()
        elapsed = now - starttime
        seconds = elapsed.seconds
        minutes, seconds = divmod(seconds, 60)
        hours, minutes = divmod(minutes, 60)
        await ctx.send("Bot has been running for {}d {}h {}m {}s".format(elapsed.days, hours, minutes, seconds))

def setup(client):
    client.add_cog(General(client))
