import discord
from discord.ext import commands
from discord.ext.commands import Cog
import random
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
        elapsed = now - self.client.starttime
        seconds = elapsed.seconds
        minutes, seconds = divmod(seconds, 60)
        hours, minutes = divmod(minutes, 60)
        await ctx.send("Bot has been running for {}d {}h {}m {}s".format(elapsed.days, hours, minutes, seconds))

    @commands.command(name="choose",brief="A command in case you get into a dilemma.",description="This command takes in multiple string values separated by commas as arguements and chooses returns one from them.")
    async def _choose(self,ctx,*,args):
        options=args.split(",")
        chosen_one=random.choice(options)        
        await ctx.send(f"I have choosen... _{chosen_one}_!")
    
    @commands.command(name="poll",brief="A command similar to choose, but the people choose the option here",description="This command takes in a topic (which has to be enclosed in double quotes, the stuff after the topic are all considered as options)and mutiple string values separated by commas and then makes a poll with it for people to vote on the most favourable option.(max options is 9)")
    async def _poll(self,ctx,topic,*,options):
        option=options.split(",")
        if len(option)>8:
            await ctx.send("You can't have more than 8 options at a time, if you need more than 8 then run the command twice with less than 8 options each time.")
        emojis=self.client.number_emojis[:len(option)]
        embed=discord.Embed(title=topic,description="Vote on this poll to decide on an option.")
        for i in option:
            embed.add_field(name=i+emojis[option.index(i)] or "No option provided",value="\u2800",inline=False)
        msg=await ctx.send(embed=embed)
        for i in emojis:
            await msg.add_reaction(i)
    
    @commands.command(name="calc",aliases=["calculate"],brief="Does some basic math operations.",description="This command will do basic mathematical operations like +,-,/,*,//,%. Multiple operations can be used in the same expression.This command also supports the usage of exponential operator ,example: 1e6-100e1")
    async def calc(self,ctx,expression):
        for i in expression:
            if i not in ["+","-","*","/","//","%","(",")",".","e","1","2","3","4","5","6","7","8","9","0"]:
                await ctx.send("That is not a valid mathematical expression.")
                break
        else:
            try:
                final_answer=eval(expression)
            except Exception as e:
                await ctx.send(f"An error has been raised : `{e}`")
            await ctx.send(f"Final answer `{final_answer}`")

def setup(client):
    client.add_cog(General(client))
