import discord
from discord.ext import commands
import aiohttp
from io import BytesIO
from utils import slash_util
from utils.views import *

class Usercommands(slash_util.ApplicationCog):
    def __init__(self, bot: slash_util.Bot):
        super().__init__(bot)
        self.bot=bot
        
    @slash_util.user_command(name="user_info")
    async def uinfo(self,ctx:slash_util.Context,user:discord.Member):
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

    @slash_util.user_command(name="steal avatar")
    async def stealavatar(self,ctx:slash_util.Context,user:discord.Member):
        avurl=user.avatar.url
        async with aiohttp.ClientSession() as s:
            async with s.get(url=avurl) as res:
                c=await res.read()
                img=BytesIO(c)
        e=await ctx.author.send(file=discord.File(fp=img,filename="avatar.png"))
        await ctx.send(content=f"[check your dms]({e.jump_url})",ephemeral=True)


def setup(bot):
    bot.add_cog(Usercommands(bot))