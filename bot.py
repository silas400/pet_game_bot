import discord
from discord.ext import commands, tasks
from discord.ext.commands import Bot
import sqlite3
import os.path
from os import path
import random
import time
import asyncio
from datetime import datetime
import pytz
from threading import Thread
import string

#Had to enable intents for members so I can access all member objects from a server. I also had to turn on the SERVER MEMBERS INTENT on the bot page in "bot" settings.
intents = discord.Intents.all()
intents.members = True
intents.guilds = True

client = commands.Bot(intents=intents, command_prefix = '.') #Had to include intents to add members to the server.

client.remove_command('help') #Removes the default help command so we can freely use a custom one

@client.event
async def on_ready():
    print('Bot Is Ready!')

    await client.change_presence(activity=discord.Game('.help'))

    # *These starts background tasks that will keep looping without interrupting anything
    new.start()
    
    new.stop() #This stops a background task AFTER its current iteration. Useful for when I need to only execute a background task once.
    
    hatchTimer.start()
    updateGamble.start()
    decay.start()
        
#Sends PM message of all the avaliable commands when user types '!help'
@client.command(pass_context=True)
async def help(ctx):
    author = ctx.message.author

    ID = '<@' + str(ctx.message.author.id) + '>' #Constructs the User's ID to @ them.

    embed = discord.Embed(
        colour = discord.Colour.orange()
    )

    embed.set_author(name="() = Required and [] = Optional || Each Input is separated by a space")
    embed.set_image(url="https://cdn.discordapp.com/attachments/444221100071583756/759601750574497792/unknown.png")
    embed.add_field(name='.gamble (amount)', value='Allows you to gamble a portion of your bounty', inline=False)
    embed.add_field(name='.bounty [@Friend]', value="Allows you to check your bounty or a friend's", inline=False)
    embed.add_field(name='.search (Pet Name OR ID) [Last Name]', value="Allows you to pull up a pet's picture and stats", inline=False)
    embed.add_field(name='.rename (Original Name OR ID) (New Name) [Last Name]', value="Allows you to rename a pet that you own", inline=False)
    embed.add_field(name='.unname (Original Name OR ID) [Last Name]', value="Allows you to erase the name of a pet", inline=False)
    embed.add_field(name='.lotprice', value="Tells you how much you would have to pay in order to buy an egg", inline=False)
    embed.add_field(name='.lot', value="Spends some of your points in order to purchase an egg", inline=False)
    embed.add_field(name='.sell (Pet Name OR ID) [Last Name]', value="Allows you to sell one of your pets", inline=False)
    embed.add_field(name='.pets [@Friend]', value="Allows you to view a list of your (or a friend's) pet names and associated ID's.", inline=False)
    embed.add_field(name='.givepet (@Friend) (Pet Name OR ID) [Last Name]', value="Allows you to give one of your pets to a friend", inline=False)
    embed.add_field(name='.feed (Original Name OR ID) [Last Name]', value="Allows you to feed one of your pets.", inline=False)
    embed.add_field(name='.play (Original Name OR ID) [Last Name]', value="Allows you to play with one of your pets.", inline=False)
    
    

    await ctx.send(embed=embed)

@client.command(aliases=['GAMBLE', 'g', 'G'])
async def gamble(ctx, amount):
    ID = '<@' + str(ctx.message.author.id) + '>' #Constructs the User's ID to @ them.


    choice = random.randint(0, 1) #Randomizes whether the user will gain or lose the amount.

    conn = sqlite3.connect('gamble.db') # connect to the database

    c = conn.cursor() #Create a cursor to browse the database

    c.execute("select * FROM players WHERE userID=?", (ID,))

    rows = c.fetchall()

    if int(amount) > int(rows[0][2]) or int(amount) < 0:
        await ctx.send('No')

    else:

        if choice == 0:

            newAmount = int(rows[0][2]) + int(amount)
            await ctx.send('You Won! ' + ID)

        else:

            newAmount = int(rows[0][2]) - int(amount)
            await ctx.send('You Lost! ' + ID)


        c.execute("UPDATE players SET points=? WHERE userID=?", (newAmount, ID))

    conn.commit()

    conn.close()

