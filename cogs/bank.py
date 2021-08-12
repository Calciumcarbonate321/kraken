from collections import UserDict
import discord
from discord.ext import commands
from discord.ext.commands import Cog
import json

class bank(commands.Cog):
    '''This cog has the bank commands of the bot economy'''

    def __init__(self,client):
        self.client=client

    @commands.Cog.listener()
    async def on_ready(self):
        print(self.client.db)

    async def get_wallet(self,user_id :int):
        async with self.client.db.execute(f"SELECT * FROM bankdata WHERE userid={user_id}") as cursor:
            e=await cursor.fetchone()
            return e[1]

    async def get_bal(self,user_id :int):
        async with self.client.db.execute(f"SELECT * FROM bankdata WHERE userid={user_id}") as cursor:
            e=await cursor.fetchone()
            return e[2]

    async def create_account(self,user_id):
        with open('data/bank.json','r',encoding='utf8') as r:
            data=json.load(r)
            if user_id not in data:
                data[user_id]={'bal' : 0,'wallet' : 0,'bank_limit' : 100000,'daily':0}                
        with open('data/bank.json','w',encoding='utf8') as r:
            r.write(json.dumps(data,indent=4))
            
    async def get_daily_streak(self,user_id):
        async with self.client.db.execute(f"SELECT * FROM bankdata WHERE userid={user_id}") as cursor:
            e=await cursor.fetchone()
            return e[3]

    async def update_daily_streak(self,user_id):
        current=await self.get_daily_streak(user_id)
        new=current+1
        await self.client.db.execute(f"UPDATE bankdata SET daily={new} WHERE userid={user_id}")
        await self.client.db.commit()


    
    async def get_bank_limit(self,user_id):
        with open('data/bank.json','r',encoding='utf8') as r:
            return 1000000


    async def add_money(self,user_id,amount : int):
        current=await self.get_wallet(user_id)
        new=current+amount
        await self.client.db.execute(f"UPDATE bankdata SET wallet = {new} WHERE userid={user_id}")
        await self.client.db.commit()



    async def remove_money(self,user_id,amount : int):
        current=await self.get_wallet(user_id)
        new=current-amount
        await self.client.db.execute(f"UPDATE bankdata SET wallet = {new} WHERE userid={user_id}")
        await self.client.db.commit()

                
    async def add_money_bank(self,user_id,amount : int):
        current=await self.get_bal(user_id)
        new=current+amount
        await self.client.db.execute(f"UPDATE bankdata SET bankbal = {new} WHERE userid={user_id}")
        await self.client.db.commit()


    async def remove_money_bank(self,user_id,amount : int):
        current=await self.get_bal(user_id)
        new=current-amount
        await self.client.db.execute(f"UPDATE bankdata SET bankbal = {new} WHERE userid={user_id}")
        await self.client.db.commit()

            

    @commands.command(aliases=['bal','balance'],description="This command will show your bank and wallet details.")
    async def bank_balance(self,ctx,user : discord.User=None):
        if user is None:
            user=ctx.author
        userid=str(user.id)
        await self.create_account(userid)

        wallet=await self.get_wallet(userid)
        bank_bal=await self.get_bal(userid)
        bank_limit=await self.get_bank_limit(userid)

        embed=discord.Embed(title=f"{user.name}'s bank")
        embed.add_field(name="Wallet",value=f"⌬`{wallet}`")
        embed.add_field(name="Bank",value=f"⌬`{bank_bal}`/`{bank_limit}`",inline=False)
        embed.set_footer(text=f"Command invoked by {ctx.author.name}",icon_url=ctx.author.avatar_url)
        await ctx.send(embed=embed)
        

    @commands.command(aliases=['with','withdraw'],description="This command is used to some bot currency from your bank.")
    async def witho(self,ctx,amount :str=None):      
        userid=str(ctx.author.id)
        await self.create_account(userid)
        if amount is None:
            await ctx.send("What are you withdrawing you idiot")
            return
        amount=amount.lower()
        if amount not in ["max", "all"]:
            try:
                amount=int(amount)
            except:
                await ctx.send("You haven't entered a valid number")
                return
            else:
                if amount<0:
                    await ctx.send("The amount that you want to withdraw must be a whole number greater than 0.")
                    return              

        if amount in ["max", "all"]:
            amount=await self.get_bal(userid)

        bankbal=await self.get_bal(userid)
        if amount>bankbal:
            await ctx.send(f"You don't even have that much money in your bank, you have only ⌬{bankbal}")
        else:
            await self.add_money(userid,amount)
            await self.remove_money_bank(userid,amount)
            await ctx.send(f"You have withdrawn ⌬{amount}, your current wallet balance is ⌬{await self.get_wallet(userid)} and you have ⌬{await self.get_bal(userid)} in your bank")
        return

    @commands.command(aliases=['dep','deposit'],description="This command is used to deposit bot currency in your bank, so that it cannot be stolen by other users.")
    async def depo(self,ctx,amount :str=None):      
        userid=str(ctx.author.id)
        await self.create_account(userid)
        if amount is None:
            await ctx.send("What are you depositing you idiot")
            return
        amount=amount.lower()
        if amount not in ["max", "all"]:
            try:
                amount=int(amount)
            except:
                await ctx.send("You haven't entered an invalid number")
                return
            else:
                if amount<0:
                    await ctx.send("The amount that you want to deposit must be a whole number greater than 0.")
                    return              

        if amount in ["max", "all"]:
            amount=await self.get_wallet(userid)
            amount=int(amount)

        bankbal=await self.get_bal(userid)
        banklimit=await self.get_bank_limit(userid)
        wallet=await self.get_wallet(userid)

        if amount>wallet:
            await ctx.send(f"You don't even have that much money in your wallet, you have only ⌬{wallet}")
        elif amount+bankbal>banklimit:
            new_amount=banklimit-bankbal
            await self.add_money_bank(userid,new_amount)
            await self.remove_money(userid,new_amount)
            await ctx.send("Your bank is now full")
        elif bankbal==banklimit:
            await ctx.send("You have a full bank kiddo")
        else:
            await self.add_money_bank(userid,amount)
            await self.remove_money(userid,amount)
            await ctx.send(f"You have deposited ⌬{amount}, your current wallet balance is ⌬{await self.get_wallet(userid)} and you have ⌬{await self.get_bal(userid)} in your bank")

        return

    @commands.command(aliases=['share','give'],description="This command is used to share some bot currency with another user.")
    async def givemoney(self,ctx,user: discord.User,amount : int=None):
        try:
            userid=str(user.id)
            authid=str(ctx.author.id)
            await self.create_account(userid)
            await self.create_account(authid)
            authbal=await self.get_wallet(authid)
            if authbal<amount:
                await ctx.send("You don't even have that much money bruh")
                return
            if user is None or amount is None:
                await ctx.send("The correct format to do this command is `>give @user amount`")
                return

            await self.add_money(userid,amount)
            await self.remove_money(authid,amount)
            await ctx.send(f"You gave ⌬{amount} to {user.name}")
        except:
            await ctx.send("There was some error when running this command,make sure the format is correct, the correct format : `>give @user amount`")


            



def setup(client):
    client.add_cog(bank(client))

        