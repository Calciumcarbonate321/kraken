import discord
from discord.ext import commands
import asyncpraw
from utils import slash_util

class RedditCog(slash_util.ApplicationCog):
    def __init__(self,bot:slash_util.Bot):
        super().__init__(bot)
        self.bot=bot
