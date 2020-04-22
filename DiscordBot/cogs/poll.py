import discord
from discord.ext import commands 
import asyncio


class poll(commands.Cog):

    def __init__(self, client):
        self.client = client
        self.question = ""
        self.choices = []
        self.votes = []
    



    @commands.Cog.listener()
    async def on_ready(self):
        print("poll cog online.")

    @commands.command()
    async def startPoll(self,ctx):
        self.choices.clear()
        self.votes.clear()
        await ctx.send("What is your poll question?")
        try:
            choice = await self.client.wait_for('message', timeout=60.0)
        except asyncio.TimeoutError:
            return ctx.send('Sorry, you took too long.')
        self.question = str(choice.content)
        await ctx.send("What are the options?\nEnter each option as its own message\nType STOP to stop entering options")
        message = ""
        while(message.lower() != "stop"):
            try:
                choice = await self.client.wait_for('message', timeout=60.0)
                message = choice.content
            except asyncio.TimeoutError:
                return ctx.send('Sorry, you took too long.')
            if(message.lower() != "stop"):
                self.choices.append(message)
                self.votes.append(0)
        ctx.send("Stopped adding questions.\nUse !vote to vote")

    @commands.command()    
    async def vote(self,ctx):
        ctx.send("Here are your choices:")
        for i in range(len(self.choices)):
            msg = "{}. {}"
            await ctx.send(msg.format(i+1,self.choices[i]))

        await ctx.send("Please choose a number")
        def is_correct(m):
            return m.author == ctx.message.author and m.content.isdigit()
        try:
            choice = await self.client.wait_for('message', check=is_correct, timeout=5.0)
        except asyncio.TimeoutError:
            return ctx.send('Sorry, you took too long.')
        choice = int(choice.content)
        if(choice<1 or choice > len(self.choices)):
            ctx.send("That is not a valid choice. Please vote again.")
        else:
            self.votes[choice-1] += 1
            print(self.votes)
            ctx.send("Vote counted.")

    
    @commands.command()    
    async def endPoll(self,ctx):
        await ctx.send("POLLS ARE ENDED!")
        ctx.send("Here are the results:")
        for i in range(len(self.choices)):
            msg = "{}. {} with {} votes!"
            await ctx.send(msg.format(i+1,self.choices[i],self.votes[i]))

        


def setup(client):
    client.add_cog(poll(client))