@client.command(aliases=['BOUNTY', 'b', 'B'])
async def bounty(ctx, friendID=None):
    ID = '<@' + str(ctx.message.author.id) + '>' #Constructs the User's ID to @ them.

    if friendID != None:
        ID = friendID = friendID.replace("!", '')

    conn = sqlite3.connect('gamble.db') # connect to the database

    c = conn.cursor() #Create a cursor to browse the database

    c.execute("select * FROM players WHERE userID=?", (ID,))

    rows = c.fetchall()

    if friendID == None:
        await ctx.send(ID + ' Your Bounty Is ' + str(rows[0][2]))

    else:
        await ctx.send(ID + "'s Bounty Is " + str(rows[0][2]))
            
@client.command(aliases=['SEARCH', 's', 'S'])
async def search(ctx, ID, last=None):

    print(ID)

    if last != None:
        ID = ID + ' ' + last

    userID  = '<@' + str(ctx.message.author.id) + '>' 

    if ID != '???':
        
        conn = sqlite3.connect('gamble.db') # connect to the database

        c = conn.cursor() #Create a cursor to browse the database

        c.execute("select * FROM pets WHERE ID=? OR name=?", (ID, ID))

        rows = c.fetchall()

        #If the first query does not find anything, check the database with full uppercase, full lowercase, and then title case.
        if len(rows) == 0:
            c.execute("select * FROM pets WHERE ID=? OR name=?", (ID.upper(), ID.upper()))

            rows = c.fetchall()

            if len(rows)== 0:

                c.execute("select * FROM pets WHERE ID=? OR name=?", (ID.lower(), ID.lower()))

                rows = c.fetchall()

                if len(rows)== 0:

                    c.execute("select * FROM pets WHERE ID=? OR name=?", (ID.title(), ID.title()))

                    rows = c.fetchall()
    
        #If there are more than 2 rows found, find the one that belongs to the intiator of the command
        if len(rows) >= 2:
            
            index = 0

            #Convert the tuple into a list so I can use the pop function properly
            for x in range(len(rows)):

                rows[index] = list(rows[index])

                index += 1
                
            print(rows)

            index = 0

            #Figure out which ID does not match the command sender, and destroy it.
            for k in rows:

                if k[8] != userID:
                    rows.pop(index)

                index +=1

        c.execute("select * from players where userID=?", (rows[0][8],))

        rows2 = c.fetchall()
            
        conn.commit()

        conn.close()

        

        embed = discord.Embed(
            colour = discord.Colour.orange()
        )

        
        embed.set_author(name=rows[0][1]) #Pet Name
        

        if int(rows[0][6]) == 0:

            
            
            embed.set_image(url=rows[0][2])# Pet Image Link

            embed.add_field(name='Owner', value=rows2[0][1], inline=True) #Player Name

            embed.add_field(name='ID', value=rows[0][0], inline=True) #ID
        
            embed.add_field(name='Rarity', value=rows[0][5], inline=True) #Rarity
        
            embed.add_field(name='Age', value=str(int(int(rows[0][7]) / 1440)) + ' (Days)', inline=True) #Age

            mood = 'Happy'

            hunger = 'Full'

            if int(rows[0][3]) < 80:
                mood = 'Sad'

            if int(rows[0][4]) < 50:
                hunger = 'Hungry'

            embed.add_field(name='Mood', value= mood + ' (' + rows[0][3] + ')', inline=True) #Mood

            embed.add_field(name='Hunger', value= hunger + ' (' + rows[0][4] + ')', inline=True) #Mood

            

        else:
            embed.set_image(url='https://cdn.discordapp.com/attachments/854779378134941726/855241266757632030/egg.png')#Egg Image

            embed.add_field(name='ID', value=rows[0][0], inline=False) #Rarity

            embed.add_field(name='Age', value='0', inline=False) #Age


        await ctx.send(embed=embed)


