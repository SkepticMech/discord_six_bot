import discord
import random
import os
import pickle
import asyncio
from PIL import Image, ImageDraw, ImageFont, ImageChops

ancientdict = {
}
dict_in = open("ancientdict.pickle", "rb")
ancientdict = pickle.load(dict_in)
def backuprecords():
    dict_out = open("ancientdict.pickle","wb")
    pickle.dump(ancientdict, dict_out)
    dict_out.close()

def get_key(val): 
    for key, value in ancientdict.items(): 
         if val in value: 
             return key 

    return -1

async def user_metrics_background_task():
    await client.wait_until_ready()
    while not client.is_closed():
        try:
            backuprecords()
            await asyncio.sleep(30)
        except Exception as e:
            print(str(e))
            await asyncio.sleep(30)   


prefix = "define"
cmd_prefix = "!"
admin_privliged_role = "Primary User"

client=discord.Client()

@client.event  # event decorator/wrapper
async def on_ready():
    print(f"I have logged in as {client.user}")

@client.event
async def on_message(message): #The main bot functions
    args = {
        "user": message.author,
        "name": message.author.display_name,
        "role": message.author.roles,
		"channel": message.channel,
		"content": message.content,
		"guild": message.guild,
        "userargs" : ""
    }

    if message.author == client.user:
        return
    elif message.content.startswith("!"):
        split_argsl = args["content"][1:].lower().split()
        cmd = split_argsl[0]
        args["userargs"] = cmd
        #Shut down command
        if cmd == "sliset" or cmd == "kill":
            roles = args["role"]
            num_roles = len(roles)
            cntr = 0
            for item in roles:
                allowed_role = str(item)
                cntr  = cntr + 1
                if allowed_role == admin_privliged_role:
                    await client.close()
                elif cntr == num_roles:
                    await message.channel.send("Sorry, only a Primary User can kill me!")
        #create image of text
        elif cmd == "draw":
            split_argsl = args["content"][1:].lower().split()
            if len(split_argsl) == 1:
                split_argsl.append("null")
            split_argst = args["content"][1:].split()
            split_args = " ".join(split_argst[1:])
            drawanc(split_args)
            await message.channel.send(file=discord.File("ancient.png"))
        #translate command
        elif cmd == "tmta" or cmd == "tatm":
            rep = translate(args)
            if rep.x == 1:
                await message.channel.send(file=discord.File("ancient.png"), content = rep.str1)
            elif rep.x == 2:
                await message.channel.send(file=discord.File("ancient.png"), content = rep.str1)
                await message.channel.send(rep.str1)
            else:
                await message.channel.send(rep.str1)
        #add to dictionary command
        elif cmd == "add":
            rep = addword(args)
            if rep.x == 0:
                await message.channel.send(rep.str1)
            elif rep.x == 1:
                await message.channel.send(rep.str1)
                await message.channel.send(rep.str2)
            elif rep.x == 2:
                await message.channel.send(rep.str1)
                await message.channel.send(file=discord.File("ancient.png"), content = rep.str2)
                channel = rep.chn
                await channel.send(rep.str3)
        #modify dictionary command
        elif cmd == "update":
            rep = updatedict(args)
            if rep.x == 0:
                await message.channel.send(rep.str1)
            elif rep.x == 1:
                await message.channel.send(rep.str1)
                await message.channel.send(rep.str2)
            elif rep.x == 2:
                await message.channel.send(rep.str1)
                await message.channel.send(file=discord.File("ancient.png"), content = rep.str2)
                channel = rep.chn
                await channel.send(rep.str3)
        #remove dictionary entry command
        elif cmd == "remove":
            rep = censordict(args)
            if rep.x == 0:
                await message.channel.send(rep.str1)
            elif rep.x == 1:
                await message.channel.send(rep.str1)
                await message.channel.send(rep.str2)
            elif rep.x == 2:
                await message.channel.send(rep.str1)
                await message.channel.send(rep.str2)
                channel = rep.chn
                await channel.send(rep.str3)

        
    elif args["content"].lower().startswith("hey six") or args["content"].lower().startswith("six"):
        rep = six_call(args)
        if rep.str1 != "":
            if rep.x == 1:
                if rep.var == 0:
                    await message.channel.send(file=discord.File("ancient.png"), content = rep.str1)
                else:
                    await message.channel.send(rep.str1)
            elif rep.x == 2:
                await message.channel.send(file=discord.File("ancient.png"), content = rep.str1)
                await message.channel.send(rep.str2)
            elif rep.x == 3:
                await message.channel.send(rep.str1)
                await asyncio.sleep(3)
                await message.channel.send(rep.str2)
                await asyncio.sleep(3)
                await message.channel.send(rep.str3)
            else:
                await message.channel.send(rep.str1)
    elif args["content"].lower().startswith("hey enkei") or args["content"].lower().startswith("enkei"):
       await message.channel.send(enkei_call(args))

