import wavelink
import discord
from discord.ext import commands
from utils import slash_util

class track(wavelink.Track):
    def __init__(self,*args,**kwargs):
        self.requester=kwargs.get("requester")

class Music(slash_util.ApplicationCog):
    """Music cog to hold Wavelink related commands and listeners."""
    def __init__(self, bot: slash_util.Bot):
        super().__init__(bot)
        self.bot = bot

        bot.loop.create_task(self.connect_nodes())

    async def cog_check(self, ctx):
        if not ctx.guild:
            await ctx.send('Music commands are not available in Private Messages.')
            return False
        return True

    async def connect_nodes(self):
        await self.bot.wait_until_ready()

        self.bot.wlink=await wavelink.NodePool.create_node(bot=self.bot,
                                            host='HOST',
                                            port=PORT,
                                            password='PASSWORD')

    @commands.Cog.listener()
    async def on_wavelink_node_ready(self, node: wavelink.Node):
        print(f'Node: <{node.identifier}> is ready!')

    @commands.Cog.listener()
    async def on_wavelink_track_start(self,player:wavelink.Player,track:wavelink.Track):
        await player.tchannel.send(f"Started playing {track}")

    @commands.Cog.listener()
    async def on_wavelink_track_end(self,player:wavelink.Player,track:wavelink.Track,reason):
        if reason!="FINISHED":
            return
        nt=player.queue.get()
        await player.play(nt)

    @slash_util.slash_command(name="play",description="Play a song with the given search query.If not connected, connect to our voice channel.",guild_id=903535543491624980)
    async def play(self, ctx:slash_util.Context,track:str):
        search=await wavelink.YouTubeTrack.search(query=track,return_first=True)
        if not ctx.voice_client:
            vc: wavelink.Player = await ctx.author.voice.channel.connect(
                cls=wavelink.Player)
        else:
            vc: wavelink.Player = ctx.voice_client
        vc.tchannel=ctx.channel
        search.requester=ctx.author
        if not vc.is_playing():
            await vc.play(search)
            return
        vc.queue.put(search)
        await ctx.send(f"Added {search} to the queue.")
    
    @commands.group(name="queue",aliases=["q"],help="Displays the current queue.")
    async def q(self,ctx):
        p=self.bot.wlink.get_player(ctx.guild)
        qstr=str()
        for i in p.queue:
            qstr+=(i.title+"\n")
        await ctx.send(qstr)

    @q.command(name="clear",help="Clears the queue.")
    async def cq(self,ctx):
        p=self.bot.wlink.get_player(ctx.guild)
        p.queue.clear()
        await ctx.send("Cleared the queue.")

    @slash_util.slash_command(name="seek",description="Seeks the audio track that is being played.",guild_id=903535543491624980)
    async def seek(self,ctx:slash_util.Context,position_in_seconds:int):
        p=self.bot.wlink.get_player(ctx.guild)
        await p.seek(position_in_seconds)

    @slash_util.slash_command(name="volume",description="Increases/decreases the volume, give any value between 0 and 1000.",guild_id=903535543491624980)
    async def volume(self,ctx:slash_util.Context,volume:slash_util.Range(1,1000)):
        p=self.bot.wlink.get_player(ctx.guild)
        await p.set_volume(volume)
        await ctx.send(f"Successfully set volume to {volume}")

    @slash_util.slash_command(name="now_playing",description="Shows the current playing audio.",guild_id=903535543491624980)
    async def np(self,ctx:slash_util.Context):
        p=self.bot.wlink.get_player(ctx.guild)
        embed=discord.Embed(title="Now playing",color=discord.Colour.random())
        embed.add_field(name="Track name",value=p.track)
        embed.add_field(name="Track link",value=f"[Click here]({p.track.uri})")
        embed.set_thumbnail(url=p.track.thumb)
        embed.set_footer(text=f"Requested by {p.track.requester}")
        await ctx.send(embed=embed)

    @slash_util.slash_command(name="skip",description="Skips the current audio.",guild_id=903535543491624980)
    async def _skip(self,ctx):
        p=self.bot.wlink.get_player(ctx.guild)
        nt=p.queue.get()
        await p.play(nt)
        await ctx.send(f"now playing {nt}")

    @slash_util.slash_command(name="stop",description="Stops the player and clears the queue.",guild_id=903535543491624980)
    async def stop(self,ctx):
        player=self.bot.wlink.get_player(ctx.guild)
        await player.stop() 
        player.queue.clear()
        await ctx.send("Successfully stopped.")

    @slash_util.slash_command(name="pause",description="Pauses the player, can be resumed later.",guild_id=903535543491624980)
    async def pause(self,ctx):
        player=self.bot.wlink.get_player(ctx.guild)
        if player.is_paused():
            return await ctx.send("Player is already paused.")
        await player.pause()
        await ctx.send("Successfully paused.")   

    @slash_util.slash_command(name="resume",description="Resumes a paused player.",guild_id=903535543491624980)
    async def resume(self,ctx):
        player=self.bot.wlink.get_player(ctx.guild)
        if not player.is_paused():
            return await ctx.send("The player is not paused.")
        await player.resume()
        await ctx.send("Successfully resumed.") 

    @slash_util.slash_command(name="disconnect",description="Disconnects the bot from the vc.",guild_id=903535543491624980)
    async def discon(self,ctx):
        player=self.bot.wlink.get_player(ctx.guild)
        await player.disconnect(force=True)
        await ctx.send("Successfully disconnected :+1:")
    
    

def setup(client):
    client.add_cog(Music(client))