@client.command(aliases=['RENAME', 'rn', 'RN'])
async def rename(ctx, ID, name, last=None):

    userID = '<@' + str(ctx.message.author.id) + '>'

    if last != None:
        name = name + ' ' + last

    conn = sqlite3.connect('gamble.db') # connect to the database

    c = conn.cursor() #Create a cursor to browse the database

    c.execute("select * FROM pets WHERE ID=? AND owner=? OR name=? and owner=?", (ID, userID, ID, userID))

    rows = c.fetchall()

    c.execute("UPDATE pets SET name=? WHERE ID=? AND owner=? OR name=? AND owner=?", (name, ID, rows[0][8], ID, rows[0][8]))

    await ctx.send(userID + ' Pet Renamed!')

    conn.commit()

    conn.close()

@client.command(aliases=['lotteryprice', 'LOTPRICE', 'LOTTERYPRICE', 'lp', 'LP'])
async def lotprice(ctx):

    userID = '<@' + str(ctx.message.author.id) + '>'

    conn = sqlite3.connect('gamble.db') # connect to the database

    c = conn.cursor() #Create a cursor to browse the database

    c.execute('select * FROM pets where owner=?',(userID,))

    rows = c.fetchall()

    price = (len(rows) * 10) + 60

    await ctx.send(userID + ' The Lottery Price For You Is ' + str(price))

    
    

@client.command(aliases=['lottery', 'LOT', 'LOTTERY', 'l', 'L'])
async def lot(ctx):

    userID = '<@' + str(ctx.message.author.id) + '>'

    conn = sqlite3.connect('gamble.db') # connect to the database

    c = conn.cursor() #Create a cursor to browse the database

    c.execute('select * FROM players where userID=?',(userID,))

    rows = c.fetchall()

    c.execute('select * FROM pets where owner=?',(userID,))

    petRows = c.fetchall()

    price = len(petRows) * 10

    price += 60

    print(price)

    if int(rows[0][2]) >= price:
        

        lottery = []
            
        result = random.randint(1, 6)

        if result == 1:
            rarity = 3

        elif result == 2 or result == 3:
            rarity = 2

        else:
            rarity = 1

        ID = ''

        while True:
            for x in range(4):
                ID += random.choice(string.ascii_letters)

            c.execute('select * from pets where ID=?', (ID,))

            rows = c.fetchall()

            print(len(rows))

            if len(rows) == 0:
                c.execute('select * FROM players where userID=?',(userID,))
                rows = c.fetchall()
                break

            else:
                ID = ''
                continue
                    

        c.execute("update players set points=? WHERE userID=?", (int(rows[0][2]) - price, userID))
        

        c.execute("select * FROM potential_pets WHERE rarity=?", (str(rarity)))

        rows = c.fetchall()

        end = len(rows)

        i = random.randint(0,end-1)

        if len(rows) != 0:
            c.execute("insert into pets values(?,?,?,?,?,?,?,?,?)", (ID, '???', rows[i][0], '100', '100', rarity, '100', '0', userID))

    
        await ctx.send('You have obtained an Egg!')
        
    else:

        await ctx.send('You do not have enough points!')

    conn.commit()

    conn.close()


