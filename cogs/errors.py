import discord
from discord.ext import commands
from discord.ext.commands import Cog
import datetime

class Errors(commands.Cog):
    def __init__(self,client):
        self.client=client

    @commands.Cog.listener()
    async def on_command_error(self,ctx : commands.Context,error : commands.CommandError):

        if isinstance(error,commands.CommandOnCooldown):
            message=f"This command is on cooldown. Please try again after {datetime.timedelta(seconds=round(error.retry_after))} seconds."
            await ctx.send(message,delete_after=30)
        elif isinstance(error, commands.MissingPermissions):
            message = f"You don't even have the required perms to run this command.Permissions missing : {error.missing_perms}"
            await ctx.send(message,delete_after=30)
        elif isinstance(error, commands.UserInputError):
            message = "Something about your input was wrong, please check your input and try again!"        
            await ctx.send(message,delete_after=30)

def setup(client):
    client.add_cog(Errors(client))