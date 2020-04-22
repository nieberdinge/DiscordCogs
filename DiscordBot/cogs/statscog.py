import discord
from discord.ext import commands 
import asyncio

bank=[]
names = []
TEXTFILE = "DiscordMessages.txt" #textfile for text tracker
      
class User:
    def __init__(self,username):
        self.username = username
        self.wordBank = []
        self.mostUsedWord = 0

    #finds the index of the word, returns -1 if not found
    def findWord(self,word):
        word  = word.lower()
        for i in range(len(self.wordBank)):
            if word == self.wordBank[i].word:
                return i
        return -1
    #adds a word to the bank
    def addWord(self,word):
        self.wordBank.append(Word(word))

    def incrementWord(self,wordIndex):
        self.wordBank[wordIndex].count += 1
        #keeps track of the most used word
        if self.wordBank[wordIndex].count > self.wordBank[self.mostUsedWord].count:
            self.mostUsedWord = wordIndex

class Word:
    def __init__(self, word):
        self.word = word
        self.count = 1

def findPerson(person):
    for i in range(len(bank)):
        if bank[i].username == person:
            return i
    return -1

def cleanUp(word):
    notWanted = ['.','?','*',"\"","\n","%"]
    for i in notWanted:
        word.translate({ord(i) : None})
    return word

def getStats():
    bank.clear()
    username = "ERROR"
    file = open(TEXTFILE,"r",errors='ignore')
    for info in file:
        info = info[:-1]
        msg = info.split('|',1)

        #No shift+enter in the chat
        if len(msg) == 2:
            username = msg[0]
            text = msg[1]
        else:
            text = msg[0]

        #goes through each bank memeber trying to find the username
        hasBeen = False
        userIndex = 0 #Allows for eaiser access later in the function
        for i in range(len(bank)):
            if username == bank[i].username:
                hasBeen = True
                userIndex = i
        if hasBeen == False:
            bank.append(User(username))
            names.append(username)

        #splits the message by space
        text = text.split()

        for word in text: 
            word = word.lower()
            word = cleanUp(word)
            #print(username,word)
            wordIndex = bank[userIndex].findWord(word)
            if wordIndex == -1:
                bank[userIndex].addWord(word)
            else:
                bank[userIndex].incrementWord(wordIndex)
    #writeToExcel()
    file.close() 

def findWord(person, word):
    personIndex = findPerson(person)
    print(personIndex)
    index = bank[personIndex].findWord(word)
    if index == -1:
        return "You have not said that word in this channel"
    words = bank[personIndex].wordBank[index].word
    count = bank[personIndex].wordBank[index].count
    print(word,count)
    msg = "You said **{}** {} times!"
    return msg.format(words,count)

#person is a string of the name of the person you want stats of
def retreiveStats(person,choice,word):
    #workbook = load_workbook(filename="hello_world.xlsx")
    #sheet = workbook.active

    getStats()
    #print(person,names)

    if person not in names:
        return "This person has not said anything in the server."
    if choice == 1:
        personIndex = findPerson(person)
        index = bank[personIndex].mostUsedWord
        return "Your most used word is {} said {} times".format(bank[personIndex].wordBank[index].word, bank[personIndex].wordBank[index].count)
    else:
        return findWord(person,word)
        

def textTracker(author, message):
    f = open(TEXTFILE,"a")
    f.write("\n"+str(author)+"|"+str(message))
    f.close()


class Stats(commands.Cog):

    def __init__(self, client):
        self.client = client
        self.user = client.user
        self.guild = client.guilds

    #Events
    @commands.Cog.listener()
    async def on_ready(self):
        print("Stats cog online.")

    #says when a user had joined
    @commands.command(pass_context=True)
    async def join(self, ctx):
        for guild in self.guild:
                if(guild == self.client.message.guild):
                    guild.get_member()

    #tracks messages
    @commands.Cog.listener()
    async def on_message(self, message):
        if message.author == self.user:
            return 
        print("Author: ", message.author, "Body: ", message.content)
        textTracker(message.author,message.content)

    #Commands 
    @commands.command(pass_context=True)
    async def stats(self,ctx):
        person = ctx.message.author
        #print(person)
        await ctx.send('What would you like to look at?\n1. Most said word\n2. A specific word')
        def is_correct(m):
            return m.author == ctx.message.author and m.content.isdigit()
        try:
            choice = await self.client.wait_for('message', check=is_correct, timeout=5.0)
        except asyncio.TimeoutError:
            return ctx.send('Sorry, you took too long.')
        choice = int(choice.content)

        if choice > 2 or choice < 1:
                await ctx.send("That is not a valid choice")
        else:
            word =""
            if choice == 2:
                await ctx.send("What word would you like to look up?")
                try:
                    word = await self.client.wait_for('message', timeout=10.0)
                    word = word.content
                except asyncio.TimeoutError:
                    return await ctx.send('Sorry, you took too long.')
                
            msg = retreiveStats(person,choice,word)
            if msg == "Ths person has not said anything in the server.":
                    await ctx.send(msg)
            else:
                await ctx.send('{}\n'.format(ctx.author.mention)+msg)  
    

def setup(client):
    client.add_cog(Stats(client))