@client.command(aliases=['SELL'])
async def sell(ctx, pet, last=None):

    ID = '<@' + str(ctx.message.author.id) + '>'

    if last != None:

        pet = pet + ' ' + last

    conn = sqlite3.connect('gamble.db') # connect to the database

    c = conn.cursor() #Create a cursor to browse the database

    c.execute('select * from pets WHERE ID=? AND owner=? OR owner=? AND name=?', (pet, ID, ID, pet))

    rows = c.fetchall()

    if len(rows) == 0:
        c.execute('select * from pets WHERE ID=? AND owner=? OR owner=? AND name=?', (pet, ID, ID, pet.upper()))
        rows = c.fetchall()
        pet = pet.upper()

        if len(rows) == 0:
            c.execute('select * from pets WHERE ID=? AND owner=? OR owner=? AND name=?', (pet, ID, ID, pet.lower()))
            rows = c.fetchall()
            pet = pet.lower()

            if len(rows) == 0:
                c.execute('select * from pets WHERE ID=? AND owner=? OR owner=? AND name=?', (pet, ID, ID, pet.title()))
                rows = c.fetchall()
                pet = pet.title()

    if len(rows) == 0:
        await ctx.send('Could Not Find Pet To Sell!')

    else:

        def check(message):

            user = '<@' + str(message.author.id) + '>'
            
            return message.content.upper() == 'YES' and user == ID or message.content.upper() == 'Y' and user == ID or message.content.upper() == 'NO' and user == ID or message.content.upper() == 'N' and user == ID
        
        await ctx.send(ID + ' Type either "YES" OR "Y" to confirm the sell of your pet. Type "NO" or "N" to reject the sell')
        while True:
            try:
                message = await client.wait_for('message', timeout=60, check=check)

                if message.content.upper() == 'YES' or message.content.upper() == 'Y':

                    c.execute('delete from pets WHERE ID=? AND owner=? OR owner=? AND name=?', (pet, ID, ID, pet))

                    petAge = int(rows[0][7]) / 1440

                    c.execute('select * from players where userID=?',(ID,))

                    rows = c.fetchall()

                    sellAmount = 4 * petAge

                    newPoints = int(rows[0][2]) + int(sellAmount) + 50

                    c.execute('update players set points=? WHERE userID=?', (str(newPoints), ID,))

                    await ctx.send(ID + ' Pet Sold!')

                elif message.content.upper() == 'NO' or message.content.upper() == 'N':
    
                    await ctx.send('You decided not to perish your pet... WHEW!')

                break

            except asyncio.TimeoutError:
                await ctx.send(ID + ' Timer Ran Out!')
                break


    conn.commit()

    conn.close()
                  

    
        
        

@client.command(aliases=['PETS', 'p', 'P'])
async def pets(ctx, friendID=None):
    
    if friendID == None:
        ID = '<@' + str(ctx.message.author.id) + '>'
    else:
        ID = friendID.replace("!", '') #For some reason there was an additional exclamation mark in the beginning?

    

    conn = sqlite3.connect('gamble.db') # connect to the database

    c = conn.cursor() #Create a cursor to browse the database

    c.execute("select * FROM pets WHERE owner=?", (ID,))

    rows = c.fetchall()

    newList = [] #Making a new list that will be sorted into a list that contains other lists containing 8 elements each

    tempList = [] #Just a templist meant to contain and then release 8 elements each

    rowIndex = -1 # This is meant to keep track of the row that was unable to reach 8 elements each

    #Starts creating a list of lists that contain 8 elements each
    for k in rows:

        pet = k[1] + ' - ' + k[0]
        
        tempList.append(pet)
            
        if len(tempList) == 8:
            newList.append(tempList)
            tempList = [] #Clear the tempList when it reaches 8 elements
            continue
            
        rowIndex += 1 #Records the row that was last used
        
    cutOff = len(rows[rowIndex]) % 8 #Figures out how many times 8 goes into the amount of elements in the row that was recorded last

    print('Cutoff Is ' + str(cutOff))

    #If 8 did not go perfectly into the amount of the elements for the last list in the main list, then we gotta add those into the new array
    if cutOff != 0 and len(rows) >= 8 and len(tempList) != 0:

        print('hm?')
        
        newList.append(tempList) #tempList should of the remnants of the elements that need to be added

    print(newList)
    

    end = len(newList)

    page = 0 # Really means page 1

    c.execute("select * FROM players WHERE userID=?", (ID,))

    rows2 = c.fetchall()

    conn.commit()

    conn.close()
    
    

    embed = discord.Embed(
        colour = discord.Colour.orange()
    )

    embed.set_author(name=rows2[0][1] + ' Pets! - ' + str(page)) #Player Name

    if len(newList) == 0:
        
        for k in rows:
        
            embed.add_field(name=k[1] + ' - ' + k[0], value = '---------------', inline=False) #Pet ID and Name

        await ctx.send(embed=embed)
        

    else:
        
        for x in range(len(newList[page])):

            embed.add_field(name=newList[page][x], value='-------------', inline=False)

        message = await ctx.send(embed=embed)
        
        await message.add_reaction("⬅")
        await message.add_reaction("➡")

        def check(reaction, user):
            return str(reaction.emoji) in ["⬅", "➡"] and user == ctx.author and reaction.message == message

        while True:
            try:
                
                reaction, user = await client.wait_for("reaction_add", timeout=60, check=check) #Returns the reaction and user if it passes the check.
                                                                                                #Will not continue execution otherwise

                embed = discord.Embed(
                    colour = discord.Colour.orange()
                )

                if str(reaction.emoji) == "➡" and page + 1 < end:
                    page += 1

                elif str(reaction.emoji) == "⬅" and page > 0:
                    page -= 1
    

                embed.set_author(name='Page ' + str(page + 1))

                for x in range(len(newList[page])):
                    
                    embed.add_field(name=newList[page][x], value='-------------', inline=False)

                await message.remove_reaction(reaction, user)

                await message.edit(embed=embed)

            except asyncio.TimeoutError:
                break


