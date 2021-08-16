import discord
from discord import guild
from discord.ext import commands
from discord_slash import cog_ext
from discord_slash.context import MenuContext,SlashContext
from discord_slash.model import ContextMenuType

class Cmenus(commands.Cog):
    def __init__(self,client):
        self.client=client
    
    guild_ids=[752757415224672326]

    @cog_ext.cog_slash(name="prefix",guild_ids=guild_ids)
    async def slash_help(self,ctx:SlashContext):
        await ctx.send(f"My prefix is {self.client.get_prefix(ctx.message)}")
    
    @cog_ext.cog_context_menu(name="userinfo",target=ContextMenuType.MESSAGE,guild_ids=guild_ids)
    async def get_user_info(self,ctx: MenuContext):
        user=ctx.target_message.author
        date_format = "%a, %d %b %Y %I:%M %p"
        embed = discord.Embed(color=0xdfa3ff, description=user.mention)
        embed.set_author(name=str(user), icon_url=user.avatar_url)
        embed.set_thumbnail(url=user.avatar_url)
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
        await ctx.send(embed=embed)

    @cog_ext.cog_context_menu(name="savemsg",target=ContextMenuType.MESSAGE,guild_ids=guild_ids)
    async def savemsg(self,ctx : MenuContext):
        msg=ctx.target_message
        embeds=msg.embeds
        stickers=msg.stickers
        await ctx.author.send(content=f"{msg.author} said :`{msg.content}`, the embeds(if any) in it are sent below:")
        for i in embeds:
            await ctx.author.send(embed=i)  
        

    
def setup(client):
    client.add_cog(Cmenus(client))
