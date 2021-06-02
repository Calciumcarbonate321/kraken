import discord
from discord import guild
from discord.ext import commands
from discord.ext.commands import Cog
from prsaw import RandomStuff
import json



class aibot(commands.Cog):
    def __init__(self,client):
        self.client=client
        self.rs=RandomStuff(async_mode=True,api_key="WIZjeeP9Qz0u")

    @commands.command(name="setaichannel",description="This command is used to set an ai channel for the server.") 
    @commands.has_permissions(administrator=True)
    async def setaichannel(self,ctx,channel :discord.TextChannel=None):
        ai_channel_id=channel.id
        with open('data/aichannel.json','r',encoding='utf8') as r:
            data=json.load(r)
            if ai_channel_id in data:
                await ctx.send("A channel has already been setup in this server")   
            else:           
                data.append(ai_channel_id)
                await ctx.send("Done")

        with open('data/aichannel.json','w',encoding='utf8') as r:
            r.write(json.dumps(data,indent=4))

        

    @commands.Cog.listener()
    async def on_message(self,message):
        Message=str(message.content)
        with open('data/aichannel.json','r',encoding='utf8') as r:
            data=json.load(r)
        if message.channel.id not in data:
            return
        if message.author.id==843071820878184458:
            return
        channel=self.client.get_channel(message.channel.id)
        async with message.channel.typing():
            response=await self.rs.get_ai_response(Message)
        await channel.send(response)
        await self.client.process_commands(message)

def setup(client):
    client.add_cog(aibot(client))