@client.command(aliases=['UNNAME'])
async def unname(ctx, name, last=None):

    ID = '<@' + str(ctx.message.author.id) + '>'

    if last != None:

        name = name + ' ' + last
    
    conn = sqlite3.connect('gamble.db') # connect to the database

    c = conn.cursor() #Create a cursor to browse the database

    c.execute("select * FROM pets WHERE owner=? AND name=? OR ID=?", (ID,name, name))

    rows = c.fetchall()

    await ctx.send(rows[0][1])

    c.execute("update pets SET name=? WHERE ID=?", ('???', rows[0][0]))

    await ctx.send(ID + ' Pet has been unnamed!')

    conn.commit()

    conn.close()

@client.command(aliases=['ADD'])
async def add(ctx, rarity, link):

    conn = sqlite3.connect('gamble.db') # connect to the database

    c = conn.cursor() #Create a cursor to browse the database

    c.execute("insert into potential_pets values(?,?)", (link, rarity))

    conn.commit()

    conn.close()

    await ctx.send('Pet Added into the database!')

@client.command(aliases=['SET'])
async def set(ctx, amount):

    ID = '<@' + str(ctx.message.author.id) + '>'

    conn = sqlite3.connect('gamble.db') # connect to the database

    c = conn.cursor() #Create a cursor to browse the database

    c.execute("update players set points=? WHERE userID=?", (amount, ID))

    conn.commit()

    conn.close()

    await ctx.send('Point Adjusted!')

    

@client.command(aliases=['TOTAL'])
async def total(ctx, rarity = None):
    

    conn = sqlite3.connect('gamble.db') # connect to the database

    c = conn.cursor() #Create a cursor to browse the database

    if rarity != None:

        if rarity == '1':
            petType = 'Cats And Dogs'

        elif rarity == '2':
            petType = 'Horses'

        else:
            petType = 'Dragons'

        c.execute("select * FROM potential_pets WHERE rarity=?", (rarity))

        rows = c.fetchall()

        await ctx.send('There are ' + str(len(rows)) + ' ' + petType)


    else:
        c.execute("select * FROM potential_pets")

        rows = c.fetchall()

        await ctx.send('There are ' + str(len(rows)) + ' Unique Pets!')


    conn.commit()

    conn.close()



