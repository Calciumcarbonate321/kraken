import discord
from discord import emoji

class invitebutton(discord.ui.Button):
    def __init__(self):
        super().__init__(label="Invite me",style=discord.ButtonStyle.link,url="https://discord.com/api/oauth2/authorize?client_id=843071820878184458&permissions=415797472576&scope=bot",emoji="<:blurple_bot:912660314938560542>")

class sourcebutton(discord.ui.Button):
    def __init__(self):
        super().__init__(label="Source code",style=discord.ButtonStyle.link,url="https://github.com/Calciumcarbonate321/kraken",emoji="<:github:912659090247933962>")

class deletethismessage(discord.ui.View):
    def __init__(self,author):
        super().__init__(timeout=30)
        self.author=author

    @discord.ui.button(emoji="<a:uncheck_ravena:907507933846327327>",style=discord.ButtonStyle.red)
    async def dele(self,button:discord.ui.Button, interaction: discord.Interaction):
        await interaction.message.delete()

    async def interaction_check(self, interaction: discord.Interaction) -> bool:
        return self.author==interaction.user
    
    