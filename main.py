import discord
from datetime import datetime
from config import *
from datetime import timezone
from utils import slash_util
import aiohttp
from discord.ext import commands
from discord import app_commands
from utils.views import *
from io import BytesIO
import asyncio

class Bot(commands.Bot):
    def __init__(self,*args,**kwargs):
        super().__init__(*args,**kwargs)
        self.starttime = datetime.now(timezone.utc)
        self.botcogs=["cogs.info","cogs.music","jishaku","cogs.useful","cogs.secret","cogs.reminder","cogs.errors","cogs.gameboy"]

    async def on_ready(self):
        print("Logged in as",self.user)

    async def load_cogs(self):
        for i in self.botcogs:
            await self.load_extension(i)
            print(f"Loaded {i}")

    async def get_invite(self):
        return "https://discord.com/api/oauth2/authorize?client_id=843071820878184458&permissions=415797472576&scope=bot"

    async def post_to_mystbin(self, data):
        data = bytes(data, 'utf-8')
        async with aiohttp.ClientSession() as cs:
            async with cs.post('https://mystb.in/documents', data = data) as r:
                res = await r.json()
                key = res["key"]
                return f"https://mystb.in/{key}"


bot=Bot(command_prefix="plz ",intents=discord.Intents.all())

@commands.is_owner()
@bot.command(name="sync")
async def sync(ctx,option=None):
    e = (await bot.tree.sync(guild=discord.Object(id=TESTING_GUILD_ID)) if option else await bot.tree.sync())
    e=discord.Embed(title="Successfully synced the following commands:",description=[i.name for i in e],color=0xdfa3ff)
    await ctx.send(embed=e)

@app_commands.context_menu(name="User Info")
async def userinfo(interaction,user:discord.Member):
    if isinstance(interaction.channel,discord.DMChannel):
        view=discord.ui.View()
        view.add_item(invitebutton())
        return await interaction.response.send_message("Sorry this command cannot be used in a dm channel, invite me to your server to use this.",view=view)
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
        embed.add_field(
            name=f"Roles [{len(user.roles) - 1}]",
            value=role_string,
            inline=False,
        )

    perm_string = ', '.join(
        str(p[0]).replace("_", " ").title()
        for p in user.guild_permissions
        if p[1]
    )

    embed.add_field(name="Guild permissions", value=perm_string, inline=False)
    embed.set_footer(text=f'ID: {str(user.id)}')
    view=deletethismessage(interaction.user)
    await interaction.response.send_message(content=None,embed=embed,view=view)

@app_commands.context_menu(name="Steal Avatar")
async def stealavatar(interaction,user:discord.Member):
    avurl=user.avatar.url
    async with aiohttp.ClientSession() as s:
        async with s.get(url=avurl) as res:
            c=await res.read()
            img=BytesIO(c)
    e=await interaction.user.send(file=discord.File(fp=img,filename="avatar.png"))
    await interaction.response.send_message(content=f"[check your dms]({e.jump_url})",ephemeral=True)
    
asyncio.run(bot.load_cogs())
bot.run(BOT_TOKEN)
