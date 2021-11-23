from datetime import datetime
import discord
from discord import invite
from discord.ext import commands
from utils import slash_util
from utils.views import *

class Informative(slash_util.ApplicationCog,name="Informative"):
    def __init__(self,bot:slash_util.Bot):
        super().__init__(bot)
        self.bot=bot

    @slash_util.slash_command(name="about",description="A command about me")
    async def aboutme(self,ctx:slash_util.Context):
        embed=discord.Embed(title="About me",description="Hi I am a multipurpose discord bot made by CaCO3#9990",color=discord.Colour.random())
        embed.add_field(name="Latency",value=round(self.bot.latency*1000))
        c=datetime.utcnow()
        elapsed=c-self.bot.starttime
        seconds = elapsed.seconds
        minutes, seconds = divmod(seconds, 60)
        hours, minutes = divmod(minutes, 60)        
        embed.add_field(name="Uptime",value="{}d {}h {}m {}s".format(elapsed.days, hours, minutes, seconds),inline=False)
        view=discord.ui.View()
        view.add_item(invitebutton())
        view.add_item(sourcebutton())
        await ctx.send(content="Hello there",embed=embed,view=view)

    @slash_util.slash_command(name="thisone",guild_id=800701747407880193)
    @slash_util.describe(optione="option to be sent")
    @slash_util.describe(optionee="option to be dmed")
    async def thisones(self,ctx:slash_util.Context,optione:str,optionee:str):
        await ctx.send(optione)
        await ctx.author.send(optionee)
        
    @slash_util.slash_command(name="userinfo",description="Gives you information about a member in your server.",guild_id=903535543491624980)
    async def userinfo(self,ctx:slash_util.Context, user: discord.Member = None): 
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
        await ctx.send(embed=embed,view=view)


def setup(bot):
    bot.add_cog(Informative(bot))