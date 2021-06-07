import discord
from discord.ext import commands
from discord.ext.commands import Cog
from random import choice
import time
from datetime import datetime,timedelta
import asyncio

class General(commands.Cog):
    def __init__(self,client):
        self.client=client
        self.ball = [
        ("As I see it, yes"),
        ("It is certain"),
        ("It is decidedly so"),
        ("Most likely"),
        ("Outlook good"),
        ("Signs point to yes"),
        ("Without a doubt"),
        ("Yes"),
        ("Yes – definitely"),
        ("You may rely on it"),
        ("Reply hazy, try again"),
        ("Ask again later"),
        ("Better not tell you now"),
        ("Cannot predict now"),
        ("Concentrate and ask again"),
        ("Don't count on it"),
        ("My reply is no"),
        ("My sources say no"),
        ("Outlook not so good"),
        ("Very doubtful"),
    ]
        self.stopwatches={}

    @commands.command()
    async def flip(self, ctx, user: discord.Member = None):
        if user is not None:
            msg = ""
            if user.id == ctx.bot.user.id:
                user = ctx.author
                msg = "Nice try. You think this is funny?\n How about *this* instead:\n\n"
            char = "abcdefghijklmnopqrstuvwxyz"
            tran = "ɐqɔpǝɟƃɥᴉɾʞlɯuodbɹsʇnʌʍxʎz"
            table = str.maketrans(char, tran)
            name = user.display_name.translate(table)
            char = char.upper()
            tran = "∀qƆpƎℲפHIſʞ˥WNOԀQᴚS┴∩ΛMX⅄Z"
            table = str.maketrans(char, tran)
            name = name.translate(table)
            await ctx.send(msg + "(╯°□°）╯︵ " + name[::-1])
        else:
            await ctx.send(("*flips a coin and... ") + choice([("HEADS!*"),("TAILS!*")]))

    @commands.command(name="8", aliases=["8ball"])
    async def _8ball(self, ctx, *, question: str):
        if question.endswith("?") and question != "?":
            await ctx.send("`" + (choice(self.ball)) + "`")
        else:
            await ctx.send("That doesn't look like a question.")
    
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

    @commands.command()
    async def timer(self, ctx, seconds):
        try:
            secondint = int(seconds)
            if secondint > 600:
                await ctx.send("I dont think im allowed to do go above 600 seconds.")
                return
            if secondint <= 0:
                await ctx.send("I dont think im allowed to do negatives")
                return
            message = await ctx.send("Timer: {seconds}")
            while True:
                secondint -= 1
                if secondint == 0:
                    await message.edit(content="Ended!")
                    break
                await message.edit(content=f"Timer: {secondint}")
                await asyncio.sleep(1)
            await ctx.send(f"{ctx.author.mention} Your timer Has ended!")
        except ValueError:
            await ctx.send("Must be a number!")
            return


def setup(client):
    client.add_cog(General(client))
