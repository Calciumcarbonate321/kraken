import discord
from discord import user
from discord import client
from discord.colour import Color
from discord.ext import commands
from discord.ext.commands import Cog
import random
import json

from discord.ext.commands.cooldowns import BucketType
from cogs.bank import bank
from cogs.shopsys import shop

from discord.ext.commands.errors import NoEntryPointError

class money_making(commands.Cog):
    def __init__(self,client):
        self.client=client
        self.bi=bank(client) #instance of the bank class from bank.py file
        self.lol=shop(client)

    @commands.command(name="beg",description="This command is used to beg some bot currecncy.")
    @commands.cooldown(1,30,commands.BucketType.user)
    async def beg(self,ctx):
        userid=str(ctx.author.id)
        users = await self.lol.get_shop_data()
        inv = users[str(userid)]["Inventory"]
        for pog in inv:
            eqp = pog["equipped"]
            break
        if eqp == "luckycharm":
            payout = random.randint(0,1600)
        else:
            payout = random.randint(0,800)
       
        payout = int(payout)
        
        if payout==0:
            embed=discord.Embed(title="Begging unsuccessful",url="https://www.youtube.com/watch?v=dQw4w9WgXcQ",color=discord.Colour.red())
            embed.add_field(name="Sadge",value="You earned nothing by begging")
            embed.set_footer(text="Try begging again after sometime",icon_url=ctx.author.avatar_url)
            await ctx.send(embed=embed)
            return 
        elif payout > 800:
            extra = (payout-800)
            extra = int(extra)
            tpo = (payout - extra)
            tpo = int(tpo)
            print(tpo)
            embed=discord.Embed(title="Begging successful",url="https://www.youtube.com/watch?v=dQw4w9WgXcQ",color=discord.Colour.red())
            embed.add_field(name="Nice job",value= f"You earned ⌬`{tpo}`by begging, and you get an additional ⌬`{extra}` since you have a *Lucky Charm*")
            embed.set_footer(text="Good job mate",icon_url=ctx.author.avatar_url)
            print("works lmao")
            await self.bi.add_money(userid,payout)
            await ctx.send(embed=embed)
        else:
            embed=discord.Embed(title="Begging successful",url="https://www.youtube.com/watch?v=dQw4w9WgXcQ",color=discord.Colour.red())
            embed.add_field(name="Nice job",value=f"You earned ⌬`{payout}`by begging")
            embed.set_footer(text="Good job mate",icon_url=ctx.author.avatar_url)
            await self.bi.add_money(userid,payout)
            await ctx.send(embed=embed)
    @beg.error
    async def beg_handler(self,ctx,error):
        if isinstance(error,commands.CommandOnCooldown):
            await ctx.send(f"This command is on a cooldown,try after {round(error.retry_after)}s")

    @commands.command(aliases=['flip','coinflip'],description="This is a coin-flip command, you can do a bet if you want.")
    async def coin(self,ctx,choice : str=None,bet : int=None):
        userid=str(ctx.author.id)
        if choice is None:
            await ctx.send("You have not entered a choice")
            return
        outcomes=['h','t']
        choice=choice[0].lower()
        outcome=random.choice(outcomes)
        bet=int(bet)
        wallet=await self.bi.get_wallet(userid)
        if wallet<bet:
            await ctx.send("You don't even have that much money bruh")
            return
        if bet<0:
            await ctx.send("The number must be greater than 0")
            return

        if outcome=='h':
            value="Heads"
        elif outcome=="t":
            value="Tails"
        payout=random.randint(1,3)
        if outcome==choice:
            embed=discord.Embed(title="Yay! you have won ",url="https://www.youtube.com/watch?v=dQw4w9WgXcQ",color=discord.Colour.green())
            embed.add_field(name="Outcome:",value=f"{value}")
            embed.add_field(name="Payout",value=f"{payout}x your bet" )
            embed.set_footer(text="Congrats on winning",icon_url=ctx.author.avatar_url)
            await ctx.send(embed=embed)
            await self.bi.add_money(userid,(payout*bet))

        else:
            embed=discord.Embed(title="Oh no you have lost ",url="https://www.youtube.com/watch?v=dQw4w9WgXcQ",color=discord.Colour.red())
            embed.add_field(name="Outcome:",value=f"{value}")
            embed.add_field(name="Payout",value="You lost the money that you bet")
            embed.set_footer(text="F you lost, try again later",icon_url=ctx.author.avatar_url)
            await ctx.send(embed=embed)
            await self.bi.remove_money(userid,bet)
    @commands.command(aliases=['bet','rolls'],description="This is the bet command, you and the bot roll a dice once each, whoever has the highest number will win the game.")
    async def gamble(self,ctx,amount : int=None):

        user_roll=random.randint(1,12)
        bot_roll=random.randint(1,12)
        payout=random.randint(50,200)
        userid=str(ctx.author.id)
        balance=await self.bi.get_wallet(userid)

        if balance<amount:
            await ctx.send("You don't have that much money")   
            return
        if amount<=0:
            await ctx.send("The bet amount should be greater than 0")
            return

        if user_roll>bot_roll:
            await self.bi.add_money(userid,int(amount*payout/100))
            embed=discord.Embed(title=f"{ctx.author.name}'s winning gambling game",url="https://www.youtube.com/watch?v=dQw4w9WgXcQ",color=discord.Colour.green())
            embed.add_field(name=f"{ctx.author.name}",value=f"{user_roll}")
            embed.add_field(name=f"{str(self.client.user)[:-5]}",value=f"{bot_roll}")
            embed.add_field(name="Percent won",value=f"{payout}%")
            embed.add_field(name="Amount won",value=f"{int(amount*payout/100)}⌬")
            embed.set_footer(text="Congratulations on winning",icon_url=ctx.author.avatar_url)
            await ctx.send(embed=embed)
        elif user_roll<bot_roll:
            await self.bi.remove_money(userid,amount)
            embed=discord.Embed(title=f"{ctx.author.name}'s losing gambling game",url="https://www.youtube.com/watch?v=dQw4w9WgXcQ",color=discord.Colour.red())
            embed.add_field(name=f"{ctx.author.name}",value=f"{user_roll}")
            embed.add_field(name=f"{str(self.client.user)[:-5]}",value=f"{bot_roll}")
            embed.add_field(name=f"You lost ⌬{amount}",value="Better luck next time")
            embed.set_footer(text="F you lost",icon_url=ctx.author.avatar_url)
            await ctx.send(embed=embed)
        elif user_roll==bot_roll:
            embed=discord.Embed(title=f"{ctx.author.name}'s tied gambling game",url="https://www.youtube.com/watch?v=dQw4w9WgXcQ",color=0xe67e22)
            embed.add_field(name=f"{ctx.author.name}",value=f"{user_roll}")
            embed.add_field(name=f"{str(self.client.user)[:-5]}",value=f"{bot_roll}")
            embed.add_field(name="That's a tie",value="You lost nothing nor did you gain anything")
            embed.set_footer(text="That was a dramatic tie",icon_url=ctx.author.avatar_url)
            await ctx.send(embed=embed)

    @commands.command(name="rob",description="This command is used to rob an user of their bot currency, there is a chance that you will fail the robbery and will pay a fine to that user.")
    @commands.cooldown(1,30,type=BucketType.user)
    async def rob(self,ctx,user : discord.User=None):
        if user is None:
            await ctx.send("Who are you robbing dum dum")
            return
        userid=str(user.id)
        authid=str(ctx.author.id)
        user_bal=await self.bi.get_wallet(userid)
        auth_bal= await self.bi.get_wallet(authid)

        if user_bal==0:
            await ctx.send(f"{user.name} doesn't even have money in their wallet")
            return

        isRobFailed=random.randint(0,5)
        if isRobFailed==0:
            amountlost=random.randint(0,auth_bal)
            await ctx.send(f"F you got caught while robbing and paid them ⌬{amountlost}")
            await self.bi.remove_money(authid,amountlost)
            await self.bi.add_money(userid,amountlost)
        else:
            amountgained=random.randint(0,user_bal)
            await ctx.send(f"You stole ⌬{amountgained} from {user.name}")
            await self.bi.remove_money(userid,amountgained)
            await self.bi.add_money(authid,amountgained)

    @rob.error
    async def rob_handler(self,ctx,error):
        if isinstance(error,commands.CommandOnCooldown):
            await ctx.send(f"This command is on a cooldown,try after {round(error.retry_after)}s")

    @commands.command(name="daily",description="This command can be used once every 24h, it gives you some coins and the number of coins depend on your daily streak.")
    @commands.cooldown(1,86400,BucketType.user)
    async def daily(self,ctx):
        userid=str(ctx.author.id)
        await self.bi.create_account(userid)
        amount=10000
        streak=await self.bi.get_daily_streak(userid)
        bonus=streak*100
        await self.bi.update_daily_streak(userid)
        amount += bonus
        await self.bi.add_money(userid,amount)

        embed=discord.Embed(title="Here are your daily coins", url="https://www.youtube.com/watch?v=dQw4w9WgXcQ", description=f"**⌬{amount}** was placed in your wallet")
        embed.add_field(name=f"You can get atleast ⌬10000 by using this command once every 24 hours", value="The amount that you get depends on your daily streak", inline=False)
        embed.set_footer(text=f"Current daily streak={await self.bi.get_daily_streak(userid)}")
        await ctx.send(embed=embed)

    @daily.error
    async def daily_handler(self,ctx,error):
        if isinstance(error,commands.CommandOnCooldown):
            await ctx.send(f"This command is on a cooldown,try after {round(error.retry_after)}s")

    


def setup(client):
    client.add_cog(money_making(client))


        

                    

                