import discord
from discord.ext import commands
from discord.ext.commands import Cog


class Math(commands.Cog):
    '''This is the math cog of the bot'''

    def __init__(self,client):
        self.client=client

    @commands.command(aliases=["calculate"],brief="Does some basic math operations.",description="This command will do basic mathematical operations like +,-,/,*,//,%. Multiple operations can be used in the same expression.This command also supports the usage of exponential operator ,example: 1e6-100e1")
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
    client.add_cog(Math(client))
        