def trim(im): #tirms whitespace from image
    bg = Image.new(im.mode, im.size, im.getpixel((0,0)))
    diff = ImageChops.difference(im, bg)
    diff = ImageChops.add(diff, diff, 2.0, -100)
    bbox = diff.getbbox()
    if bbox:
        return im.crop(bbox)

def drawanc(str): #converts string into ancient.png image
	img = Image.new("RGBA", (2000,40), color = (0,0,0, 0))
	fnt = ImageFont.truetype("ancientrunes.ttf", 32)
	d = ImageDraw.Draw(img)
	d.text((0,0), str, font=fnt, fill=(0,0,0))
	imgc = trim(img)
	imgc.save("ancient.png", "PNG")

class transout:
    def __init__(self): 
        self.str1 = ""
        self.str2 = ""
        self.x = 0

class sixoutcl:
    def __init__(self): 
        self.str1 = ""
        self.str2 = ""
        self.str3 = ""
        self.x = 0
        self.var = 0 

class dictoutcl:
    def __init__(self):
        self.chn = 0
        self.str1 = ""
        self.str2 = ""
        self.str3 = ""
        self.x = 0

def translate(args): #function to control translation for shorthand command
    trans = transout()
    split_argsl = args["content"][1:].lower().split()
    split_argst = args["content"][1:].split()
    split_args = " ".join(split_argst[1:])
    cmd = split_argsl[0]
    if split_args != "":
        if cmd == "tmta": #for english
            if split_args in ancientdict:
                drawanc((ancientdict[split_args])[0])
                if (ancientdict[split_args])[1] == "":
                    trans.x = 1
                    trans.str1 ="I believe \"" + split_args + "\" was written..."
                else:
                    trans.x = 1
                    trans.str1 ="I believe \"" + split_args + "\" translates to \"" + (ancientdict[split_args])[1] + "\", and was written..."
            else:
                trans.str1 = "I am sorry mistress, I am afraid I do not know that translation."
        elif cmd == "tatm": #for ancient symbols
            if get_key(split_args) != -1:
                if ancientdict[get_key(split_args)].index(split_args) == 0: #symbols
                    drawanc(split_args)
                    if ancientdict[get_key(split_args)][1] == "":
                        trans.x = 2
                        trans.str1 ="I believe..."
                        trans.str2 = "...translates as \"" + get_key(split_args) + "\"."
                    else:
                        trans.x = 2
                        trans.str1 ="I believe..."
                        trans.str2 = "...or \"" + ancientdict[get_key(split_args)][1] + "\", translates as \"" + get_key(split_args) + "\"."
                else: #words
                    drawanc(ancientdict[get_key(split_args)][0])
                    trans.x = 2
                    trans.str1 ="I believe \"" + split_args + "\", or..."
                    trans.str2 = "...translates as \"" + get_key(split_args) + "\"."
            else:
                trans.str1 = "I am sorry mistress, I am afraid I am not familiar with aspect of the ancient language."
    else:
        trans.str1 = "Mistress, I need to know *what* you want to translate..."
    return trans