@client.command(aliases=['GIVEPET'])
async def givepet(ctx, friendID, pet, last=None):

    ID = '<@' + str(ctx.message.author.id) + '>'

    friendID = friendID.replace("!", '')

    if last != None:
        pet = pet + ' ' + last

    def check(message):
        print(message.content.upper)
        return message.content.upper() == 'YES' and '<@' + str(message.author.id) + '>' == friendID or message.content.upper() == 'Y' and '<@' + str(message.author.id) + '>' == friendID or message.content.upper() == 'NO' and '<@' + str(message.author.id) + '>' == friendID or message.content.upper == 'N' and '<@' + str(message.author.id) + '>' == friendID

    await ctx.send(friendID + ' Type either "YES" OR "Y" to accept this pet. Type "NO" or "N" to reject the pet')
    message = await client.wait_for('message', check=check)

    if message.content.upper() == 'YES' or message.content.upper() == 'Y':

        await ctx.send('Pet Accepted!')

        conn = sqlite3.connect('gamble.db') # connect to the database

        c = conn.cursor() #Create a cursor to browse the database

        c.execute('update pets set owner=? WHERE owner=? AND ID=? OR name=? and owner=?', (friendID, ID, pet, pet, ID,))

        conn.commit()

        conn.close()

    else:
        await ctx.send('Gift Rejected!')

@client.command(aliases=['GIVEPOINTS'])
async def givepoints(ctx, friendID, pointAmount):
    
    ID = '<@' + str(ctx.message.author.id) + '>'

    friendID = friendID.replace("!", '')

    conn = sqlite3.connect('gamble.db') # connect to the database

    c = conn.cursor() #Create a cursor to browse the database

    c.execute('select * from players where userID=?',(ID,))

    rows = c.fetchall()

    conn.commit()

    conn.close()

    playerPoints = int(rows[0][2])

    if playerPoints <  int(pointAmount):

        await ctx.send(ID + ' You do not have this many points to give!')

    elif int(pointAmount) < 0:
        
        await ctx.send(ID + ' LOL!! Silly Person.')
        
    else:
        
        def check(message):
            print(message.content.upper)
            return message.content.upper() == 'YES' and '<@' + str(message.author.id) + '>' == friendID or message.content.upper() == 'Y' and '<@' + str(message.author.id) + '>' == friendID or message.content.upper() == 'NO' and '<@' + str(message.author.id) + '>' == friendID or message.content.upper == 'N' and '<@' + str(message.author.id) + '>' == friendID

        await ctx.send(friendID + ' Type either "YES" OR "Y" to accept these points. Type "NO" or "N" to reject the points') 
        message = await client.wait_for('message', check=check)

        if message.content.upper() == 'YES' or message.content.upper() == 'Y':

            await ctx.send('Points Accepted!')

            conn = sqlite3.connect('gamble.db') # connect to the database

            c = conn.cursor() #Create a cursor to browse the database

            newPoints = playerPoints - int(pointAmount)

            c.execute('update players set points=? WHERE userID=?', (str(newPoints), ID,))

            c.execute('select * from players where userID=?',(friendID,))

            rows = c.fetchall()

            newPoints = int(rows[0][2]) + int(pointAmount)
            
            c.execute('update players set points=? WHERE userID=?', (str(newPoints),friendID,))

            conn.commit()

            conn.close()

        else:
            await ctx.send(ID, ' Points Rejected')


    


@client.command(aliases=['FEED', 'f', 'F'])
async def feed(ctx, pet, last=None):

    ID = '<@' + str(ctx.message.author.id) + '>'

    if last != None:

        pet = pet + ' ' + last
    
    conn = sqlite3.connect('gamble.db') # connect to the database

    c = conn.cursor() #Create a cursor to browse the database

    c.execute('select * from pets where owner=? and ID=? OR name=? AND owner=?', (ID, pet, pet, ID,))

    rows = c.fetchall()

    if len(rows) == 0:
        c.execute('select * from pets where owner=? and ID=? OR name=? AND owner=?', (ID, pet, pet.upper(), ID,))
        rows = c.fetchall()
        pet = pet.upper()

        if len(rows) == 0:
            c.execute('select * from pets where owner=? and ID=? OR name=? AND owner=?', (ID, pet, pet.lower(), ID,))
            rows = c.fetchall()
            pet = pet.lower()

            if len(rows) == 0:
                c.execute('select * from pets where owner=? and ID=? OR name=? AND owner=?', (ID, pet, pet.title(), ID,))
                rows = c.fetchall()
                pet = pet.title()

    c.execute('update pets set hunger=100 WHERE owner=? AND ID=? OR name=? AND owner=?', (ID, pet, pet, ID,))
    
    conn.commit()

    conn.close()

    if len(rows) == 0:
        await ctx.send(ID + ' This is not your pet OR it does not exist :)')

    else:

        await ctx.send(ID + ' You fed your pet!')


