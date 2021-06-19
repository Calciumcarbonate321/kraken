from discord.ext import commands
from discord.ext.commands import Cog    

import random

from cogs.shopsys import shop
from cogs.bank import bank

class itemUsage(commands.Cog):
    '''This cog houses the item usage commands of the bot economy'''

    def __init__(self,client):
        self.client=client

        self.Shop=shop(client)

    
    async def checkitem(self,userid,item):
        users = await self.Shop.get_shop_data()
        inv = users[str(userid)]["bag"]
        for pog in inv:
            if pog["itemid"] == item:
                return pog["amount"] != 0
                
                
    @commands.command()
    async def hunt(self,ctx):
        userid=str(ctx.author.id)
        if await self.checkitem(userid,"rifle"):
            payout=random.randint(100,500)
            await ctx.send(f"You went to the forest for hunting,sold all the animals that you got and you got ⌬{payout}")
        else:
            await ctx.send("You don't even have a hunting rifle. Buy one from the shop.")

    @commands.command()
    async def fish(self,ctx):
        userid=str(ctx.author.id)
        if await self.checkitem(userid,"fishingrod"):
            payout=random.randint(200,700)
            await ctx.send(f"You went to the lake for fishing,sold all the fish that you caught and you got ⌬{payout}")
        else:
            await ctx.send("You don't even have a fishing rod. Buy one from the shop.")

    @commands.command(aliases=["pm","postmeme"])
    async def postm(self,ctx):
        userid=str(ctx.author.id)
        if await self.checkitem(userid,"laptop"):
            payout=random.randint(50,200)
            await ctx.send(f"You posted some nice memes on reddit and earned ⌬{payout}")
        else:
            await ctx.send("You don't even have a laptop.Buy one from the shop.")



def setup(client):
    client.add_cog(itemUsage(client))
        