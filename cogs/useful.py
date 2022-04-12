import discord
from discord.ext import commands
from utils.views import *
from utils.converters import Url
import aiohttp
from io import BytesIO
import json

script = """
    splash:set_user_agent('Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/98.0.4758.82 Safari/537.36')
    assert(splash:go(args.url))
    splash:set_viewport_size(1980, 1020)
    assert(splash:wait(1))
    return splash:png()
    """

class Useful(commands.Cog):
    def __init__(self,bot):
        self.bot=bot

    @commands.command(name="msgtodict",aliases=["mtd"])
    async def mtd(self,ctx):
        """Reply to a message with this command to get the message json data"""
        target=ctx.message.reference.resolved
        jsone=await self.bot.http.get_message(channel_id=ctx.channel.id,message_id=target.id)
        if ctx.message.reference:
            if len(str(json.dumps(jsone,indent=4)))<4096:
                e=discord.Embed(title=target.author,description=f"```{json.dumps(jsone,indent=4)}```")
                await ctx.send(embed=e,view=deletethismessage(ctx.author))
            else:
                link=await self.bot.post_to_mystbin(json.dumps(jsone,indent=4))
                await ctx.send(f"Too long, posted to mystbin {link}")
        else:
            await ctx.send("Didn't reply to a message.")

    @commands.command(name="screenshot",aliases=['ss'])
    async def screenshot(self,ctx,url:Url):
        """Take a screenshot of a website"""
        if not url:
            return await ctx.send("Not a valid url.")
        async with ctx.typing():
            dat={'lua_source':script,'url':url}
            async with aiohttp.ClientSession() as session:
                async with session.post('http://0.0.0.0:8050/run',json=dat) as res:
                    dat=await res.read()
            buf=BytesIO(dat)
            e=discord.Embed(title="Your requested screenshot",description=url)
            e.set_image(url='attachment://screenshot.png')
            await ctx.send(embed=e,file=discord.File(fp=buf,filename='screenshot.png'),view=deletethismessage(ctx.author))

        

async def setup(bot):
    await bot.add_cog(Useful(bot))