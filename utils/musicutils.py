import discord
from discord.ext import commands
from discord.ext.commands.context import Context
from discord.interactions import Interaction
from discord.ui.select import Select
import wavelink
from discord.ui import Button, View
import datetime

class Embifier():
	def __init__(self,success=None,content=None,title=''):
		self.success = success
		self.content = content
		self.title = title
	async def embifier(self):
		if self.success:
			color = discord.Color.green()
			emoj = '<a:check_ravena:930704225451798529>'
		else:
			color = discord.Color.red()
			emoj = "<a:cross_ravena:930704070942007316>"
		emb = discord.Embed(
			title = self.title,
			description= emoj+' | '+self.content,
			color = color
		)
		return emb

class MyPlayer(wavelink.Player):
	async def connect(self, *, timeout: float, reconnect: bool) -> None:
		await self.guild.change_voice_state(channel=self.channel,self_deaf = True)
		self._connected = True
	async def disconnect(self, *, force: bool) -> None:
		try:
			if self.is_playing():
				await self.node._websocket.send(op="stop", guildId=str(self.guild.id))
				self._source = None
			await self.guild.change_voice_state(channel=None)
			self._connected = False
		finally:
			self.node.players.remove(self)
			self.cleanup()

class DropDown(Select):
	def __init__(self,ctx=None,tracks = None,vc = None):
		self.vc:MyPlayer = vc
		self.tracks = tracks
		self.ctx:Context = ctx
		options = [
			discord.SelectOption(label=f'{self.tracks[0].title}',description = f'{datetime.timedelta(seconds=round(tracks[0].length))}',value = 0),
			discord.SelectOption(label=f'{self.tracks[1].title}',description = f'{datetime.timedelta(seconds=round(tracks[1].length))}',value = 1),
			discord.SelectOption(label=f'{self.tracks[2].title}',description = f'{datetime.timedelta(seconds=round(tracks[2].length))}',value = 2),
			discord.SelectOption(label=f'{self.tracks[3].title}',description = f'{datetime.timedelta(seconds=round(tracks[3].length))}',value = 3),
			discord.SelectOption(label=f'{self.tracks[4].title}',description = f'{datetime.timedelta(seconds=round(tracks[4].length))}',value = 4)]
		super().__init__(placeholder='Choose which song you want to play:',options = options)

	async def play_song(self,interaction:Interaction = None,label=0):
		if self.tracks[label].length > 600:
			await interaction.message.delete()
			return await self.ctx.message.reply(embed = await Embifier(success = False,content = f'That song is more than 10 mins long').embifier())
		if not self.vc.is_playing():
			await interaction.message.delete()
			return await self.vc.play(self.tracks[label])
		else:
			await interaction.message.delete()
			if self.vc.loop == 'single':
				return await self.ctx.message.reply(embed = await Embifier(success = False,content = f'The loop is set to single so can\'t add the song to queue').embifier())
			self.vc.queue.put(self.tracks[label])
			await self.ctx.message.reply(embed = await Embifier(success = True,content = f'Added **{self.tracks[label].title}** to the queue ').embifier())

	async def callback(self,interaction:Interaction):
		await self.play_song(interaction = interaction,label = int(self.values[0]))

class PlayView(View):
	def __init__(self, *, timeout = 30,ctx = None,vc=None,tracks = None):
		super().__init__(timeout=timeout)
		self.ctx:Context = ctx
		self.userid = ctx.author.id
		self.vc:MyPlayer = vc
		self.tracks = tracks
		self.add_item(DropDown(ctx = self.ctx,tracks = self.tracks,vc = self.vc))
	async def interaction_check(self, interaction: Interaction):
		if interaction.user.id != self.userid:
			await interaction.response.send_message(content = 'That menu is not for you',ephemeral=True)
			return False
		if not self.vc.is_connected():
			await interaction.message.reply(embed = await Embifier(success = False,content = 'The bot is not connected to any vc').embifier(),view = None)
			await interaction.message.delete()
			return False
		else:
			return True

