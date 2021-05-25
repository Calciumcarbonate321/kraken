import discord
from discord import guild
from discord import colour
from discord import message
from discord.colour import Color
from discord.ext import commands
from discord.ext.commands import Cog
import json

class leveling(commands.Cog):
    def __init__(self,client):
        self.client=client

    @commands.Cog.listener()
    async def on_message(self,message):
        with open('data/level.json','r',encoding='utf8') as e:
            data=json.load(e)
        if not message.author.bot:       
            guild_id=str(message.guild.id)
            author_id=str(message.author.id)

            if guild_id not in data:
                data[guild_id]={}

            if author_id not in data[guild_id]:
                data[guild_id][author_id]={'level':0,'exp':0}
            
            data[guild_id][author_id]['exp']+=1
            if data[guild_id][author_id]['exp']%100==0:
                data[guild_id][author_id]['level']+=1
                
            e.close()
            with open('data/level.json','w',encoding='utf8') as r:
                r.write(json.dumps(data,indent=4))
        
    @commands.command(aliases=['lvl'])
    async def level(self,ctx,user : discord.User=None):
        guildid=str(ctx.guild.id)
        if user==None:
            userid=str(ctx.author.id)
        else:
            try:
                userid=str(user.id)
            except:
                await ctx.send("That was not a valid user that you mentioned")
                return
        with open('data/level.json','r',encoding='utf8') as r:
            data=json.load(r)

        if guildid not in data:
            data[guildid]={}
        if userid not in data[guildid]:
            data[guildid][userid]={'level':0,'exp':0}


        current_lvl=data[guildid][userid]['level']
        current_exp=data[guildid][userid]['exp']
        
        embed=discord.Embed(title="Level", url="https://www.youtube.com/watch?v=dQw4w9WgXcQ",color=discord.Colour.random())
        embed.set_author(name=ctx.author.name)
        embed.add_field(name="Level", value=current_lvl, inline=True)
        embed.add_field(name="Experience", value=current_exp ,inline=True)
        embed.set_footer(text="Those are some wild numbers")
        await ctx.send(embed=embed)

    @commands.command(name="setlvl")
    @commands.has_permissions(manage_roles=True)
    async def setlvl(self,ctx,user : discord.User=None,newlvl : int=None):
       
        try:
            guildid=str(ctx.guild.id)
            userid=str(user.id)
            with open('data/level.json','r',encoding='utf8') as r:
                data=json.load(r)

            if guildid not in data:
                data[guildid]={}
            if userid not in data[guildid]:
                data[guildid][userid]={'level':0,'exp':0}

            current_lvl=data[guildid][userid]['level']
            current_exp=data[guildid][userid]['exp']

            data[guildid][userid]['level']=newlvl
            expchange=(newlvl-current_lvl)*100
            data[guildid][userid]['exp']+=expchange
        

            await ctx.send(f"Successfully set the level of {user.name} to {newlvl}")
 
            with open('data/level.json','w',encoding='utf8') as r:
                r.write(json.dumps(data,indent=4))
            

        except:
            prefix=await self.client.get_prefix(message)
            embed=discord.Embed(title="Error on running the command", description="I think you haven't entered all the arguements", color=0xfb0404)
            embed.add_field(name="Correct format", value=f"{prefix} setlvl @user 100 ", inline=True)
            embed.set_footer(text="Try using the command again with the correct format")
            await ctx.send(embed=embed)
            return
        
            



def setup(client):
    client.add_cog(leveling(client))
            