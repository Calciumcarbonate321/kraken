import discord
import datetime
import contextlib
from discord.ext import commands


class HelpEmbed(discord.Embed): # Our embed with some preset attributes to avoid setting it multiple times
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.timestamp = datetime.datetime.utcnow()
        text = "Use help [command] or help [category] for more information | <> is required | [] is optional, also right click on a user/message to have a look at the user/message commands."
        self.set_footer(text=text)
        self.color = discord.Color.random()

class MyHelp(commands.HelpCommand):
    def __init__(self):
        super().__init__( # create our class with some aliases and cooldown
            command_attrs={
                "help": "The main help command of this bot.",
                
            }
        )
        

    async def send(self, **kwargs):
        await self.get_destination().send(**kwargs)

    async def send_bot_help(self, mapping):
        ctx = self.context
        embed = HelpEmbed(title=f"{ctx.me.display_name} Help")
        embed.set_thumbnail(url=ctx.me.avatar_url)
        usable = 0 

        for cog, commands in mapping.items(): #iterating through our mapping of cog: commands
            if filtered_commands := await self.filter_commands(commands): 
                # if no commands are usable in this category, we don't want to display it
                amount_commands = len(filtered_commands)
                usable += amount_commands
                if cog: # getting attributes dependent on if a cog exists or not
                    name = cog.qualified_name
                    description = cog.description or "No description"
                else:
                    name = "No Category"
                    description = "Commands with no category"

                embed.add_field(name=f"{name} Category [{amount_commands}]", value=description)

        embed.description = "Some commands may not be listed as you cannot use them."   
        await self.send(embed=embed)

    async def send_command_help(self, command):
        signature = self.get_command_signature(command) # get_command_signature gets the signature of a command in <required> [optional]
        embed = HelpEmbed(title=signature, description=command.help or "There is no help for this ")

        if cog := command.cog:
            embed.add_field(name="Category", value=cog.qualified_name)

        can_run = "No"
        # command.can_run to test if the cog is usable
        with contextlib.suppress(commands.CommandError):
            if await command.can_run(self.context):
                can_run = "Yes"
            
        embed.add_field(name="Usable", value=can_run)

        if command._buckets and (cooldown := command._buckets._cooldown): # use of internals to get the cooldown of the command
            embed.add_field(
                name="Cooldown",
                value=f"{cooldown.rate} per {cooldown.per:.0f} seconds",
            )
        await self.send(embed=embed)

    async def send_help_embed(self, title, description, commands): # a helper function to add commands to an embed
        embed = HelpEmbed(title=title, description=description or "There is no help for this")

        if filtered_commands := await self.filter_commands(commands):
            for command in filtered_commands:
                embed.add_field(name=self.get_command_signature(command), value=command.help or "There is no help for this")
           
        await self.send(embed=embed)

    async def send_group_help(self, group):
        title = self.get_command_signature(group)
        await self.send_help_embed(title, group.help, group.commands)

    async def send_cog_help(self, cog):
        title = cog.qualified_name or "No"
        await self.send_help_embed(f'{title} Category', cog.description, cog.get_commands())

