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
          break
    
    
      if name_ == None:
        return [False,1]
      
      cost = int(price) * int(amount)
      cost = int(cost)
    
      users = await self.get_shop_data()
    
      bal = await self.bi.get_wallet(str(user.id))
    
    
      if bal<cost:
        print(bal)
        print(cost)
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
          obj = {"itemid": item_name,"amount": amount, "name": rlname}
          users[str(user.id)]["bag"].append(obj)
      except:
        obj = {"itemid":item_name,"amount":amount, "name": rlname}
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
      
      cost=price * amount
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
          await ctx.send("wrong store buddy, we dont have that item")
          return
        if res[1] ==2:
          await ctx.send(f"you dont have enough money to buy {item}")
          return
        
      await ctx.send(f"You just bought {amount} {item} ! pogchamp")
    
    
    
    @commands.command()
    async def bag(self,ctx,user : discord.User):
      if user==None:
        user = ctx.author
        return
      else:
        user=user

      await self.open_account(ctx.author)
      await self.open_shopacc(ctx.author)
      
      users = await self.get_shop_data()
    
      try:
        bag = users[str(user.id)]["bag"]
      except:
        bag = []
    
      em = discord.Embed(title = "Bag",color = discord.Color.red())
    
      for item in bag:
        name = item["name"]
        amount = item["amount"]
        em.add_field(name = name , value = amount)
        
      await ctx.send(embed = em)
      
    
    @commands.command()
    async def sell(self,ctx,item,amount = 1):
      await self.open_account(ctx.author)
    
      res = await self.sell_this(ctx.author,item,amount)
    
      if not res[1]:
        if res[1] == 1:
          await ctx.send("that object aint here")
          return
        if res[1]== 2:
          await ctx.send(f"you dont have {amount} {item} in your bag bruh")
          return
        if res[1]== 3:
          await ctx.send(f"you dont have {item} in your bag dumbass")
          return
      
      await ctx.send(f"you sold {amount} {item}, pog")



def setup(client):
    client.add_cog(shop(client))