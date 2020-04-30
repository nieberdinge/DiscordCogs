import asyncio
import discord
from discord.ext import commands 
from datetime import datetime
from pytz import all_timezones,timezone


class Person():
    def __init__(self,name):
        self.turnips = []
        self.name = name
        self.timezone = "US/Eastern"

    def addPrice(self,price):
        d = datetime.now(timezone(self.timezone))
        #"Time,AM/PM",PRICE
        time = d.strftime("%a:%p")
        print(time,price)
        if len(self.turnips) != 0 and self.turnips[-1][0] == time:
            self.turnips[-1] = (time,price)
        else:
            self.turnips.append((time,price))

    def prices(self):
        msg = ""
        for i in self.turnips:
            msg += i[0] + " " + str(i[1]) + "\n"
        return msg 


      


class turnip(commands.Cog):

    def __init__(self, client):
        self.client = client
        self.people = []
        self.week = 0
        self.filename = "turnip.txt"

    def findPerson(self,name):
        for i in range(len(self.people)):
            print(self.people[i].name)
            if self.people[i].name == name:
                return i
        return -1


    #how I want files to look like
    #Week Number
    #USERNAME | TIMEZONE
    #Sun:AM,PRICE|Mon:AM,PRICE| ... | SAT:PM,PRICE
    #repeats username and day until out of players
    def writeTurn(self):
        f = open(self.filename,"w")
        f.write("{}".format(datetime.strftime("%U")))
        for person in self.people:
            f.write("{}|{}".format(person.name, person.timezone))
            msg = "" 
            for day in person.turnips:
                msg += day[0] + "," + day[1] + "|"
            f.write(msg)
        f.close()

    def openTurn(self):
        f = open(self.filename, 'r') 
        self.week = int(f.readline())
        allPeople = f.readlines()
        f.close()
        for i in range(0,len(allPeople),2):
            #gets name and timezone
            self.people.append(allPeople[i].split('|')[0])
            self.people[-1].timezone = allPeople[i].split('|')[1]
            #splits up dates
            arr = allPeople[i+1].split('|')
            for date in arr:
                turnips = tuple(date.split(',')) 
                self.people[-1].turnips.append(turnips)




    @commands.command(pass_context=True)
    async def highest(self,ctx):
        d = datetime.now()
        #"Time:AM/PM",PRICE
        time = d.strftime("%a:%p")
        highest = 0
        highName = "No one sucka"    
        for i in self.people:
            if i.turnips[-1][1] > highest and i.turnips[-1][0] == time:
                highest = i.turnips[-1][1]
                highName = i.name 
        if highName == "No one sucka":
            await ctx.send("No one has updated the turnip list for the current time")
        else:
            index = self.findPerson(highName)
            await ctx.send("{} ({}) has the highest reported price at {} bells".format(highName,self.people[index].timezone,highest))

    
    
    @commands.command(pass_context=True)
    async def getPrices(self, ctx):
        self.openTurn()
        index = self.findPerson(ctx.message.author)
        print(index)
        msg = self.people[index].prices()
        await ctx.send("{}, here is your prices for the week:".format(ctx.message.author))
        await ctx.send(msg)

    @commands.command(pass_context=True)
    async def all(self,ctx):
        self.openTurn()
        for i in self.people:
            msg = i.prices()
            await ctx.send("{} prices are:\n{}".format(i.name,msg))
    
    @commands.Cog.listener()
    async def on_ready(self):
        print("turnip cog online.")

    @commands.command(pass_context=True)
    async def add(self,ctx,price : int):
        index = self.findPerson(ctx.message.author)
        d = datetime.now()
        time = d.strftime("%a:%p")

        await ctx.send("What is your turnip price?")

        def is_correct(m):
            return m.author == ctx.message.author and m.content.isdigit()

        #gets User input  for price
        try:
            price = await self.client.wait_for('message', check=is_correct, timeout=60.0)
        except asyncio.TimeoutError:
            return ctx.send('Sorry, you took too long.')
        price = int(price.content)
        

        if(index == -1):
            await ctx.send("Added {} to this weeks turnips.".format(ctx.message.author.mention))
            self.people.append(Person(ctx.message.author))
            msg = "Currently your timezone is {}\nIs this correct?\n1. Yes\n2. No".format(self.people[-1].timezone)
            await ctx.send(msg)
            try:
                choice = await self.client.wait_for('message', check=is_correct, timeout=60.0)
            except asyncio.TimeoutError:
                return ctx.send('Sorry, you took too long. Your timezone was not changed')
            
            if(int(choice.content) == 2):
                await ctx.send("Please use !setTime to change your time")
        if time == "Sun:AM":
            self.people[index].turnip.clear()
        self.people[index].addPrice(price)
        await ctx.send("Added your turnip")
        self.writeTurn()


    
    @commands.command(pass_context=True)
    async def setTime(self,ctx):
        index = self.findPerson(ctx.message.author)
        await ctx.send("Your current time zone is {} ".format(self.people[index].timezone))
        await ctx.send("Please choose a number corresponding to your timezone")
        counter = 0
        msg = ""
        usTime = []
        for zone in all_timezones:
            if 'US' in zone:
                counter += 1 
                msg += "{}. {}\n".format(counter, zone)
                usTime.append(zone)
        await ctx.send(msg)

        def is_correct(m):
            return m.author == ctx.message.author and m.content.isdigit() and int(m.content) > 0 and int(m.content) < len(usTime)

        try:
            timezone = await self.client.wait_for('message', check=is_correct, timeout=60.0)
        except asyncio.TimeoutError:
            return ctx.send('Sorry, you took too long.')
        


        self.people[index].timezone = usTime[int(timezone.content)-1]

        await ctx.send("Your timezone is now {}".format(self.people[index].timezone))
        

        


def setup(client):
    client.add_cog(turnip(client))