def six_call(args): #interaction with Six, both comedic and for translation
    sixout = sixoutcl()
    if args["content"].lower().startswith("hey six"):
        if len(args["content"]) == 7:
            sixout.str1 = "Yes, mistress?"
            cmd = "nul"
            sixout.var = 1
        else:
            split_argsl = args["content"][8:].lower().split()
            split_argst = args["content"][8:].split()
            split_args = " ".join(split_argst[4:])
            cmd = split_argsl[0]
    elif args["content"].lower().startswith("six"):
        if len(args["content"]) == 3:
            sixout.str1 = "Yes, mistress?"
            cmd = "nul"
            sixout.var = 1
        else:
            split_argsl = args["content"][4:].lower().split()
            split_argst = args["content"][4:].split()
            split_args = " ".join(split_argst[4:])
            cmd = split_argsl[0]
    if cmd == "translate":
        if len(split_argsl) < 5:
            if len(split_argsl) > 2:
                if split_argsl[2] in ("word","phrase"):
                    sixout.str1 = "I need to know if that " + split_argsl[2] + " is *modern*, or *ancient*, mistress."
                else:
                    sixout.str1 = "Translate *what*, mistress?"
            else:
                sixout.str1 = "Translate *what*, mistress?"
        else:
            if split_argsl[2] == "modern":
                if split_args in ancientdict:
                    drawanc((ancientdict[split_args])[0])
                    if (ancientdict[split_args])[1] == "":
                        sixout.x = 1
                        sixout.str1 ="I believe \"" + split_args + "\" was written..."
                    else:
                        sixout.x = 1
                        sixout.str1 ="I believe \"" + split_args + "\" translates to \"" + (ancientdict[split_args])[1] + "\", and was written..."
                else:
                    sixout.str1 = "I am sorry mistress, I am afraid I do not know that translation."
            elif split_argsl[2] == "ancient":
                if get_key(split_args) != -1:
                    if ancientdict[get_key(split_args)].index(split_args) == 0: #symbols
                        drawanc(split_args)
                        if ancientdict[get_key(split_args)][1] == "":
                            sixout.x = 2
                            sixout.str1 ="I believe..."
                            sixout.str2 = "...translates as \"" + get_key(split_args) + "\"."
                        else:
                            sixout.x = 2
                            sixout.str1 ="I believe..."
                            sixout.str2 = "...or \"" + ancientdict[get_key(split_args)][1] + "\", translates as \"" + get_key(split_args) + "\"."
                    else: #words
                        drawanc(ancientdict[get_key(split_args)][0])
                        sixout.x = 2
                        sixout.str1 ="I believe \"" + split_args + "\", or..."
                        sixout.str2 = "...translates as \"" + get_key(split_args) + "\"."
                else:
                    sixout.str1 = "I am sorry mistress, I am afraid I am not familiar with that aspect of the ancient language."
    if cmd == "do":
        sixout.var = 1
        if len(split_argsl) < 3:
            sixout.str1 = "Do *what*, mistress?"
        else:
            if len(split_argsl) < 4:
                sixout.str1 = "A scan for *what*, mistress?"
            elif split_argsl[3] != "for":
                sixout.str1 = "A scan *for what*, mistress?"
            elif split_argsl[3] == "for" and len(split_argsl) > 4:
                sixout.x = 3
                focus = " ".join(split_argst[4:])
                sixout.str1 = "Please wait while I scan the area for " + focus + "..."
                sixout.str2 = "..."
                direc = ["north","northwest","northeast","south","southwest","southeast","west","east"]
                findarray = ["...I could not locate any " + focus + " in range, mistress."]*2 + ["...I believe there is " + focus + " to the " + random.choice(direc) + ", mistress."]
                sixout.str3 = random.choice(findarray)
            else:
                sixout.str1 = "A scan for *what*, mistress?"
    return sixout

def enkei_call(args): #purely comedic interaction with Enkei
    insultarray = ["pauper","imbicile","Elborethian rat","child"]
    lc_mess = args["content"].lower()
    if (lc_mess.find("do a scan") != -1):
        reply =  "I am not your slave, " + random.choice(insultarray) + "."
    else:
        reply = "What is it, " + random.choice(insultarray) + "?"
    return reply

def addword(args): #function to enable addtion to dictionary
    dictout = dictoutcl()
    split_argsl = args["content"][1:].lower().split()
    if len(split_argsl) == 1:
        split_argsl.append("null")
    split_argst = args["content"][1:].split()
    if len(split_argst) == 1:
        split_argst.append("")
    if str(args["channel"]) == "archive":
        if "_" in split_argst:
            brk = [i for i, x in enumerate(split_argst) if x == "_"]
            if len(brk) == 2:
                engl = " ".join(split_argst[1:brk[0]])
                anchr = " ".join(split_argst[(brk[0]+1):brk[1]])
                anchs = " ".join(split_argst[(brk[1]+1):])
            elif len(brk) == 1:
                engl = " ".join(split_argst[1:brk[0]])
                anchr = " ".join(split_argst[(brk[0]+1):])
                anchs = ""
            else:
                dictout.str1 = "Invalid format. Please use the form: modern _ ancientrunes _ anchientsounds or simply modern _ ancientrunes if the sound is not known"
            if anchr != "":
                dictout.x = 1
                drawanc(anchr)
                guild = args["guild"]
                dictout.chn = discord.utils.get(guild.text_channels, name='general')
                dictout.str1 = "Checking Submission..."
                if engl in ancientdict:
                    dictout.str2 = "This entry already exists."
                else:
                    dictout.x = 2
                    if len(brk) == 2:
                        dictout.str2 = "Entry Added:\n\"" + anchs + "\", meaning \"" + engl + "\", and written...\n"
                    else:
                        dictout.str2 = "Entry Added:\n\"" + engl + "\", written...\n"
                    dictout.str3 = "New dictionary submission from " + args["name"]
                    ancientdict[engl] = [anchr,anchs]
            else:
                dictout.str1 = "Invalid format. Please provide the translation"
        else:
            dictout.str1 = "Invalid format, please check your spacing"
    else:
        dictout.str1 = "Dictionary submissions are only accepted in the archive channel."
    return dictout

