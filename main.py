import discord
from discord.ext import commands
from discord import Colour
from discord.ext.commands.core import has_guild_permissions, has_permissions, is_owner
import json

intents = discord.Intents.default()
intents.members = True

def get_prefix(client, message):
    try:
        with open('data/config.json', 'r',encoding='utf8') as r:
            prefixes = json.load(r)
            return prefixes[str(message.guild.id)]
        
    except KeyError: 
        with open('data/config.json', 'r',encoding='utf8') as k:
            prefixes = json.load(k)
        prefixes[str(message.guild.id)] = '>'

        with open('data/config.json', 'w',encoding='utf8') as j:
            j.write(json.dumps(prefixes,indent=4))

        with open('data/config.json', 'r',encoding='utf8') as t:
            prefixes = json.load(t)
            return prefixes[str(message.guild.id)]
        
    except: 
        return '>'

client=commands.Bot(command_prefix=(get_prefix),case_insensitive=True)


@client.event
async def on_ready():
    print("ready")

@client.command(name="ping")
async def ping(ctx):
    embed=discord.Embed(name="Client latency",descrption="This command shows the latency of the bot.",color=discord.Colour.random())
    embed.add_field(name="Client latency",value="Client latency is the time taken by the bot to respond to your command")
    embed.add_field(name="Latency",value=f"{round(client.latency*1000)}ms")
    embed.set_footer(text="Hello there",icon_url=ctx.author.avatar_url)
    await ctx.send(embed=embed)

def load_cogs():
    cogs=[
            "cogs.bank",
            "cogs.moneymaking",
            "cogs.level",
            "cogs.shopsys",
            "cogs.help",
            "cogs.fun"  
    ]
    for i in cogs:
        client.load_extension(i)

@client.command()
@is_owner()
async def load(ctx,ext):
    try:
        client.load_extension(f"cogs.{ext}")
        await ctx.send(f"{ext} cog successfully loaded.")
    except:
        await ctx.send(f"{ext} is not a valid cog name.")

@client.command()
@is_owner()
async def unload(ctx,ext):
    try:
        client.unload_extension(f"cogs.{ext}")
        await ctx.send(f"{ext} cog successfully unloaded.")
    except:
        await ctx.send(f"{ext} is not a valid cog name.")

@client.command(aliases=['re'])
@is_owner()
async def reload(ctx,ext):
    try:
        client.unload_extension(f"cogs.{ext}")
        client.load_extension(f"cogs.{ext}")
        await ctx.send(f"{ext} cog has been successfully reloaded.")
    except:
        await ctx.send(f"{ext} is not a valid cog name.")  

@client.command(aliases=['setprefix','changeprefix'])      
@has_permissions(administrator=True)
async def prefix(ctx,prefix : str):
    with open('data/config.json','r',encoding='utf8') as r:
        data=json.load(r)
        new_prefix=prefix
        data[str(ctx.guild.id)]=str(new_prefix)
    with open('data/config.json','w',encoding='utf8') as r:
        r.write(json.dumps(data,indent=4))
        await ctx.send(f"Success, new prefix is {prefix}")

@client.event
async def on_message(message):
    if client.user.mentioned_in(message):
        await message.channel.send(f"My prefix in this server is {await client.get_prefix(message)}")
    await client.process_commands(message)



load_cogs()       

client.run('ODQzMDcxODIwODc4MTg0NDU4.YJ-h0Q.Vu_FtWbUpKluG0mISjUR7XL2DGs')    
