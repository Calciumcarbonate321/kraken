import discord
from discord.ext import commands
from discord.ext.commands import Cog
import aiohttp
from random import choice

class Fun(commands.Cog):
    '''This cog has some pretty fun commands in it'''

    def __init__(self,client):
        self.client=client
        self.ball = [
        "As I see it, yes",
        "It is certain",
        "It is decidedly so",
        "Most likely",
        "Outlook good",
        "Signs point to yes",
        "Without a doubt",
        "Yes",
        "Yes – definitely",
        "You may rely on it",
        "Reply hazy, try again",
        "Ask again later",
        "Better not tell you now",
        "Cannot predict now",
        "Concentrate and ask again",
        "Don't count on it",
        "My reply is no",
        "My sources say no",
        "Outlook not so good",
        "Very doubtful",
    ]

    @commands.command(aliases=['catpics','catpic','cat'],description="This command will show a random cat picture.")
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
    @commands.command(aliases=['dogpics','dogpic','dog'],description="This command will show a random cat picture.")
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

    @commands.command(description='For when plain text just is not enough')
    async def emojify(self,ctx, *, text: str):

        author = ctx.message.author
        formatted=str()
        for c in text:
            if c.isalpha():
                formatted+=c
        if text == '':
            await ctx.send('Remember to say what you want to convert!')
        else:
            emojified = ''.join(
                '     ' if i == ' ' else ':regional_indicator_{}: '.format(i)
                for i in formatted
            )

            if len(emojified) >= 1998:
                await ctx.send('Your message in emojis exceeds 2000 characters!')
            if len(emojified) <= 25:
                await ctx.send('Your message could not be converted!')
            else:
                await ctx.send(''+emojified+'')


    @commands.command(name="8ball")
    async def _8ball(self, ctx, *, question: str):
        if question.endswith("?") and question != "?":
            await ctx.send("`" + (choice(self.ball)) + "`")
        else:
            await ctx.send("That doesn't look like a question.")
              

def setup(client):
    client.add_cog(Fun(client))
