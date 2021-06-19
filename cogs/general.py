import discord
from discord.ext import commands
from discord.ext.commands import Cog
from random import choice
import time
from datetime import datetime,timedelta

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


def setup(client):
    client.add_cog(General(client))
