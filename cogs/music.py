import wavelink
import discord
from discord.ext import commands

class track(wavelink.Track):
    def __init__(self,*args,**kwargs):
        self.requester=kwargs.get("requester")

class Music(commands.Cog):
    """Music cog to hold Wavelink related commands and listeners."""
    def __init__(self, bot: commands.Bot):
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
                                            host='lava.link',
                                            port=80,
                                            password='anything as a password')

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

    @commands.command(name="play",aliases=["p"],help="Play a song with the given search query.If not connected, connect to our voice channel.")
    async def play(self, ctx, *,search:wavelink.YouTubeTrack):
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
        await ctx.message.add_reaction("👌")
        await ctx.send("Cleared the queue.")

    @commands.command(name="seek",help="Seeks the audio track that is being played.")
    async def seek(self,ctx,position_in_seconds:int):
        p=self.bot.wlink.get_player(ctx.guild)
        await p.seek(position_in_seconds)

    @commands.command(name="volume",help="Increases/decreases the volume, give any value between 0 and 1000.")
    async def volume(self,ctx,volume:int):
        p=self.bot.wlink.get_player(ctx.guild)
        await p.set_volume(volume)

    @commands.command(name="now_playing",aliases=["np"],help="Shows the current playing audio.")
    async def np(self,ctx):
        p=self.bot.wlink.get_player(ctx.guild)
        embed=discord.Embed(title="Now playing",color=discord.Colour.random())
        embed.add_field(name="Track name",value=p.track)
        embed.add_field(name="Track link",value=f"[Click here]({p.track.uri})")
        embed.set_thumbnail(url=p.track.thumb)
        embed.set_footer(text=f"Requested by {p.track.requester}")
        await ctx.send(embed=embed)

    @commands.command(name="skip",aliases=["next"],help="Skips the current audio.")
    async def _skip(self,ctx):
        p=self.bot.wlink.get_player(ctx.guild)
        nt=p.queue.get()
        await p.play(nt)
        await ctx.send(f"now playing {nt}")

    @commands.command(name="stop",help="Stops the player and clears the queue.")
    async def stop(self,ctx):
        player=self.bot.wlink.get_player(ctx.guild)
        await player.stop() 
        player.queue.clear()
        await ctx.message.add_reaction("👌")
        await ctx.send("Successfully stopped.")

    @commands.command(name="pause",help="Pauses the player, can be resumed later.")
    async def pause(self,ctx):
        player=self.bot.wlink.get_player(ctx.guild)
        if player.is_paused():
            return await ctx.send("Player is already paused.")
        await player.pause()
        await ctx.message.add_reaction("👌")
        await ctx.send("Successfully paused.")   

    @commands.command(name="resume",help="Resumes a paused player.")
    async def resume(self,ctx):
        player=self.bot.wlink.get_player(ctx.guild)
        if not player.is_paused():
            return await ctx.send("The player is not paused.")
        await player.resume()
        await ctx.message.add_reaction("👌")
        await ctx.send("Successfully resumed.") 

    @commands.command(name="disconnect",help="Disconnects the bot from the vc.")
    async def discon(self,ctx):
        player=self.bot.wlink.get_player(ctx.guild)
        await player.disconnect(force=True)
        await ctx.message.add_reaction("👌")
        await ctx.send("Successfully disconnected :+1:")
    
    

def setup(client):
    client.add_cog(Music(client))
