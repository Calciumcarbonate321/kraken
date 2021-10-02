import discord
from discord.errors import HTTPException
from discord.ext import commands
import aiohttp
import urllib

class Utility(commands.Cog):
    def __init__(self,client):
        self.client=client

    @commands.group(name="qr",aliases=["qrcode"],invoke_without_command=True)
    async def qr(self,ctx):
        await ctx.send("You have 2 options, either choose read or create option, for eg: >qr read <qrcode link> will read the qr code and return its contents")
    
    @qr.command()
    async def read(self,ctx,qr_link=None):
        msg=await ctx.send("Processing...")
        if qr_link is None:
            qr_link=ctx.message.attachments[0].url
        qr_l=urllib.parse.quote(qr_link)
        link="https://api.qrserver.com/v1/read-qr-code/?fileurl="+qr_l
        async with aiohttp.request("GET",link) as r:
            e=await r.read()
        data=e.decode('utf-8')
        a=data.replace('null','None')
        content=eval(a)
        qrcontent=content[0]['symbol'][0]['data']
        embed=discord.Embed(title="Your requested QR code decryption",description="I use an api to read the qr code,[their website](https://goqr.me/)")
        embed.add_field(name="Content",value=qrcontent)
        embed.set_footer(text=f"Requested by {ctx.author}",icon_url=ctx.author.avatar_url)
        try:
            await msg.edit(embed=embed)
        except HTTPException:
            await msg.edit(content="You haven't provided a valid qr code.")


    @qr.command()
    async def create(self,ctx,*,qr_content:str=None):
        if qr_content is None:
            await ctx.send("You didn't give any content to embed into a qr code.(it should be either a link or a text or a combination of both)")
            return
        qr_c=urllib.parse.quote(qr_content)
        link=f"http://api.qrserver.com/v1/create-qr-code/?data={qr_c}&size=256x256"
        embed=discord.Embed(title="Your requested QR code",description="I use an api to generate the qr code,[their website](https://goqr.me/)")
        embed.set_image(url=link)
        embed.set_footer(text=f"Requested by {ctx.author}",icon_url=ctx.author.avatar_url)
        await ctx.send(embed=embed)
  

def setup(client):
    client.add_cog(Utility(client))
