import discord
from discord.ext import commands
from discord.ext.commands.context import Context
import wavelink
import asyncio
from discord.ui import Button, View
import aiohttp
from utils.musicutils import LyricsView,NowPlayingView,PlayView,MyPlayer
import datetime
from wavelink.ext import spotify
import re
from utils import slash_util
from config import MUSIC_HOST,MUSIC_HOST_PORT,MUSIC_HOST_PWD,SPOTIFY_CLIENT_ID,SPOTIFY_CLIENT_SECRET

class Music(slash_util.ApplicationCog):
	def __init__(self,bot:slash_util.Bot):
		super().__init__(bot)
		self.bot:commands.Bot = bot
		self.menotconnected = 'I am not connected to a voice channel'
		self.unotconnected = 'You are not connected to the voice channel I am in '
		self.notplaying =  'The bot is not playing anything currently'

	@commands.Cog.listener()
	async def on_ready(self):
		print('Music Ready!')
		self.bot.wavelink = await wavelink.NodePool.create_node(bot=self.bot,
									host=MUSIC_HOST,
									port=MUSIC_HOST_PORT,
									password=MUSIC_HOST_PWD,
									spotify_client=spotify.SpotifyClient(client_id=SPOTIFY_CLIENT_ID, client_secret=SPOTIFY_CLIENT_SECRET))

	async def embifier(self,success,content=None,title=''):
		if success:
			color = discord.Color.green()
			emoj = '<a:check_ravena:930704225451798529>'
		else:
			color = discord.Color.red()
			emoj = "<a:cross_ravena:930704070942007316>"
		emb = discord.Embed(
			title = title,
			description= emoj+' | '+content,
			color = color
		)
		return emb

	@commands.Cog.listener()
	async def on_voice_state_update(self, member, before, after):
		if member.id != self.bot.user.id:
			return

		if after.channel is None:
			vc:MyPlayer = self.bot.wavelink.get_player(before.channel.guild)
			if vc is None:
				return
			if vc.queue.is_empty:
				pass
			else:
				vc.queue.clear()
			await vc.stop()
			await vc.disconnect(force=True)
			delattr(vc,'cmdchannel')
			delattr(vc,'loop')
			return

		if before.channel is None:
			vc:MyPlayer = self.bot.wavelink.get_player(after.channel.guild)
			i = 0
			while True:
				await asyncio.sleep(1)
				i += 1
				if vc.is_playing() and len(after.channel.members) > 1:
					i = 0
				if i == 60:
					if vc.queue.is_empty:
						pass
					else:
						vc.queue.clear()
					await vc.disconnect(force = True)
					await vc.cmdchannel.send(embed = await self.embifier(False,content = 'Disconnected for being inactive for more than a minute'))
					delattr(vc,'cmdchannel')
					delattr(vc,'loop')
				if not vc.is_connected():
					break

	@commands.Cog.listener()
	async def on_wavelink_track_end(self,player:MyPlayer,track,reason):
		if reason != 'FINISHED':
			return

		if player.loop == 'single':
			return await player.play(track,replace = True)

		if player.queue.is_empty:
			try:
				await player.stop()
				return
			except:
				return

		if player.loop == 'queue':
			song =  player.queue.get()
			player.queue.put(track)
			while song.length > 600:
				await player.cmdchannel(embed = await self.embifier(False,content = f'{song.title} was longer than 10 mins, so skipping that song and moved on to the other (if any)'))
				song =  player.queue.get()
			await player.play(song,replace = True)

		if player.loop == 'none':
			song =  player.queue.get()
			while song.length > 600:
				await player.cmdchannel(embed = await self.embifier(False,content = f'{song.title} was longer than 10 mins, so skipping that song and moved on to the other (if any)'))
				song =  player.queue.get()
			await player.play(song,replace = True)

	@commands.Cog.listener()
	async def on_wavelink_track_start(self,player:MyPlayer,track):
		if not player.is_connected():
			await player.stop()
			delattr(player,'cmdchannel')
			delattr(player,'loop')
		await player.cmdchannel.send(embed = await self.embifier(True,content = f'Started playing - **{track.title}**'))

	@commands.command(name = 'join')
	async def join_msg(self,ctx:Context):
		"""Joins the voice channel you are in"""
		if ctx.author.voice is None or ctx.author.voice.channel is None:
			return await ctx.message.reply(embed = await self.embifier(False,content = f'You are not connected to any voice channel'))
		vc:MyPlayer = self.bot.wavelink.get_player(ctx.guild)
		if vc is None:
			vc:MyPlayer = await ctx.author.voice.channel.connect(cls = MyPlayer)
			vc.cmdchannel = ctx.channel
			vc.loop = 'none'
			await ctx.message.reply(embed = await self.embifier(True,content = f'Connected to {ctx.author.voice.channel.mention}'))
			return vc
		if vc.is_connected():
			return await ctx.message.reply(embed = await self.embifier(False,content = f'I am already connected to a voice channel {vc.channel.mention}'))

	@commands.command(name = 'leave')
	async def leave(self,ctx:Context):
		"""Leaves the voice channel"""
		vc:MyPlayer = self.bot.wavelink.get_player(ctx.guild)
		if vc is None or not vc.is_connected():
			return await ctx.message.reply(embed = await self.embifier(False,content = self.menotconnected))

		if ctx.author.voice is None or ctx.author.voice.channel is None or vc.channel.id != ctx.author.voice.channel.id:
			return await ctx.message.reply(embed = await self.embifier(False,content = self.unotconnected + vc.channel.mention))	

		if vc.channel.id == ctx.author.voice.channel.id:
			if vc.queue.is_empty:
				pass
			else:
				vc.queue.clear()
			delattr(vc,'cmdchannel')
			delattr(vc,'loop')
			await vc.disconnect(force=True)
			return await ctx.message.reply(embed = await self.embifier(True,content = 'Disconnected'))

	@commands.command(name = 'play')
	@commands.cooldown(1, 5, commands.BucketType.member)
	async def play(self,ctx:Context,*,query:str):
		"""Plays any song with the given name or spotify url."""
		if ctx.author.voice is None or ctx.author.voice.channel is None:
			return await ctx.message.reply(embed = await self.embifier(False,content = 'You are not connected to a voice channel'))
		vc:MyPlayer = self.bot.wavelink.get_player(ctx.guild)
		if vc is None or not vc.is_connected():
			vc:MyPlayer = await ctx.author.voice.channel.connect(cls = MyPlayer)
			vc.cmdchannel = ctx.channel
			vc.loop = 'none'
			await ctx.message.reply(embed = await self.embifier(True,content = f'Connected to {ctx.author.voice.channel.mention}'))
		if vc.channel.id != ctx.author.voice.channel.id:
			return await ctx.message.reply(embed = await self.embifier(False,content = self.unotconnected + vc.channel.mention))
		try:
			if re.match('^https://open.spotify.com/(playlist|track|album)/',query):
				async with aiohttp.request("GET",query,headers = {}) as resp:
					if resp.status == 404 and not query.startswith('https://open.spotify.com/playlist') and not query.startswith('https://open.spotify.com/album'):
						return await ctx.message.reply(embed = await self.embifier(False,content = 'Pls provide a valid spotify url'))
				if vc.is_playing() and vc.loop == 'single':
					return await ctx.message.reply('The queue is set to single so can\'t add to queue')
				if query.startswith('https://open.spotify.com/track/'):
					if vc.is_playing() and vc.loop == 'single':
						return await ctx.message.reply(embed = await self.embifier(False,content = f'The loop is set to single so can\'t add the song to queue'))
					track = await spotify.SpotifyTrack.search(query=query, return_first=True)
					if track.length > 600:
						return await ctx.message.reply(embed = await self.embifier(False,content = f'That song is more than 10 mins long'))
					if not vc.is_playing():
						return await vc.play(track)
					else:
						vc.queue.put(track)
						return await ctx.message.reply(embed = await self.embifier(True,content = f'Added **{track.title}** to the queue '))
				if query.startswith('https://open.spotify.com/playlist') or query.startswith('https://open.spotify.com/album'):
					if vc.is_playing() and vc.loop == 'single':
						return await ctx.message.reply(embed = await self.embifier(False,content = f'The loop is set to single so can\'t add the song to queue'))
					added = 0
					total = 0
					tracks = await spotify.SpotifyTrack.search(query=query)
					for track in tracks:
						if total == 21:
							await ctx.message.reply(embed = await self.embifier(True,content = f'Added {added} tracks to the queue.(Stopped adding the rest of them as we only support upto 20 songs)'))
							break
						if vc.is_playing() == False:
							added +=1
							await vc.play(track)
						else:
							added +=1
							vc.queue.put(track)
						total += 1
					return await ctx.message.reply(embed = await self.embifier(True,content = f'Added {added} tracks to the queue.'))
			else:
				tracks = await wavelink.YouTubeTrack.search(query = query)
				if tracks is None:
					return await ctx.message.reply(embed = await self.embifier(False,content = 'There are no songs by that name'))

				emb = discord.Embed(title = 'Choose which song you want to play',description='Do it under 30 seconds',color = discord.Color.random())
				try:
					emb.set_thumbnail(url = tracks[0].thumb)
				except:
					pass
				emb.set_author(name = ctx.author.name,icon_url=ctx.author.display_avatar)
				view = PlayView(timeout = 30,ctx=ctx,vc=vc,tracks = tracks)

				msg = await ctx.message.reply(embed = emb,view = view)
				check = await view.wait()
				if check == True:
					try:
						return await msg.edit(content = f'This message has timed out because {ctx.author.mention} did not select which song to play in 30 seconds.Try again',view=None,embed=None)
					except:
						return				
		except Exception as e:
			return await ctx.message.reply(embed = await self.embifier(False,content = f'Some error occured\n {e}'))			

	@commands.command(name = 'queue')
	async def queue(self,ctx:Context):
		"""Shows the queue for the server"""
		vc:MyPlayer = self.bot.wavelink.get_player(ctx.guild)

		if vc is None or not vc.is_connected():
			return await ctx.message.reply(embed = await self.embifier(False,content = self.menotconnected))
		if vc.queue.is_empty:
			return await ctx.message.reply(embed = await self.embifier(False,content = 'The queue is empty'))

		emb = discord.Embed(title = 'This server\'s queue:',color = discord.Color.random())
		i=1
		for track in vc.queue:
			if i == 1:
				try:
					emb.set_thumbnail(url = track.thumb)
				except AttributeError:
					pass
			emb.add_field(name = f'{i}- **{track.title}**',value = f'{datetime.timedelta(seconds=round(track.length))}',inline = False)
			i+=1
		emb.set_author(name = ctx.author.name,icon_url=ctx.author.display_avatar)
		await ctx.message.reply(embed = emb)

	@commands.command(name = 'skip')
	async def skip(self,ctx:Context):
		"""Skips the current playing song"""
		vc:MyPlayer = self.bot.wavelink.get_player(ctx.guild)
		if vc is None or not vc.is_connected():
			return await ctx.message.reply(embed = await self.embifier(False,content = self.menotconnected))

		if not vc.is_playing():
			return await ctx.message.reply(embed = await self.embifier(False,content = self.notplaying))

		if ctx.author.voice is None or ctx.author.voice.channel is None or vc.channel.id != ctx.author.voice.channel.id:
			return await ctx.message.reply(embed = await self.embifier(False,content = self.unotconnected + vc.channel.mention))

		if vc.loop == 's' or vc.loop == 'single':
			await vc.seek(position = 0)
			return await ctx.message.reply(embed = await self.embifier(True,content = 'Skipped!'))

		if vc.queue.is_empty:
			return await ctx.message.reply(embed = await self.embifier(False,content = 'The queue is empty'))

		if vc.loop == 'q' or vc.loop == 'queue':
			song =  vc.queue.get()
			vc.queue.put(vc.track)
			await vc.stop()
			await vc.play(song,replace = True)

		if vc.loop == 'n' or vc.loop == 'none':
			song =  vc.queue.get()
			await vc.stop()
			await vc.play(song,replace = True)

		await ctx.message.reply(embed = await self.embifier(True,content = 'Skipped!'))

	@commands.command(name = 'now_playing',aliases = ['np'])
	@commands.cooldown(1, 5, commands.BucketType.member)
	async def np(self,ctx:Context):
		"""Gives information about the currently playing song"""
		vc:MyPlayer = self.bot.wavelink.get_player(ctx.guild)

		if vc is None or not vc.is_connected():
			return await ctx.message.reply(embed = await self.embifier(False,content = self.menotconnected))
		if not vc.is_playing():
			return await ctx.message.reply(embed = await self.embifier(False,content = self.notplaying))
		if ctx.author.voice is None or ctx.author.voice.channel is None or vc.channel.id != ctx.author.voice.channel.id:
			return await ctx.message.reply(embed = await self.embifier(False,content = self.unotconnected + vc.channel.mention))

		if vc.is_paused():
			paused = 'Paused'
		if not vc.is_paused():
			paused = 'Playing'
		if vc.loop == 'single':
			loopvalue = 'Single'
		if vc.loop == 'queue':
			loopvalue = 'Queue'
		if vc.loop == 'none':
			loopvalue = 'None'
		emb = discord.Embed(title = 'This server\'s music status',color = discord.Color.teal())
		try:
			emb.set_image(url = vc.track.thumb)
		except:
			pass
		current = datetime.timedelta(seconds=round(vc.position))
		total = datetime.timedelta(seconds=round(vc.track.length))
		emb.add_field(name = '<a:playing:936587336383336538> Title:',value = f'**{vc.track.title}**')
		emb.add_field(name = '<a:timeline:936583271557521419> Duration:',value = f'{total}')
		emb.add_field(name = '✍️ Author:',value = vc.track.author)
		emb.add_field(name = '🔗 Url:',value = vc.track.info['uri'])
		emb.add_field(name = '<a:timeline:936583271557521419> Timeline',value = f'{current} / {total}')
		emb.add_field(name = '⏯️ Playing/Paused:',value = paused)
		emb.add_field(name = '<a:player:936579719741210635> Queue count:',value = vc.queue.count)
		emb.add_field(name = '<a:playing:936587336383336538> Loop:',value = loopvalue)
		volume = vc.volume
		if volume == 0:
			volume = 'Muted'
		emb.add_field(name = '🔊 Volume:',value = volume)
		emb.set_author(name = ctx.author.name,icon_url=ctx.author.display_avatar)
		view = NowPlayingView(timeout=None,ctx=ctx,vc=vc)
		msg = await ctx.send(embed = emb,view = view)
		check = await view.wait()
		diabledview = View(timeout = 1)
		button1 = Button(label = 'Play/Pause',disabled = True,style=discord.ButtonStyle.blurple,emoji = '⏯️')
		button2 = Button(label = 'Skip',disabled = True,style=discord.ButtonStyle.red)
		button3 = Button(label = 'Rewind',disabled = True,style=discord.ButtonStyle.blurple)
		button4 = Button(label = 'Mute',disabled = True,style=discord.ButtonStyle.red)
		button5 = Button(label = 'Loop',disabled = True,style=discord.ButtonStyle.blurple)
		diabledview.add_item(button1)
		diabledview.add_item(button2)
		diabledview.add_item(button3)
		diabledview.add_item(button4)
		diabledview.add_item(button5)
		if check == True:
			try:
				return await msg.edit(content = 'The buttons on this message have timed out',embed = emb,view=diabledview)
			except:
				return

	@commands.command(name = 'pause')
	async def song_pause(self,ctx:Context):
		"""Pauses the currently playing song"""
		vc:MyPlayer = self.bot.wavelink.get_player(ctx.guild)
		if vc is None or not vc.is_playing():
			return await ctx.message.reply(embed = await self.embifier(False,content = self.notplaying))
		if ctx.author.voice is None or ctx.author.voice.channel is None or vc.channel.id != ctx.author.voice.channel.id:
			return await ctx.message.reply(embed = await self.embifier(False,content = self.unotconnected + vc.channel.mention))
		if vc.channel.id == ctx.author.voice.channel.id and not vc.is_paused():
			await vc.pause()
			await vc.set_pause(True)
			return await ctx.message.reply(embed = await self.embifier(True,content = 'Paused!'))
		if vc.is_paused():
			return await ctx.message.reply(embed = await self.embifier(False,content = 'The bot is already paused'))

	@commands.command(name = 'resume')
	async def song_resume(self,ctx:Context):
		"""Resumes the currently playing song"""
		vc:MyPlayer = self.bot.wavelink.get_player(ctx.guild)
		if vc is None or not vc.is_playing():
			return await ctx.message.reply(embed = await self.embifier(False,content = self.notplaying))
		if ctx.author.voice is None or ctx.author.voice.channel is None or vc.channel.id != ctx.author.voice.channel.id:
			return await ctx.message.reply(embed = await self.embifier(False,content = self.unotconnected + vc.channel.mention))
		if vc.channel.id == ctx.author.voice.channel.id and vc.is_paused():
			await vc.resume()
			await vc.set_pause(False)
			return await ctx.message.reply(embed = await self.embifier(True,content = 'Resumed!'))
		if not vc.is_paused():
			return await ctx.message.reply(embed = await self.embifier(False,content = 'The bot is not paused'))

	@commands.command(name = 'stop')
	async def stop(self,ctx:Context):
		"""Stops the currently playing song"""
		vc:MyPlayer = self.bot.wavelink.get_player(ctx.guild)
		if vc is None or not vc.is_playing():
			return await ctx.message.reply(embed = await self.embifier(False,content = self.notplaying))
		if ctx.author.voice is None or ctx.author.voice.channel is None or vc.channel.id != ctx.author.voice.channel.id:
			return await ctx.message.reply(embed = await self.embifier(False,content = self.unotconnected + vc.channel.mention))
		if vc.is_playing():
			await vc.stop()
			boolean = vc.queue.is_empty
			if boolean:
				pass
			else:
				vc.queue.clear()
			return await ctx.message.reply(embed = await self.embifier(True,content = 'Stopped!'))
		else:
			return await ctx.message.reply(embed = await self.embifier(False,content = self.notplaying))

	@commands.command(name = 'clear_queue',aliases = ['cq'])
	async def cq(self,ctx:Context):
		"""Clears the queue"""
		vc:MyPlayer = self.bot.wavelink.get_player(ctx.guild)
		if vc is None or not vc.is_playing():
			return await ctx.message.reply(embed = await self.embifier(False,content = self.notplaying))
		if ctx.author.voice is None or ctx.author.voice.channel is None or vc.channel.id != ctx.author.voice.channel.id:
			return await ctx.message.reply(embed = await self.embifier(False,content = self.unotconnected + vc.channel.mention))
		boolean = vc.queue.is_empty
		if boolean:
			return await ctx.message.reply(embed = await self.embifier(False,content = 'The queue is already empty'))
		
		queuecount = vc.queue.count
		vc.queue.clear()
		return await ctx.message.reply(embed = await self.embifier(True,content = f'Cleared {queuecount} from the queue!'))

	@commands.command(name = 'volume',description = 'Sets the volume to the given number or tells the current volume if no number is given')
	async def volume_command(self,ctx:Context, volume:int = None):
		"""Tells you the current volume of the bot if no volume mentioned, if mentioned sets the volume"""
		vc:MyPlayer = self.bot.wavelink.get_player(ctx.guild)
		if vc is None or not vc.is_playing():
			return await ctx.message.reply(embed = await self.embifier(False,content = self.notplaying))
		if ctx.author.voice is None or ctx.author.voice.channel is None or vc.channel.id != ctx.author.voice.channel.id:
			return await ctx.message.reply(embed = await self.embifier(False,content = self.unotconnected + vc.channel.mention))
		if volume == None:
			return await ctx.message.reply(embed = await self.embifier(True,content = f'Volume: **{vc.volume}**'))
		if int(volume) > 100 or int(volume) < 0:
			return await ctx.message.reply(embed = await self.embifier(False,content = f'Please specify a bumner between 0 and 100 to set the volume.'))
		if vc is None:
			return await ctx.message.reply(embed = await self.embifier(False,content = self.menotconnected))
		if ctx.author.voice is None or ctx.author.voice.channel is None or vc.channel.id != ctx.author.voice.channel.id:
			return await ctx.message.reply(embed = await self.embifier(False,content = self.unotconnected + vc.channel.mention))
		await vc.set_volume(int(volume))
		await ctx.message.reply(embed = await self.embifier(True,content = f'Volume set to {volume}'))

	@commands.command(name = 'lyrics',description = 'Returns the lyrics of the song mentioned')
	@commands.cooldown(1, 5, commands.BucketType.member)
	async def lyric_command(self,ctx:Context,*,search):
		"""Gives you the lyrics for the mentioned song"""
		url = f'https://some-random-api.ml/lyrics?title={search}'

		async with aiohttp.request("GET", url, headers={}) as r:
			if not 200 <= r.status <= 299:
				return await ctx.message.reply('No lyrics were found for the given song')
			data = await r.json()
			lyrics = data['lyrics']
			current_char = 0
			page_list = []
			total_indices_of_n = []
			for (index, item) in enumerate(list(lyrics)):
				if item == "\n":
					total_indices_of_n.append(index)
			while current_char!=total_indices_of_n[-1]:
				indices_of_n = []
				for (index, item) in enumerate(list(lyrics[:int(current_char)+401])):
					if item == "\n":
						indices_of_n.append(index)

				n_value = indices_of_n[-1]
				page_list.append(lyrics[int(current_char):(int(n_value)+1)])
				current_char = n_value
			last_emb = page_list[-1]
			page_list[-1] = str(last_emb+lyrics[int(current_char):-1]+lyrics[-1])
			emb = discord.Embed(
				title = data['title'],
				description='These lyrics are not guaranteed to be correct.\n\n'+page_list[0]
			)
			vc:MyPlayer = self.bot.wavelink.get_player(ctx.guild)
			view = LyricsView(ctx=ctx,vc=vc,pagelist = page_list,data = data,current = 0)
			msg = await ctx.message.reply(embed = emb,view = view)
			check = await view.wait()
			diabledview = View(timeout = 1)
			button1 = Button(label = 'PPrevious',disabled = True,style=discord.ButtonStyle.blurple)
			button2 = Button(label = 'Next',disabled = True,style=discord.ButtonStyle.blurple)
			diabledview.add_item(button1)
			diabledview.add_item(button2)
			if check == True:
				try:
					return await msg.edit(content = 'The buttons on this message have timed out',embed = emb,view=diabledview)
				except:
					return

	@commands.command(name = 'loop')
	async def loop_cmd(self,ctx:Context,looptype:str = None):
		"""Tells you the current loop of the bot if no loop mentioned, if mentioned sets the loop"""
		vc:MyPlayer = self.bot.wavelink.get_player(ctx.guild)
		if vc is None or not vc.is_playing():
			return await ctx.message.reply(embed = await self.embifier(False,content = self.notplaying))
		if ctx.author.voice is None or ctx.author.voice.channel is None or vc.channel.id != ctx.author.voice.channel.id:
			return await ctx.message.reply(embed = await self.embifier(False,content = self.unotconnected + vc.channel.mention))
		if looptype == None:
			if vc.loop is None:
				return await ctx.message.reply(embed = await self.embifier(False,content = 'Pls specify the type of loop (q,queue,s,single,n,none)'))
			if vc.loop == 'single':
				return await ctx.message.reply(embed = await self.embifier(True,content = 'The loop is set to Single'))	
			if vc.loop == 'queue':
					return await ctx.message.reply(embed = await self.embifier(True,content = 'The loop is set to Queue'))
			if vc.loop == 'none':
					return await ctx.message.reply(embed = await self.embifier(True,content = 'The loop is set to None'))
		if looptype in ['s','q','n','queue','single','none']:
			if looptype == 's' or looptype == 'single':
				vc.loop = 'single'
			if looptype == 'q' or looptype == 'queue':
					vc.loop = 'queue'
			if looptype == 'n' or looptype == 'none':
					vc.loop = 'none'
			return await ctx.message.reply(embed = await self.embifier(True,content = f'Loop set to {vc.loop}'))
		else:
			return await ctx.message.reply(embed = await self.embifier(False,content = 'Pls specify the type of loop correctly (q,queue,s,single,n,none)'))

async def setup(client:commands.Bot):
	await client.add_cog(Music(client))