@client.command(aliases=['FEEDALL', 'fa', 'FA'])
async def feedall(ctx):

    ID = '<@' + str(ctx.message.author.id) + '>'
    
    conn = sqlite3.connect('gamble.db') # connect to the database

    c = conn.cursor() #Create a cursor to browse the database

    c.execute('update pets set hunger=100 WHERE owner=?',(ID,))

    conn.commit()

    conn.close()

    await ctx.send(ID + ' You fed all your pets!')


@client.command(aliases=['PLAYALL', 'pa', 'PA'])
async def playall(ctx):

    ID = '<@' + str(ctx.message.author.id) + '>'
    
    conn = sqlite3.connect('gamble.db') # connect to the database

    c = conn.cursor() #Create a cursor to browse the database

    c.execute('update pets set mood=100 WHERE owner=?',(ID,))

    conn.commit()

    conn.close()

    await ctx.send(ID + ' You played with all your pets!')
    

@client.command(aliases=['PLAY', 'pl', 'PL'])
async def play(ctx, pet, last=None):

    ID = '<@' + str(ctx.message.author.id) + '>'

    if last != None:

        pet = pet + ' ' + last
    
    conn = sqlite3.connect('gamble.db') # connect to the database

    c = conn.cursor() #Create a cursor to browse the database

    c.execute('select * from pets where owner=? and ID=? OR name=? AND owner=?', (ID, pet, pet, ID,))

    rows = c.fetchall()

    if len(rows) == 0:
        c.execute('select * from pets where owner=? and ID=? OR name=? AND owner=?', (ID, pet, pet.upper(), ID,))
        rows = c.fetchall()
        pet = pet.upper()

        if len(rows) == 0:
            c.execute('select * from pets where owner=? and ID=? OR name=? AND owner=?', (ID, pet, pet.lower(), ID,))
            rows = c.fetchall()
            pet = pet.lower()

            if len(rows) == 0:
                c.execute('select * from pets where owner=? and ID=? OR name=? AND owner=?', (ID, pet, pet.title(), ID,))
                rows = c.fetchall()
                pet = pet.title()
        

    c.execute('update pets set mood=100 WHERE owner=? AND ID=? OR name=? AND owner=?', (ID, pet, pet, ID,))
    
    conn.commit()

    conn.close()

    if len(rows) == 0:
        await ctx.send(ID + ' This is not your pet OR it does not exist :)')

    else:
        await ctx.send(ID + ' You played with your pet and it appreciated you!!')


def checkDatabase():
    
    if path.exists("gamble.db"):
        None #Do nothing

    else:
        #connect to database
        conn = sqlite3.connect('gamble.db')

        # create the cursor
        c = conn.cursor()

        #Create a Table
        c.execute("""CREATE TABLE players (
                    userID text,
                    name text,
                    points text
                    )""")

        conn.commit() # Commit our command

        conn.close() # Close the connection
        

@tasks.loop(seconds=1)
async def hatchTimer():

    await asyncio.sleep(300)

    print('Ding!')

    channel = client.get_channel(857051147226841129)

    conn = sqlite3.connect('gamble.db') # connect to the database

    c = conn.cursor() #Create a cursor to browse the database
    
    c.execute("select * FROM pets WHERE hatch NOT LIKE " + "0")

    rows = c.fetchall()

    if len(rows) > 0:

        for k in rows:
            result = int(k[6]) -50

            if result <= 0:

                result = 0

                c.execute("update pets SET age=? WHERE ID=?", ('360', k[0]))

                await channel.send(k[8] + " Your egg has HATCHED!")

            c.execute("update pets SET hatch=? WHERE ID=?", (str(result), k[0]))
            

    conn.commit() # Commit our command

    conn.close() # Close the connection
        
