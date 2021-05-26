import discord
import json
import random
import os
from discord.ext import commands
from discord.ext.commands import Cog
from cogs.bank import bank



mainshop = [
{"name":"Rifle","price":"50000","description":"used to kill","icon":":gun:","itemid":"rifle"},
{"name":"Fishing Rod","price":"5000","description":"used to fish","icon":":fishing_pole_and_fish:","itemid":"fishingrod"},
{"name":"Laptop","price":"1000","description":"Post memes, blog and work","icon":":computer:","itemid":"laptop"},
{"name":"Lucky Charm","price":"15000","description":"increases luck by 10%","icon":":shamrock:","itemid":"luckycharm"}




]

class shop(commands.Cog):
    def __init__(self,client):
        self.client=client
        self.bi=bank(client)

    async def get_bank_data(self):
       with open("data/bank.json","r") as f:
          users = json.load(f)
    
       return users
    
    async def get_shop_data(self):
       with open("data/shop.json","r") as f:
          users = json.load(f)
    
       return users

    async def update_bank(self,user,change = 0,mode = "wallet"):
      users = await self.get_bank_data()
    
      users[str(user.id)][mode] += change
        
      with open("data/bank.json","w") as f:
        f.write(json.dumps(users,indent=4))
    
      bal = [users[str(user.id)]["wallet"]]
      return bal

    
    async def open_account(self,user):
      users = await self.get_bank_data()
    
      if str(user.id) in users:
         return False
      else:
         users[str(user.id)] = {}
         users[str(user.id)]["wallet"] = 0
         users[str(user.id)]["bal"] = 0
      
      with open("data/bank.json","w") as f:
         f.write(json.dumps(users,indent=4))
      return True
    
    async def open_shopacc(self,user):
      users = await self.get_shop_data()
    
      if str(user.id) in users:
         return False
      else:
         users[str(user.id)] = {}
         users[str(user.id)]["Inventory"] = None
         users[str(user.id)]["bag"] = []
      
      with open("data/shop.json","w") as f:
         f.write(json.dumps(users,indent=4))
      return True


    
    async def buy_this(self,user,item_name,amount):
      item_name = item_name.lower()
      name_ = None
      for item in mainshop:
        name = item["itemid"].lower()
        if name == item_name:
          name_ = name
          price = item["price"]
          rlname = item["name"]
          iticon = item["icon"]
          break
    
    
      if name_ == None:
        return [False,1]
      
      cost = int(price) * int(amount)
      cost = int(cost)
    
      users = await self.get_shop_data()
    
      bal = await self.bi.get_wallet(str(user.id))
    
    
      if bal<cost:
        return [False,2]
    
    
      try:
        index = 0
        t = None
        for thing in users[str(user.id)]["bag"]:
          n = thing["itemid"]
          if n == item_name:
            old_amt = thing["amount"]
            new_amt = old_amt + amount
            users[str(user.id)]["bag"][index]["amount"] = new_amt
            t = 1
            break
          index+=1
        if t == None:
          obj = {"itemid": item_name,"amount": amount, "name": rlname,"icon": iticon}
          users[str(user.id)]["bag"].append(obj)
      except:
        obj = {"itemid":item_name,"amount":amount, "name": rlname, "icon": iticon}
        users[str(user.id)]["bag"] = [obj]
    
      with open("data/shop.json","w") as f:
        f.write(json.dumps(users,indent=4))
    
      await self.update_bank(user,cost*-1,"wallet")
      return [True,"Worked"]
    
    
    async def sell_this(self,user,item_name,amount,price=None):
      item_name = item_name.lower()
      name_ = None
      for item in mainshop:
        name = item["itemid"].lower()
        if name == item_name:
           name_ = name
           if price==None:
             price = item["price"]
           break
    
    
      if name_ == None:
        return [False,1]
      if amount == None:
        amount = 1
      amount = int(amount)
      
      cost=int(price) * int(amount)
      cost = int(cost)
    
      users = await self.get_shop_data()
    
      bal = await self.update_bank(user)
    
    
      try:
        index = 0
        t = None
        for thing in users[str(user.id)]["bag"]:
          n = thing["itemid"]
          if n == item_name:
            old_amt = thing["amount"]
            old_amt = int(old_amt)
            new_amt = old_amt - amount
            if new_amt<0:
              return [False,2]
            users[str(user.id)]["bag"][index]["amount"] = new_amt
            t = 1
            break
          index+=1
        if t == None:
          return [False,3]
      except:
        return [False,3]

      with open("data/shop.json","w") as f:
        f.write(json.dumps(users,indent=4))
    
      await self.update_bank(user,cost,"wallet")
      return [True,"Worked"]
      


    @commands.command()
    async def shop(self,ctx):
      await self.open_shopacc(ctx.author)
      em = discord.Embed(title = "__Shop__",url="https://www.youtube.com/watch?v=dQw4w9WgXcQ",color = discord.Color.red())

      for item in mainshop:
        name = item["name"]
        price = item["price"]
        desc = item["description"]
        icon = item["icon"]
        itid = item["itemid"]

        em.add_field(name = f"\n {name} " + f" «{icon}»", value = f"**{price} ⌬** | {desc}\n`{itid}`\n")
        em.add_field(name = "⠀",value = "⠀")
        em.add_field(name = "⠀",value = "⠀")

      await ctx.send(embed = em)



    @commands.command()
    async def buy(self,ctx,item,amount = 1):
      await self.open_account(ctx.author)
      await self.open_shopacc(ctx.author)
      res = await self.buy_this(ctx.author,item,amount)
    
      if not res[0]:
        if res[1] ==1:
          await ctx.send(ctx.author.mention + ", This item does not exist!")
          return
        if res[1] ==2:
          await ctx.send(ctx.author.mention + f", you dont have enough money to buy {item}(s)!")
          return
      
      await ctx.send(ctx.author.mention + f" >> *Successfully bought **{amount} {item}(s)**! Nice*")
    
    
    
    @commands.command()
    async def inv(self,ctx,user : discord.User=None):
      if user==None:
        user=ctx.author
      else:
        user=user

      await self.open_account(user)
      await self.open_shopacc(user)
      users = await self.get_shop_data()
    
      try:
        bag = users[str(user.id)]["bag"]
      except:
        bag = []
    
      em = discord.Embed(title = "__Inventory__",url="https://www.youtube.com/watch?v=dQw4w9WgXcQ",color = discord.Color.red())
      for item in bag:
        name = item["name"]
        amount = item["amount"]
        itid = item["itemid"]
        iticonn = item["icon"]
        em.add_field(name = f">> {name} {iticonn} " + f" | **{amount}**" , value = f"*ID* : `{itid}`")
        em.add_field(name = "⠀",value = "⠀")
        em.add_field(name = "⠀",value = "⠀")

        
      await ctx.send(embed = em)
      
    
    @commands.command()
    async def sell(self,ctx,item,amount = 1):
      await self.open_account(ctx.author)
    
      res = await self.sell_this(ctx.author,item,amount)
    
      if not res[0]:
        if res[1] == 1:
          await ctx.send(ctx.author.mention + ", That item does not exist!")
          return
        if res[1]== 2:
          await ctx.send(ctx.author.mention + f", you dont have {amount} {item}(s) in your bag!")
          return
        if res[1]== 3:
          await ctx.send(ctx.author.mention + f", you dont have that item!")
          return
      
      await ctx.send(ctx.author.mention + f" >> *Successfully sold **{amount} {item}(s)**! Nice*")


    @commands.command()
    async def opacmem(self,ctx,member:discord.Member):
      await self.open_shopacc(member)
      await ctx.send("opened an account for yo homie")




    @commands.command()
    async def gift(self,ctx,member:discord.Member = None, item_name = None, amount = None):
      await self.open_shopacc(member)
      for item in mainshop:
        name = item["itemid"].lower()
        if name == item_name:
          name_ = name
          price = item["price"]
          rlname = item["name"]
          iticon = item["icon"]
          break



      if member == None:
        await ctx.send(ctx.author.mention + ", please mention the recipient of the gift!")
        return
      if item_name == None:
        await ctx.send(ctx.author.mention + ", please mention the name of the gift!")
        return
      if amount == None:
        amount = 1
      
      try:
        amount=int(amount)
      except:
        await ctx.send(ctx.author.mention + ", You haven't entered a valid number!")
        return
      if amount < 0 :
        await ctx.send(ctx.author.mention + ", enter a positive integer!")
        return



      users = await self.get_shop_data()
      await self.open_shopacc(ctx.author)
      await self.open_shopacc(member)
      bag = users[str(ctx.author.id)]["bag"]
      bag2 = users[str(member.id)]["bag"]

      try:
        index = 0
        t = None
        for thing in bag:
          n = thing["itemid"]
          if n == item_name:
            old_amt = thing["amount"]
            new_amt = old_amt - amount
            if new_amt<0:
              await ctx.send(ctx.author.mention + ", you dont have that many of that item!")
              return
            users[str(ctx.author.id)]["bag"][index]["amount"] = new_amt
            t = 1
            break
        if t == None:
          await ctx.send(ctx.author.mention + ", you dont have that item!")
          return
      except:
        await ctx.send(ctx.author.mention + ", you dont have that item!")

      try:
        index = 0
        t = None
        for thing in bag2:
          n = thing["itemid"]
          if n == item_name:
            old_amt = thing["amount"]
            new_amt = old_amt + amount
            users[str(member.id)]["bag"][index]["amount"] = new_amt
            t = 1
            break
          index += 1
        if t == None:
          obj = {"itemid": item_name,"amount": amount, "name": rlname,"icon": iticon}
          users[str(member.id)]["bag"].append(obj)
      except:
        obj = {"itemid":item_name,"amount":amount, "name": rlname, "icon": iticon}
        users[str(member.id)]["bag"] = [obj]

      with open("data/shop.json","w") as f:
        f.write(json.dumps(users,indent=4))
      await ctx.send (ctx.author.mention + f" >> Succesfully gifted **{amount} {item_name}(s)** to " + member.mention + "!")














def setup(client):
    client.add_cog(shop(client))