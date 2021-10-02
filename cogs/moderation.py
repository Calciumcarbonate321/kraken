import discord
from discord.ext import commands
from discord.ext.commands import Cog
from discord.ext.commands.cooldowns import BucketType

class Moderation(commands.Cog):
    def __init__(self,client):
        self.client=client

    @commands.command(name="kick")
    @commands.cooldown(1,60,type=BucketType.member)
    @commands.has_permissions(ban_members=True)
    async def _kick(self,ctx, member : discord.Member=None,*,reason : str=None):
        if member is None:
            await ctx.send("Specify a member to kick.")
            return
        try:
            await member.send(f"You have been kicked by {ctx.author.name} from {ctx.guild.name}. Reason : {reason}")
        except:
            pass
        try:
            await member.kick(reason=reason)
        except:
            await ctx.send("I don't have permissions to kick that user")

    @commands.command(name="ban",aliases=["yeet"])
    @commands.cooldown(1,60,type=BucketType.member)
    @commands.has_permissions(ban_members=True)
    async def _ban(self,ctx, member : discord.Member=None,*,reason : str=None):
        if member is None:
            await ctx.send("Specify a member to kick.")
            return
        try:
            await member.send(f"You have been banned by {ctx.author.name} from {ctx.guild.name}. Reason : {reason}")
        except:
            pass
        try:
            await member.ban(reason=reason)
        except:
            await ctx.send("I don't have permissions to ban that user")
        
def setup(client):
    client.add_cog(Moderation(client))