class NowPlayingView(View):
	def __init__(self, *, timeout = 60,ctx = None,vc=None):
		super().__init__(timeout=timeout)
		self.ctx:Context = ctx
		self.userid = ctx.author.id
		self.vc:MyPlayer = vc

	async def interaction_check(self, interaction: Interaction):
		if interaction.user.id != self.userid:
			await interaction.response.send_message(content = 'Those buttons are not for you',ephemeral=True)
			return False
		if not self.vc.is_connected():
			await interaction.message.reply(embed = await Embifier(success = False,content = 'The bot is not connected to any vc').embifier(),view = None)
			await interaction.message.delete()
			return False
		else:
			return True

	async def nowplayingembed(self):
		if self.vc.is_paused():
			paused = 'Paused'
		if not self.vc.is_paused():
			paused = 'Playing'
		if self.vc.is_paused():
			paused = 'Paused'
		if not self.vc.is_paused():
			paused = 'Playing'
		if self.vc.loop == 'single':
			loopvalue = 'Single'
		if self.vc.loop == 'queue':
			loopvalue = 'Queue'
		if self.vc.loop == 'none':
			loopvalue = 'None'
		current = datetime.timedelta(seconds=round(self.vc.position))
		total = datetime.timedelta(seconds=round(self.vc.track.length))
		emb = discord.Embed(title = 'This server\'s music status',color = discord.Color.teal())
		emb.add_field(name = '<a:playing:936587336383336538> Title:',value = f'**{self.vc.track.title}**')
		emb.add_field(name = '<a:timeline:936583271557521419> Duration:',value = f'{total}')
		emb.add_field(name = '✍️ Author:',value = self.vc.track.author)
		emb.add_field(name = '🔗 Url:',value = self.vc.track.info['uri'])
		emb.add_field(name = '<a:timeline:936583271557521419> Timeline',value = f'{current} / {total}')
		emb.add_field(name = '⏯️ Playing/Paused:',value = paused)
		emb.add_field(name = '<a:player:936579719741210635> Queue count:',value = self.vc.queue.count)
		emb.add_field(name = '<a:playing:936587336383336538> Loop:',value = loopvalue)
		try:
			emb.set_thumbnail(url = self.vc.track.thumb)
		except:
			pass
		volume = self.vc.volume
		if volume == 0:
			volume = 'Muted'
		emb.add_field(name = '🔊 Volume:',value = volume)
		emb.set_author(name = self.ctx.author.name,icon_url=self.ctx.author.display_avatar)
		return emb

	async def song_skip(self,interaction:Interaction = None):
		if self.vc is None:
			return await interaction.response.send_message(embed = await Embifier(success = False,content = 'I am not in a voice channel').embifier())
		if self.ctx.author.voice is None or self.ctx.author.voice.channel.id != self.vc.channel.id:
			return await interaction.response.send_message(embed = await Embifier(success = False,content = f'You are not connected to the voice channel I am in {self.vc.channel}').embifier())
		if self.vc.loop == 's' or self.vc.loop == 'single':
			await self.vc.seek(0)
			emb = await self.nowplayingembed()
			await interaction.response.edit_message(embed=emb)
			msg = await interaction.original_message()
			return await msg.reply(embed = await Embifier(success = True,content = 'Skipped!').embifier())

		if self.vc.queue.is_empty:
			return await interaction.response.send_message(embed = await Embifier(success = False,content = 'The queue is empty').embifier())

		if self.vc.loop == 'q' or self.vc.loop == 'queue':
			song =  self.vc.queue.get()
			self.vc.queue.put(self.vc.track)
			await self.vc.stop()
			await self.vc.play(song,replace = True)

		if self.vc.loop == 'n' or self.vc.loop == 'none':
			song =  self.vc.queue.get()
			await self.vc.stop()
			await self.vc.play(song,replace = True)

		emb = await self.nowplayingembed()
		await interaction.response.edit_message(embed=emb)
		msg = await interaction.original_message()
		return await msg.reply(embed = await Embifier(success = True,content = 'Skipped!').embifier())

	@discord.ui.button(label='Play/Pause',style=discord.ButtonStyle.blurple,emoji = '⏯️')
	async def button1(self,button:Button,interaction:Interaction):
		if self.vc.is_paused():
			await self.vc.resume()
			emb = await self.nowplayingembed()
			await interaction.response.edit_message(embed=emb)
			msg = await interaction.original_message()
			return await msg.reply(embed = await Embifier(success = True,content = 'Resumed!').embifier())
		if not self.vc.is_paused():
			await self.vc.pause()
			emb = await self.nowplayingembed()
			await interaction.response.edit_message(embed=emb)
			msg = await interaction.original_message()
			return await msg.reply(embed = await Embifier(success = True,content = 'Paused!').embifier())
	
	@discord.ui.button(label='Skip',style=discord.ButtonStyle.red)
	async def button2(self,button:Button,interaction:Interaction):
		await self.song_skip(interaction = interaction)

	@discord.ui.button(label='Rewind',style=discord.ButtonStyle.blurple)
	async def button3(self,button:Button,interaction:Interaction):
		await self.vc.seek(position = 0)
		emb = await self.nowplayingembed()
		await interaction.response.edit_message(embed=emb)
		msg = await interaction.original_message()
		return await msg.reply(embed = await Embifier(success = True,content = 'Rewinded!').embifier())

	@discord.ui.button(label='Mute/Unmute',style=discord.ButtonStyle.red)
	async def button4(self,button:Button,interaction:Interaction):
		if self.vc.volume == 0:
			await self.vc.set_volume(100)
		else:
			await self.vc.set_volume(0)
		emb = await self.nowplayingembed()
		await interaction.response.edit_message(embed=emb)
		msg = await interaction.original_message()
		if self.vc.volume == 0:
			muted = 'Muted!'
		else:
			muted = 'Unmuted!'
		return await msg.reply(embed = await Embifier(success = True,content = f'{muted}').embifier())

