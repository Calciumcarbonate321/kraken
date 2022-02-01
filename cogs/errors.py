import discord
import sys
import traceback
from discord.ext import commands
import datetime
from difflib import get_close_matches
import wavelink
from wavelink.errors import QueueEmpty
from utils.views import invitebutton
import logging


class CommandErrorHandler(commands.Cog):

    def __init__(self, bot):
        self.bot=bot
        self.logger = logging.getLogger("discord")

    @commands.Cog.listener()
    async def on_command_error(self, ctx, error):  

        if hasattr(ctx.command, 'on_error'):
            return

        cog = ctx.cog
        if cog and cog._get_overridden_method(cog.cog_command_error) is not None:
            return
        ignored = (commands.NotOwner)

        error = getattr(error, 'original', error)

        if isinstance(error, ignored):
            return

        if isinstance(error, commands.CommandNotFound):
            cmd = ctx.invoked_with
            cmds = [cmd.name for cmd in self.bot.commands if not cmd.hidden] 
            matches = get_close_matches(cmd, cmds)
            if len(matches) > 0:
                await ctx.send(f'Command "{cmd}" not found, maybe you meant "{matches[0]}"?')
            return

        if isinstance(error, commands.DisabledCommand):
            await ctx.send(f'{ctx.command} has been disabled.')

        elif isinstance(error,commands.MemberNotFound):
            await ctx.send("Sorry, that member was not found. Make sure you have provided a valid user id/user name.")
        
        elif isinstance(error,commands.ChannelNotFound):
            await ctx.send("Sorry, that channel was not found. Make sure you have provided a valid channel id/name.")
        
        elif isinstance(error,commands.RoleNotFound):
            await ctx.send("Sorry, that role was not found. Make sure you have provided a valid role id/name.")

        elif isinstance(error,commands.ChannelNotReadable):
            await ctx.send("Sorry I do not have the permission to read the messages in that channel.")
        
        elif isinstance(error,commands.MissingRequiredArgument):
            await ctx.send(f"Sorry, {error}")

        elif isinstance(error,commands.BadArgument):
            await ctx.send(f"{error.args}")

        elif isinstance(error, commands.MissingPermissions):
            await ctx.send(f"Sorry you are missing some permission(s) that are required to run this command : {error.missing_permissions}")
        
        elif isinstance(error,commands.BotMissingPermissions):
            await ctx.send(f"Sorry I am missing some permission(s) that are required to run this command : {error.missing_permissions}")

        elif isinstance(error,commands.CommandOnCooldown):
            message=f"This command is on cooldown. Please try again after {datetime.timedelta(seconds=round(error.retry_after))} seconds."
            await ctx.send(message)  

        elif isinstance(error,commands.NoPrivateMessage):
            view=discord.ui.View()
            view.add_item(invitebutton())
            await ctx.send("Sorry you cannot use this command in my dm channel, please join a server where I am or invite me",view=view)

        elif isinstance(error,commands.ArgumentParsingError):
            await ctx.send("There was some error in parsing your arguement(s).")

        elif isinstance(error,wavelink.LavalinkException):
            await ctx.send("There was some problem with the music server, please try again, I have reported to my owner.")
            await ctx.bot.owner.send(traceback.print_exception(type(error), error, error.__traceback__, file=sys.stderr))
        
        elif isinstance(error,wavelink.LoadTrackError) or isinstance(error,wavelink.BuildTrackError) or isinstance(error,wavelink.InvalidIDProvided):
            await ctx.send("There was some error in loading your given track, I have reported to my owner,")
            traceback.print_exception(type(error), error, error.__traceback__, file=sys.stderr)

        elif isinstance(error,wavelink.NodeOccupied):
            await ctx.send("Sorry the server is a bit overloaded right now, please try again.")
        
        elif isinstance(error,QueueEmpty):
            await ctx.send("Sorry the queue is empty.")
'''
        else:
            self.logger.exception(msg=f"Ignoring exception in command {ctx.command}: \n {type(error)}\n {error}\n {error.__traceback__}")
            print('Ignoring exception in command {}:'.format(ctx.command), file=sys.stderr)
            traceback.print_exception(type(error), error, error.__traceback__, file=sys.stderr)
'''
def setup(client):
    client.add_cog(CommandErrorHandler(client))