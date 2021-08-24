import discord
from discord import user
from discord.ext import commands
from discord.ext.commands import Cog
import json

class leveling(commands.Cog):
    '''This cog manages the chat exp system of the bot'''

    def __init__(self,client):
        self.client=client

    async def make_guild_account(self,guild_id : int):
        await self.client.lvldb.execute(f"CREATE TABLE IF NOT EXISTS `{guild_id}` (user_id int PRIMARY KEY,exp int DEFAULT 0,lvl int DEFAULT 0)")
        await self.client.lvldb.commit()
    
    async def make_user_account_in_guild(self,guild_id : int,user_id : int):
        async with self.client.lvldb.execute(f"SELECT * FROM `{guild_id}` WHERE user_id={user_id}") as cursor:
            e=await cursor.fetchall()
            if len(e)==0:   
                await self.client.lvldb.execute(f"INSERT INTO `{guild_id}` (user_id,exp,lvl) VALUES ({user_id},0,0)")
                await self.client.lvldb.commit()

    async def get_exp(self,guild_id:int,user_id:int):
        await self.make_user_account_in_guild(guild_id,user_id)
        async with self.client.lvldb.execute(f"SELECT exp FROM `{guild_id}` WHERE user_id={user_id}") as cursor:
            exp=await cursor.fetchall()
            return exp[0][0]
    
    async def add_exp(self,guild_id : int,user_id : int,amount:int=1):
        exp=await self.get_exp(guild_id,user_id)+amount
        await self.client.lvldb.execute(f" UPDATE `{guild_id}` SET exp={exp} WHERE user_id={user_id}")
        await self.client.lvldb.commit()   

    async def _setlvl(self,guild_id:int,user_id:int,new_lvl:int) :
        await self.client.lvldb.execute(f"UPDATE `{guild_id}` SET lvl={new_lvl} WHERE user_id={user_id}")
        await self.client.lvldb.commit()

    async def _setexp(self,guild_id:int,user_id:int,new_exp:int) :
        await self.client.lvldb.execute(f"UPDATE `{guild_id}` SET exp={new_exp} WHERE user_id={user_id}")
        await self.client.lvldb.commit()

    async def get_lvl(self,guild_id:int,user_id:int):
        xp=await self.get_exp(guild_id,user_id)
        return int(xp/100)


    @commands.Cog.listener()
    async def on_message(self,message):
        if message.guild is None:
            return
        await self.make_guild_account(message.guild.id)
        await self.make_user_account_in_guild(message.guild.id,message.author.id)
        await self.add_exp(message.guild.id,message.author.id)
        
    @commands.command(aliases=['lvl'],description="This command shows your level in the bot's chat leveling system.")
    async def level(self,ctx,user : discord.User=None):
        await self.make_user_account_in_guild(ctx.guild.id,ctx.author.id)
        guild_id=ctx.guild.id
        user_id = ctx.author.id if user is None else user.id
        current_exp=await self.get_exp(guild_id,user_id)
        current_lvl=await self.get_lvl(guild_id,user_id)

        embed=discord.Embed(title="Level", url="https://www.youtube.com/watch?v=dQw4w9WgXcQ",color=discord.Colour.random())
        embed.set_author(name=ctx.author.name)
        embed.add_field(name="Level", value=current_lvl, inline=True)
        embed.add_field(name="Experience", value=current_exp ,inline=True)
        embed.set_footer(text="Those are some wild numbers")
        await ctx.send(embed=embed)

    @commands.command(name="setlvl",description="This command is used to modify a user's level.")
    @commands.has_permissions(manage_roles=True)
    async def setlvl(self,ctx,user : discord.User=None,newlvl : int=None):
        try:
            await self._setlvl(ctx.guild.id,ctx.author.id,newlvl)
            await self._setexp(ctx.guild.id,ctx.author.id,newlvl*100)
            
        except:
            embed=discord.Embed(title="Error on running the command", description="I think you haven't entered all the arguements", color=0xfb0404)
            embed.add_field(name="Correct format", value=f"prefix setlvl @user 100 ", inline=True)
            embed.set_footer(text="Try using the command again with the correct format")
            await ctx.send(embed=embed)
        else:
            current_lvl=await self.get_exp(ctx.guild.id,ctx.author.id)
            current_exp=await self.get_lvl(ctx.guild.id,ctx.author.id)
            content="Successfully set new level, the current stats are.."
            embed=discord.Embed(title="Level", url="https://www.youtube.com/watch?v=dQw4w9WgXcQ",color=discord.Colour.random())
            embed.set_author(name=ctx.author.name)
            embed.add_field(name="Level", value=current_lvl, inline=True)
            embed.add_field(name="Experience", value=current_exp ,inline=True)
            await ctx.send(content=content,embed=embed)

def setup(client):
    client.add_cog(leveling(client))
            