from datetime import datetime,timedelta
from os import name
import discord
import aiohttp
import time
from utils.views import *
from config import APPLICATION_ID,BOT_TOKEN
from datetime import timezone
from discord import app_commands
from discord.ext import commands

class Informative(commands.Cog):
    def __init__(self,bot):
        self.bot=bot
        self.stopwatches = {}
    
    @app_commands.command(name="aboutme",description="About me command.")
    async def aboutme(self,interaction):
        embed=discord.Embed(title="About me",description="Hi I am a multipurpose discord bot made by CaCO3#9990. I was made using [discord.py](https://github.com/Rapptz/discord.py)",color=0x2F3136)
        embed.add_field(name="Credits",value="Huge thanks to Danny#0007 for making discord.py and Maya#9000 for making the slash command handler.")
        embed.add_field(name="Latency",value=round(self.bot.latency*1000),inline=False)
        c = datetime.now(timezone.utc)
        elapsed=c-self.bot.starttime
        seconds = elapsed.seconds
        minutes, seconds = divmod(seconds, 60)
        hours, minutes = divmod(minutes, 60)
        embed.add_field(
            name="Uptime", value=f"{elapsed.days}d {hours}h {minutes}m {seconds}s"
        )

        embed.set_thumbnail(url=self.bot.user.avatar.url)
        e=self.bot.get_user(437163344525393920)
        embed.set_footer(text="Made with ❤️ by CaCO3#9990",icon_url=e.avatar.url)
        view=discord.ui.View()
        view.add_item(invitebutton())
        view.add_item(sourcebutton())
        await interaction.response.send_message(content="Hello there",embed=embed,view=view)
        
    @app_commands.command(name="userinfo",description="Describes a user.")
    @app_commands.describe(user="The user to describe. Can be blank.")
    async def userinfo(self,interaction, user: discord.Member = None): 
        if isinstance(interaction.channel,discord.DMChannel):
            view=discord.ui.View()
            view.add_item(invitebutton())
            return await interaction.response.send_message("Sorry this command cannot be used in a dm channel, invite me to your server to use this.",view=view)
        if user is None:
            user = interaction.user
        date_format = "%a, %d %b %Y %I:%M %p"
        embed = discord.Embed(color=0xdfa3ff, description=user.mention)
        if user.avatar:
            embed.set_author(name=str(user), icon_url=user.avatar.url)
        if user.avatar:
            embed.set_thumbnail(url=user.avatar.url)
        embed.add_field(name="Joined", value=user.joined_at.strftime(date_format))
        members = sorted(interaction.guild.members, key=lambda m: m.joined_at)
        embed.add_field(name="Join position", value=str(members.index(user)+1))
        embed.add_field(name="Registered", value=user.created_at.strftime(date_format))
        if len(user.roles) > 1:
            role_string = ' '.join([r.mention for r in user.roles][1:])
            embed.add_field(name="Roles [{}]".format(len(user.roles)-1), value=role_string, inline=False)
        perm_string = ', '.join(
            str(p[0]).replace("_", " ").title()
            for p in user.guild_permissions
            if p[1]
        )

        embed.add_field(name="Guild permissions", value=perm_string, inline=False)
        embed.set_footer(text='ID: ' + str(user.id))
        view=deletethismessage(interaction.user)
        await interaction.response.send_message(content=None,embed=embed,view=view)

    @app_commands.command(name="serverinfo",description="Describes the server you are in")
    async def serverinfo(self,interaction):
        if isinstance(interaction.channel,discord.DMChannel):
            view=discord.ui.View()
            view.add_item(invitebutton())
            return await interaction.response.send_message("Sorry this command cannot be used in a dm channel, invite me to your server to use this.",view=view)
        guild=interaction.guild
        embed=discord.Embed(title="Server Information",description=f"This embed contains information about {guild.name}",color=0x2F3136)
        try:
            embed.set_thumbnail(url=guild.icon.url)
        except:
            pass
        if guild.banner:
            embed.set_image(url=guild.banner.url)
        embed.add_field(name="Owner",value=guild.owner.mention)
        embed.add_field(name="Member count",value=guild.member_count)
        bots=len([i for i in guild.members if i.bot])
        embed.add_field(name="Number of bots",value=bots)
        embed.add_field(name="Numer of text channels",value=len(guild.text_channels))
        embed.add_field(name="Number of voice channels",value=len([i for i in guild.channels if isinstance(i,discord.VoiceChannel)]))
        embed.add_field(name="Number of categories",value=len(guild.categories))
        if guild.features:
            embed.add_field(name="Server features",value="✅"+"\n✅".join(guild.features) or "Nothing")
        embed.set_footer(text=f"ID:{guild.id}",icon_url=interaction.user.avatar.url)
        v=deletethismessage(interaction.user)
        await interaction.response.send_message(content=None,embed=embed,view=v)
        

    @app_commands.command(name="roleinfo",description="Describes a role.")
    async def roleinfo(self,interaction,role:discord.Role):
        embed=discord.Embed(title="Role information",description=f"Information about the {role.name} role.",color=0x2F3136)
        embed.add_field(name="Mention of the role",value=role.mention)
        embed.add_field(name="Colour of role",value=role.color)
        embed.add_field(name="Hoist status",value=role.hoist)
        embed.add_field(name="Mention status",value=role.mentionable)
        embed.add_field(name="Managed status",value=role.managed)
        embed.add_field(name="Bot role managed status",value=role.is_bot_managed())
        perm_string = ', '.join(
            str(p[0]).replace("_", " ").title()
            for p in role.permissions
            if p[1]
        )
        embed.add_field(name="Role member count",value=len(role.members))
        embed.add_field(name="Permissions",value=perm_string)
        embed.set_footer(text=f"Requested by {interaction.user}",icon_url=interaction.user.avatar.url)
        await interaction.response.send_message(content=None,embed=embed,view=deletethismessage(interaction.user))

    @app_commands.command(name="stopwatch",description="Starts a stopwatch. Run this again to stop running stopwatch")
    async def stopwatch(self, interaction):
        author = interaction.user
        if str(author.id) not in self.stopwatches:
            self.stopwatches[str(author.id)] = int(time.perf_counter())
            await interaction.response.send_message(author.mention + (" Stopwatch started!"))
        else:
            tmp = abs(self.stopwatches[str(author.id)] - int(time.perf_counter()))
            tmp = str(timedelta(seconds=tmp))
            await interaction.response.send_message(author.mention + (" Stopwatch stopped! Time: **{seconds}**").format(seconds=tmp))
            self.stopwatches.pop(str(author.id), None)


async def setup(bot):
    await bot.add_cog(Informative(bot))
