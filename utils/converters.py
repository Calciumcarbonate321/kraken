import discord
from discord.ext import commands
import re

urlregex = re.compile(
        r'^(?:http)s?://' 
        r'(?:(?:[A-Z0-9](?:[A-Z0-9-]{0,61}[A-Z0-9])?\.)+(?:[A-Z]{2,6}\.?|[A-Z0-9-]{2,}\.?)|' 
        r'localhost|'
        r'\d{1,3}\.\d{1,3}\.\d{1,3}\.\d{1,3})' 
        r'(?::\d+)?' 
        r'(?:/?|[/?]\S+)$', re.IGNORECASE)

class Url(commands.Converter):
    async def convert(self,ctx,url):
        return (url if re.match(urlregex,url) else None)