def updatedict(args): #function to edit a dictionary entry
    dictout = dictoutcl()
    split_argsl = args["content"][1:].lower().split()
    if len(split_argsl) == 1:
        split_argsl.append("null")
    split_argst = args["content"][1:].split()
    if len(split_argst) == 1:
        split_argst.append("")
    if str(args["channel"]) == "archive":
        if "_" in split_argst:
            brk = [i for i, x in enumerate(split_argst) if x == "_"]
            if len(brk) == 2:
                engl = " ".join(split_argst[1:brk[0]])
                anchr = " ".join(split_argst[(brk[0]+1):brk[1]])
                anchs = " ".join(split_argst[(brk[1]+1):])
            elif len(brk) == 1:
                engl = " ".join(split_argst[1:brk[0]])
                anchr = " ".join(split_argst[(brk[0]+1):])
                anchs = ""
            else:
                dictout.str1 = "Invalid format. Please use the form: modern _ ancientrunes _ anchientsounds or simply modern _ ancientrunes if the sound is not known"
            if anchr != "":
                dictout.x = 1
                drawanc(anchr)
                guild = args["guild"]
                dictout.chn = discord.utils.get(guild.text_channels, name='general')
                dictout.str1 = "Checking Modification..."
                if engl not in ancientdict:
                    dictout.str2 = "This entry does not yet exist."
                else:
                    dictout.x = 2
                    if len(brk) == 2:
                        dictout.str2 = "Entry Changed:\n\"" + anchs + "\", meaning \"" + engl + "\", and written...\n"
                    else:
                        dictout.str2 = "Entry Changed:\n\"" + engl + "\", written...\n"
                    dictout.str3 = "New translation update by " + args["name"]
                    ancientdict[engl] = [anchr,anchs]
            else:
                dictout.str1 = "Invalid format. Please provide the translation"
        else:
            dictout.str1 = "Invalid format, please check your spacing"
    else:
        dictout.str1 = "Translation updates are only accepted in the archive channel."
    return dictout

def censordict(args): #function to remove a dictionary entry
    dictout = dictoutcl()
    split_argsl = args["content"][1:].lower().split()
    if len(split_argsl) == 1:
        split_argsl.append("null")
    split_argst = args["content"][1:].split()
    if len(split_argst) == 1:
        split_argst.append("")
    if str(args["channel"]) == "archive":
        engl = " ".join(split_argst[1:])
        print(engl)
        if engl == "":
            dictout.str1 = "Invalid format. Please provide the entry to be removed."
        else:
            dictout.x = 1
            guild = args["guild"]
            dictout.chn = discord.utils.get(guild.text_channels, name='general')
            dictout.str1 = "Checking Deletion..."
            if engl not in ancientdict:
                dictout.str2 = "This entry does not yet exist."
            else:
                dictout.x = 2
                dictout.str2 = "Entry Removed:\n\"" + engl + "\""
                dictout.str3 = "Dictionary entry removed by " + args["name"]
                ancientdict.pop(engl)
    else:
        dictout.str1 = "Translation removal is allowed in the archive channel."
    return dictout





# client.loop.create_task(user_metrics_background_task())
client.run("NTY5Mzk4OTE0NjQ2NTQwMzIz.XLwEhQ.Dw8US4osHL5FPSf6PN6YYoovGvs") #SHOP
# client.run("NTY5MzgxOTk4NDMxNTY3ODcy.XLv0fA.U6UVquCagOzgl4eXkwi5cB05YMU") #LANG CLUB