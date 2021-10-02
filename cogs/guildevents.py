import discord
from discord.ext import commands
from discord.ext.commands import Cog

class guildEvents(commands.Cog):
    def __init__(self,client):
        self.client=client

    @commands.Cog.listener()
    async def on_member_join(self,member):
        await member.send(f"Welcome to {member.guild.name}.")

def setup(client):
    client.add_cog(guildEvents(client))