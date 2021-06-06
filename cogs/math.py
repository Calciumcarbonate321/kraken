import discord
from discord.ext import commands
from discord.ext.commands import Cog

import math

class Math(commands.Cog):
    def __init__(self,client):
        self.client=client

    @commands.command(aliases=["calculate"])
    async def calc(self,ctx,var):
        for i in var:
            if i not in ["+","-","*","/","//","%","1","2","3","4","5","6","7","8","9","0"]:
                await ctx.send("That is not a valid mathematical expression.")
                break
        else:
            await ctx.send(f"Final answer `{eval(var)}`")

def setup(client):
    client.add_cog(Math(client))
        