@tasks.loop(seconds=1)
async def updateGamble(): #This runs in the On Ready Section

    await asyncio.sleep(3600)

    conn = sqlite3.connect('gamble.db') # connect to the database

    c = conn.cursor() #Create a cursor to browse the database

    c.execute("select * FROM players")

    rows = c.fetchall()

    extraPoints = 0 # This is gonna keep track of the extra points be accumulated

    total = 0 #This will be the total amount of points after all calculations

    for row in rows:

        ID = row[0]

        c.execute("select * from pets where owner=?",(ID,))

        rows2 = c.fetchall() # Creates a two dimensional array of the pet table associated to the current player/user

        if len(rows2) == 0:  
            c.execute("UPDATE players SET points=? WHERE userID=?", (str(int(row[2]) + 10), str(ID))) #Updates the points for the current row/user
            continue

        else:

            for row2 in rows2:

                print('yes?')

                if int(row2[3]) >= 80:
                    extraPoints += 2

                if int(row2[4]) <= 50:
                    extraPoints -= 2

            total = int(row[2]) + extraPoints + 10

            extraPoints = 0

            if total < 0:
                total = 0

            c.execute("UPDATE players SET points=? WHERE userID=?", (str(total), str(ID))) #Updates the points for the current row/user
            
            

    conn.commit()

    conn.close()

    print('Update Completed!')
    

'''@tasks.loop(seconds=60)
async def mudaeReminder():

    channel = client.get_channel(843315069705388083)
        
    fmt = '%I:%M'

    ID = '<@' + '200791913945628682' + '>' #Constructs the User's ID to @ them.

    # METHOD 1: Hardcode zones: Converting from UTC to Any Timezone
    to_zone = pytz.timezone('US/Eastern')

    #Get the current time
    utc = datetime.now()

    #Convert the timezone to Eastern
    Eastern = utc.astimezone(to_zone)

    minutes = Eastern.strftime(fmt).split(':')[1]

    if minutes == '58':
        await channel.send(ID + " It's almost time to roll! WAKE UP!")'''

@tasks.loop(seconds=1)
async def decay():
    
    await asyncio.sleep(3600) #3600 seconds Is an hour, which is 60 minutes.

    conn = sqlite3.connect('gamble.db') # connect to the database

    c = conn.cursor() #Create a cursor to browse the database

    c.execute('select * from pets')

    rows = c.fetchall()

    newHunger = 0

    newMood = 0

    newAge = 0

    for k in rows:

        newMood = str(int(k[3]) - 2) #mood

        newHunger = str(int(k[4]) - 2) #hunger

        newAge = str(int(k[7]) + 60) #Age

        if int(newMood) < 0:
            newMood = 0

        if int(newHunger) <0:
            newHunger = 0

        c.execute('update pets set mood=? WHERE ID=?', (newMood, k[0],))

        c.execute('update pets set hunger=? WHERE ID=?', (newHunger,k[0],))

        c.execute('update pets set age=? WHERE ID=?', (newAge,k[0],))

    conn.commit()

    conn.close()

    

@tasks.loop(seconds=60)
async def new():

    server = client.get_guild(428331662343012362)
    members = server.members

    conn = sqlite3.connect('gamble.db') # connect to the database

    c = conn.cursor() #Create a cursor to browse the database

    for k in members:
        if k.bot == False:
            
            ID = '<@' + str(k.id) + '>'
            
            if k.nick != None:
                name = k.nick
            else:
                name = k.name

            c.execute('select * from players WHERE userID=?',(ID,))

            rows = c.fetchall()

            if len(rows) == 0:

                c.execute('insert into players values(?,?,?)', (ID, name, str(60)))

    conn.commit()

    conn.close()


checkDatabase() #Checks to see if there is a database and gets it running.

client.run('ODU0MDkwNjY4NDE4OTI0NTc0.YMe36w.-6TTOuVv3P3HSdBrP2gJxAsCnFM')

