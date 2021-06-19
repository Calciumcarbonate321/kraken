import discord
import json
import random
import os
from discord.ext import commands
from discord.ext.commands import Cog
from cogs.bank import bank
from cogs.shopsys import shop

class equip(commands.Cog):
    '''This cog has the item usage command of bot economy'''

    def __init__(self,client):
        self.client=client
        self.bi=shop(client)

    @commands.command()
    async def equip(self,ctx,item=None):    
        users = await self.bi.get_shop_data()
        invt = users[str(ctx.author.id)]["Inventory"]
        bag = users[str(ctx.author.id)]["bag"]
        if item == None:
            await ctx.send("what are you trying to equip?!") 
            return
        for thing in invt:              
            n = thing["equipped"] 
            if n == item:
                await ctx.send("you already have that equipped!")
                return
            if n != "Nothing" and n != item:
                await ctx.send("You already have an item equipped!")
                return
            break



        try:
            index = 0
            t = None
            for thing in bag:
                itid = thing["itemid"]  
                amount = thing["amount"]
                iname = thing["name"]
                eicon = thing["icon"]
                if itid == item:
                    amount = thing["amount"]
                    new_amt = amount - 1
                    if amount == 0:
                        await ctx.send("you dont have that item")
                        return
                    users[str(ctx.author.id)]["bag"][index]["amount"] = new_amt
                    ranx = 0
                    for itemz in invt:
                        if itemz["equipped"] == "Nothing":
                            ranx = 1
                        break
                    if ranx == 1:
                        for itemz in invt:
                            itemz["equipped"] = itemz["equipped"].replace("Nothing", item)
                            itemz["eqname"] = itemz["eqname"].replace("Noname", iname)     
                            itemz["eqicon"] = itemz["eqicon"].replace("None", eicon)    
                            itemz["eqamt"] = 1
                            break
                    else:
                        obj = {"equipped": item,"eqname": iname,"eqamt": 1,"eqicon": eicon} 
                        users[str(ctx.author.id)]["Inventory"].append(obj)                  
                    t = 1
                    break
                index+=1 
        
            if t == None:
                await ctx.send("you dont have that item") 
                return
        except:
            await ctx.send("You dont have that item")
            return
                    
        with open("data/shop.json","w") as f:
            f.write(json.dumps(users,indent=4))
        await ctx.send(ctx.author.mention + f" >> Succesfully equipped **{iname}**!") 

    @commands.command()
    async def unequip(self,ctx):
        await self.bi.open_shopacc(str(ctx.author.id))
        users = await self.bi.get_shop_data()
        invt = users[str(ctx.author.id)]["Inventory"]
        bag = users[str(ctx.author.id)]["bag"]
        for thing in invt:
            eqp = thing["equipped"]
            eqp1 = thing["eqname"]
            eqp2 = thing["eqamt"]
            eqp3 = thing["eqicon"]
            if eqp == None or eqp =="Nothing": 
                await ctx.send("You have nothing equipped")
                return
            break
        try:
            index = 0
            t = None
            for thing in bag:
                itid = thing["itemid"]
                amount = thing["amount"]
                iname = thing["name"]
                if itid == eqp:
                    nothing = "Nothing"
                    amount = thing["amount"]
                    amount = int(amount)
                    new_amt = amount + 1
                    users[str(ctx.author.id)]["bag"][index]["amount"] = new_amt
                    tempnum = 0
                    for item in invt:
                        item["equipped"] = item["equipped"].replace(eqp, "Nothing") 
                        item["eqname"] = item["eqname"].replace(eqp1, "Noname")     
                        item["eqicon"] = item["eqicon"].replace(eqp3, "None")       #
                        item["eqamt"] = 0                                          

                    t = 1
                    break
                index+=1
                
            if t == None:
                await ctx.send("You dont have that item equipped") 
                return
        except:
            await ctx.send("that item does not exist")
            return
                    
        with open("data/shop.json","w") as f:
            f.write(json.dumps(users,indent=4))
        await ctx.send(ctx.author.mention + f" >> Succesfully unequipped **{iname}**!")






def setup(client):
    client.add_cog(equip(client))