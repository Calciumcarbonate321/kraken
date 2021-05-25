import discord
from discord.ext import commands
from discord.ext.commands import Cog
import aiohttp

class Fun(commands.Cog):
    def __init__(self,client):
        self.client=client

    @commands.command(aliases=['catpics','catpic','cat'])
    async def kitty(self,ctx):
        async with aiohttp.ClientSession() as session:
            request = await session.get('https://some-random-api.ml/img/cat') 
            catjson = await request.json() 
            request2 = await session.get('https://some-random-api.ml/facts/cat')
            factjson = await request2.json()
            embed = discord.Embed(title="Kitty!", color=discord.Color.purple()) 
            embed.set_image(url=catjson['link']) 
            embed.set_footer(text=factjson['fact'])
            await ctx.send(embed=embed) 
    @commands.command(aliases=['dogpics','dogpic','dog'])
    async def doggo(self,ctx):
        async with aiohttp.ClientSession() as session:
            request = await session.get('https://some-random-api.ml/img/dog') 
            dogjson = await request.json() 
            embed = discord.Embed(title="Doggo!", color=discord.Color.purple()) 
            request2 = await session.get('https://some-random-api.ml/facts/dog')
            factjson = await request2.json()           
            embed.set_image(url=dogjson['link']) 
            embed.set_footer(text=factjson['fact'])
            await ctx.send(embed=embed) 


def setup(client):
    client.add_cog(Fun(client))