class LyricsView(View):
	def __init__(self, *, timeout = 120,ctx = None,vc=None,pagelist = None,data = None,current = 0):
		super().__init__(timeout=timeout)
		self.ctx:Context = ctx
		self.vc:MyPlayer = vc
		self.pagelist = pagelist
		self.data = data
		self.current = current

	async def interaction_check(self, interaction: Interaction):
		if interaction.user.id != self.ctx.author.id:
			await interaction.response.send_message(content = 'Those buttons are not for you',ephemeral=True)
			return False
		return True

	@discord.ui.button(label='Previous',style=discord.ButtonStyle.blurple)
	async def button1(self,button:Button,interaction:Interaction):
		if self.current != 0:
			emb = discord.Embed(
				title = self.data['title'],
				description='The lyrics are not guaranteed to be correct \n\n'+self.pagelist[self.current-1],
				color = discord.Color.random())
			await interaction.response.edit_message(embed = emb)
			self.current = self.current-1
		else:
			return await interaction.response.send_message(content = 'This is the first page',ephemeral=True)

	@discord.ui.button(label='Next',style=discord.ButtonStyle.blurple)
	async def button2(self,button:Button,interaction:Interaction):
		lastpage = len(self.pagelist)-1
		if self.current != lastpage:
			emb = discord.Embed(
				title = self.data['title'],
				description='These lyrics are not guaranteed to be correct \n\n'+self.pagelist[self.current+1],
				color = discord.Color.random())
			self.current = self.current+1
			await interaction.response.edit_message(embed = emb,view = LyricsView(ctx = self.ctx,vc = self.vc,current=self.current,pagelist = self.pagelist,data = self.data))
		else:
			return await interaction.response.send_message(content = 'This is the last page',ephemeral=True)
