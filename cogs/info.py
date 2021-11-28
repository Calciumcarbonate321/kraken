from datetime import datetime
from operator import le
from os import name
import discord
from discord import invite
from discord.ext import commands
import aiohttp
from discord.ext.commands.errors import NoPrivateMessage
from utils import slash_util
from utils.views import *
from config import APPLICATION_ID,BOT_TOKEN

class Informative(slash_util.ApplicationCog,name="Informative"):
    def __init__(self,bot:slash_util.Bot):
        super().__init__(bot)
        self.bot=bot

    @slash_util.slash_command(name="about",description="A command about me")
    async def aboutme(self,ctx:slash_util.Context):
        """A bit about me :)"""
        embed=discord.Embed(title="About me",description="Hi I am a multipurpose discord bot made by CaCO3#9990. I was made completely using [discord.py](https://github.com/Rapptz/discord.py) and slash command support is added by [this](https://gist.github.com/XuaTheGrate/5690a3d9dadb280d3d15f28f940e02d1)",color=0x2F3136)
        embed.add_field(name="Credits",value="Huge thanks to Danny#0007 for making discord.py and Maya#9000 for making the slash command handler.")
        embed.add_field(name="Latency",value=round(self.bot.latency*1000),inline=False)
        c=datetime.utcnow()
        elapsed=c-self.bot.starttime
        seconds = elapsed.seconds
        minutes, seconds = divmod(seconds, 60)
        hours, minutes = divmod(minutes, 60)        
        embed.add_field(name="Uptime",value="{}d {}h {}m {}s".format(elapsed.days, hours, minutes, seconds))
        embed.set_thumbnail(url=self.bot.user.avatar.url)
        e=self.bot.get_user(437163344525393920)
        embed.set_footer(text="Made with ❤️ by CaCO3#9990",icon_url=e.avatar.url)
        view=discord.ui.View()
        view.add_item(invitebutton())
        view.add_item(sourcebutton())
        await ctx.send(content="Hello there",embed=embed,view=view)
        
    @slash_util.slash_command(name="userinfo",description="Gives you information about a member in your server.")
    @slash_util.describe(user="The user whose information you want.")
    async def userinfo(self,ctx:slash_util.Context, user: discord.Member = None): 
        if isinstance(ctx.channel,discord.DMChannel):
            view=discord.ui.View()
            view.add_item(invitebutton())
            return await ctx.send("Sorry this command cannot be used in a dm channel, invite me to your server to use this.",view=view)
        """Gives you information about a member in your server, just use the command and select their user from the autocomplete or type out the name yourself."""
        if isinstance(ctx.channel,discord.DMChannel):
            await ctx.send("This command can only be used in servers,sorry.You can do e!invite to get my invite.")
        if user is None:
            user = ctx.author
        date_format = "%a, %d %b %Y %I:%M %p"
        embed = discord.Embed(color=0xdfa3ff, description=user.mention)
        if user.avatar:
            embed.set_author(name=str(user), icon_url=user.avatar.url)
        if user.avatar:
            embed.set_thumbnail(url=user.avatar.url)
        embed.add_field(name="Joined", value=user.joined_at.strftime(date_format))
        members = sorted(ctx.guild.members, key=lambda m: m.joined_at)
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
        view=deletethismessage(ctx.author)
        await ctx.send(content=None,embed=embed,view=view)

    @slash_util.slash_command(name="help",description="This command lists out all the slash commands of this bot and tells what it does.")
    async def helpme(self,ctx:slash_util.Context,command_name:str=None):
        """Gives you help about the bot."""
        if command_name:
            if (scommand:=self.bot.get_application_command(command_name)):
                return await ctx.send(scommand.func.__doc__)
            else:
                return await ctx.send(f"Sorry, no command with the name `{command_name}` was found.")
        async with aiohttp.ClientSession(headers={"Authorization":f"Bot {BOT_TOKEN}"}) as session:
            async with session.get(f"https://discord.com/api/v8/applications/{APPLICATION_ID}/commands") as res:
                commandlist=await res.json()
                embed=discord.Embed(title="Kraken help",description="Stop it,get some help")
                embed.set_thumbnail(url=self.bot.user.avatar.url)
                e=self.bot.get_user(437163344525393920)
                embed.set_footer(text="Made with ❤️ by CaCO3#9990",icon_url=e.avatar.url)
                fcount=0
                nembed=discord.Embed(title="Kraken bot help",description="Stop it get some help")
                for i in commandlist:
                    if fcount<10:
                        cname=i.get('name')
                        scoommand=self.bot.get_application_command(cname)
                        embed.add_field(name=scoommand.name,value=scoommand.func.__doc__)
                        fcount+=1
                    else:
                        scoommand=self.bot.get_application_command(cname)
                        nembed.add_field(name=scoommand.name,value=scoommand.func.__doc__)
                view=discord.ui.View()
                view.add_item(invitebutton())
                await ctx.send(content=None,embeds=[embed],view=view)

    @slash_util.slash_command(name="serverinfo",description="This command gives you information about the server you are in.")
    async def serverinfo(self,ctx:slash_util.Context):
        if isinstance(ctx.channel,discord.DMChannel):
            view=discord.ui.View()
            view.add_item(invitebutton())
            return await ctx.send("Sorry this command cannot be used in a dm channel, invite me to your server to use this.",view=view)
        guild=ctx.guild
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
        embed.set_footer(text=f"ID:{guild.id}",icon_url=ctx.author.avatar.url)
        v=deletethismessage(ctx.author)
        await ctx.send(content=None,embed=embed,view=v)
        
    @slash_util.slash_command(name="roleinfo",description="This command gives you information about a role.")
    async def roleinfo(self,ctx:slash_util.Context,role:discord.Role=None):
        if role is None:
            return await ctx.send("Sorry, you have not selected a role, please try again and this time specify a role.")

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
        embed.set_footer(text=f"Requested by {ctx.author}",icon_url=ctx.author.avatar.url)
        await ctx.send(content=None,embed=embed,view=deletethismessage(ctx.author))



def setup(bot):
    bot.add_cog(Informative(bot))