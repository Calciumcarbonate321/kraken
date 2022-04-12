import io
import pyboy
import discord
from discord.ext import commands

from PIL import Image

ROM_DIR=r"./data/roms/"
SAVES_DIR = './data/saves/'

GAMES=["red.gbc"]
GAME_NAME_MAP={
    "red":GAMES[0]
}

def blankfunc():
    pass

OPPOSITE_BUTTONS={
    "A":pyboy.WindowEvent.RELEASE_BUTTON_A,
    "B":pyboy.WindowEvent.RELEASE_BUTTON_B,
    "Up":pyboy.WindowEvent.RELEASE_ARROW_UP,
    "Down":pyboy.WindowEvent.RELEASE_ARROW_DOWN,
    "Left":pyboy.WindowEvent.RELEASE_ARROW_LEFT,
    "Right":pyboy.WindowEvent.RELEASE_ARROW_RIGHT,
    "Select":pyboy.WindowEvent.RELEASE_BUTTON_SELECT
    
}

COLOURS={
    "Save":discord.ButtonStyle.green,
    "Load":discord.ButtonStyle.danger,
    "A":discord.ButtonStyle.blurple,
    "B":discord.ButtonStyle.blurple,
    "Up":discord.ButtonStyle.blurple,
    "Down":discord.ButtonStyle.blurple,
    "Left":discord.ButtonStyle.blurple,
    "Right":discord.ButtonStyle.blurple,
    "DUp":discord.ButtonStyle.blurple,
    "DDown":discord.ButtonStyle.blurple,
    "DLeft":discord.ButtonStyle.blurple,
    "DRight":discord.ButtonStyle.blurple,
    "Select":discord.ButtonStyle.blurple,
    "Quit":discord.ButtonStyle.danger,
    "Blank":discord.ButtonStyle.gray
}

async def save(userid,game):
    with open(f"{SAVES_DIR}/{userid}.state","wb") as f:
        game.save_state(f)

async def load(userid,game):
    try:
        with open(f"{SAVES_DIR}/{userid}.state","rb") as f:
            game.load_state(f)
    except Exception:
        return False

BUTTONS={
    "Save":save,
    "Load":load,
    "A":pyboy.WindowEvent.PRESS_BUTTON_A,
    "B":pyboy.WindowEvent.PRESS_BUTTON_B,
    "Up":pyboy.WindowEvent.PRESS_ARROW_UP,
    "Down":pyboy.WindowEvent.PRESS_ARROW_DOWN,
    "Left":pyboy.WindowEvent.PRESS_ARROW_LEFT,
    "Right":pyboy.WindowEvent.PRESS_ARROW_RIGHT,
    "Select":pyboy.WindowEvent.PRESS_BUTTON_SELECT,
    "Quit":pyboy.WindowEvent.QUIT,
    "Blank":blankfunc
}

BUTTONS_TEXT={
    "Save":"💾",
    "Load":"📥",
    "A":"🇦",
    "B":"🇧",
    "Up":"⬆️",
    "Down":"⬇️",
    "Left":"⬅️",
    "Right":"➡️",
    "DUp":"⏫",
    "DDown":"⏬",
    "DLeft":"⏪",
    "DRight":"⏩",
    "Quit":"⏹️",

}

class GameButton(discord.ui.Button):
    def __init__(self,type,row):
        super().__init__(style=COLOURS[type],label="\u200B" if type!="Select" else "Select",row=row,emoji=BUTTONS_TEXT[type] if type not in ["Blank","Select"] else None,)
        self.btype=type

    async def callback(self, interaction):
        if self.btype=="Quit":
            for i in self.view.children:
                i.disabled=True
            await interaction.response.edit_message(content="Game Ended.",view=self.view)
            return
        await self.view.button_press(self.btype)
        await self.view.rungame()
        f=await self.view.renderframes()
        await interaction.response.edit_message(content="Game going on...",attachments=[f])

BUTTONS_LIST=[
    GameButton("Save",0),GameButton("Load",0),GameButton("DUp",0),GameButton("Quit",0),GameButton("Select",0),
    GameButton("Blank",1),GameButton("Blank",1),GameButton("Up",1),GameButton("Blank",1),GameButton("Blank",1),
    GameButton("DLeft",2),GameButton("Left",2),GameButton("Blank",2),GameButton("Right",2),GameButton("DRight",2),
    GameButton("Blank",3),GameButton("Blank",3),GameButton("Down",3),GameButton("Blank",3),GameButton("A",3),
    GameButton("Blank",4),GameButton("Blank",4),GameButton("DDown",4),GameButton("B",4),GameButton("Blank",4)
]

class GameView(discord.ui.View):
    def __init__(self,bot,user,gamedir,message=None):
        self.bot=bot
        self.user=user
        self.game=pyboy.PyBoy(gamedir,window_type="headless")
        self.frames=[]
        self.game.set_emulation_speed(0)
        self.screen=self.game.botsupport_manager().screen()
        self.message=message
        super().__init__(timeout=None)
        for i in BUTTONS_LIST:
            self.add_item(i)
        

    async def button_press(self,button):
        if button not in ["Blank","Save","Load","Quit","DUp","DDown","DLeft","DRight"]:
            self.game.send_input(BUTTONS[button])
            await self.rungame(5)
            if e := OPPOSITE_BUTTONS.get(button):
                self.game.send_input(e)
        elif button in ["Save","Load"]:
            await BUTTONS[button](self.user.id,self.game)
        elif button=="Quit":
            self.game.send_input(pyboy.WindowEvent.QUIT)
        elif button in ["DUp","DDown","DLeft","DRight"]:
            self.game.send_input(BUTTONS[button[1:]])
            await self.rungame(10)
            if e := OPPOSITE_BUTTONS.get(button[1:]):
                self.game.send_input(e)
            self.game.send_input(BUTTONS[button[1:]])
            await self.rungame(10)
            if f := OPPOSITE_BUTTONS.get(button[1:]):
                self.game.send_input(f)

    async def rungame(self,ticks=200):
        def run():
            for i in range(ticks):
                self.game.tick()
                if i%5==0:
                    self.frames.append(self.screen.screen_image().resize((256,256),resample=Image.NEAREST))
        await self.bot.loop.run_in_executor(None,run)
    
    async def renderframes(self):
        b=io.BytesIO()
        def render():
            i=self.frames.pop(0)
            i.save(b,format="gif",append_images=self.frames,save_all=True)
            self.frames.clear()
        await self.bot.loop.run_in_executor(None,render)
        b.seek(0)
        f=discord.File(fp=b,filename="game.gif")
        return f

    async def interaction_check(self, interaction):
        if interaction.user!=self.user:
            await interaction.response.send_message("Not your game lol", ephemeral=True)
            return False
        return True

class GameBoyCog(commands.Cog):
    def __init__(self,bot):
        self.bot=bot
        self.games={}

    @commands.command(name="gb")
    async def gb(self,ctx):
        if ctx.author.id in self.games:
            return await ctx.send("You are already playing")
        e=await ctx.reply("Here see this game")
        view=GameView(self.bot,ctx.author,ROM_DIR+GAME_NAME_MAP["red"],e)
        await view.rungame()
        f=await view.renderframes()
        self.games[ctx.author.id]=view
        await e.edit(content="Game going on...",attachments=[f],view=view)
                

async def setup(bot):
    await bot.add_cog(GameBoyCog(bot))
