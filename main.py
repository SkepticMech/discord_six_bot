import discord, random, pickle, asyncio, csv, time, atexit, requests, re
from PIL import Image, ImageDraw, ImageFont, ImageChops
from apscheduler.schedulers.background import BackgroundScheduler

ancientdict = {
}
dict_in = open("ancientdict.pickle", "rb")
ancientdict = pickle.load(dict_in)

memo = {
    "nul" : [""]
}

memo_in = open("memos.pickle", "rb")
memo = pickle.load(memo_in)

scores = {
    "nul" : [0,0,0]
}

score_in = open("scores.pickle", "rb")
scores = pickle.load(score_in)


admin_privliged_role = "Primary User"
role1 = "Archivist"
role2 = "Scribe"
role3 = "Explorer"

rank1 = 0
rank2 = 0
rank3 = 0

scorelims = [100,100,100]

client=discord.Client()

@client.event  # event decorator/wrapper
async def on_ready():
    global role1, role2, role3
    global rank1, rank2, rank3
    print(f"I have logged in as {client.user}")
    thisguild = client.guilds[0]
    allroles = thisguild.roles
    for item in allroles:
        if item.name == role1:
            rank1 = item
        elif item.name == role2:
            rank2 = item
        elif item.name == role3:
            rank3 = item

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
                cntr  += 1
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
            await change_roles(args,updatescore(args, scoregroup(trn = 1)))
        elif cmd == "draww":
            split_argsl = args["content"][1:].lower().split()
            if len(split_argsl) == 1:
                split_argsl.append("null")
            split_argst = args["content"][1:].split()
            split_args = " ".join(split_argst[1:])
            drawanc(split_args, 1)
            await message.channel.send(file=discord.File("ancient.png"))
            await change_roles(args,updatescore(args, scoregroup(trn = 1)))
        #translate command
        elif cmd in ["tmta","tatm","tmtaw","tatmw","tatmf","tatmfw"]:
            wht = 0
            if cmd == "tmtaw" or cmd == "tatmw" or cmd == "tatmfw":
                wht = 1
            rep = translate(args, wht)
            if rep.x == 1:
                await message.channel.send(file=discord.File("ancient.png"), content = rep.str1)
            elif rep.x == 2:
                await message.channel.send(file=discord.File("ancient.png"), content = rep.str1)
                await message.channel.send(rep.str2)
            else:
                await message.channel.send(rep.str1)
            await change_roles(args,updatescore(args, scoregroup(trn = 1)))
        #add to dictionary command
        elif cmd == "add":
            rep = addword(args)
            if rep.x == 0:
                await message.channel.send(rep.str1)
            elif rep.x == 1:
                await message.channel.send(file=discord.File("ancient.png"), content = rep.str1)
                await change_roles(args,updatescore(args, scoregroup(dic = 5)))
        #modify dictionary command
        elif cmd == "update":
            rep = updatedict(args)
            if rep.x == 0:
                await message.channel.send(rep.str1)
            elif rep.x == 1:
                await message.channel.send(file=discord.File("ancient.png"), content = rep.str1)
                await change_roles(args,updatescore(args, scoregroup(dic = 2)))
        #remove dictionary entry command
        elif cmd == "remove":
            rep = censordict(args)
            if rep.x == 0:
                await message.channel.send(rep.str1)
            elif rep.x == 1:
                await message.channel.send(file=discord.File("ancient.png"), content = rep.str1)
        elif cmd == "export":
            if str(args["channel"]) == "archive":
                csvexp(1)
                await message.channel.send(file=discord.File("Ancient_Dictionary.csv"))
                await message.channel.send(file=discord.File("AD_for_import.csv"))
            else:
                await message.channel.send("The dictionary may only be retrieved from the Archive.")
        elif cmd == "import":
            if str(args["channel"]) == "archive":
                impnew = impdata()
                if message.attachments:
                    impnew.ata = 1
                    impnew.refloc = message.attachments[0].url
                if args["content"].lower().endswith("all"):
                    impnew.repl = 1
                impnew = csvimp(impnew)
                await message.channel.send(impnew.str1)
                if impnew.ata == 1 and impnew.err == 0:
                    await change_roles(args,updatescore(args, scoregroup(dic = 50)))
            else:
                await message.channel.send("Dictionary encoding may only be performed in the Archive.") 
        elif cmd == "roll":
            result = diceroll(args["content"])
            if result != "error":
                await message.channel.send(result)
                await change_roles(args,updatescore(args, scoregroup(egg = 1)))
            else:
                await message.channel.send("I am sorry mistress, I do not recognize the format of your request.")
        elif cmd == "fireball":
            await message.channel.send(diceroll("roll 8d6") + " fire damage")
            await change_roles(args,updatescore(args, scoregroup(egg = 1)))
    #Six and Enkei Interaction informal commands 
    elif args["content"].lower().startswith(("hey six","hey, six","six")):
        rep = six_call(args)
        if rep.str1 != "":
            if rep.x == 1:
                if rep.var == 0:
                    await message.channel.send(file=discord.File("ancient.png"), content = rep.str1)
                    await change_roles(args,updatescore(args, scoregroup(trn = 1)))
                else:
                    await message.channel.send(rep.str1)
            elif rep.x == 2:
                await message.channel.send(file=discord.File("ancient.png"), content = rep.str1)
                await message.channel.send(rep.str2)
                await change_roles(args,updatescore(args, scoregroup(trn = 1)))
            elif rep.x == 3:
                await message.channel.send(rep.str1)
                await asyncio.sleep(3)
                await message.channel.send(rep.str2)
                await asyncio.sleep(3)
                await message.channel.send(rep.str3)
                await change_roles(args,updatescore(args, scoregroup(egg = 2)))
            elif rep.x == 4:
                await message.channel.send(rep.str1)
                await asyncio.sleep(2)
                await message.channel.send("Vaulting In:")
                await asyncio.sleep(2)
                await message.channel.send("3")
                await asyncio.sleep(1)
                await message.channel.send("2")
                await asyncio.sleep(1)
                await message.channel.send("1")
                await asyncio.sleep(1)
                await message.channel.send("Vaulting...")
                await asyncio.sleep(3)
                await message.channel.send("Error: Insufficient Power")
                await change_roles(args,updatescore(args, scoregroup(egg = 5)))
            else:
                await message.channel.send(rep.str1)
    elif args["content"].lower().startswith(("hey enkei","enkei")):
       await message.channel.send(enkei_call(args))
       await change_roles(args,updatescore(args, scoregroup(egg = 1)))

async def change_roles(args, chngs):
    whois = args["user"]
    if chngs.rem == 0:
        await whois.add_roles(chngs.id1)
    if chngs.rem == 1:
        await whois.add_roles(chngs.id1)
        await whois.remove_roles(chngs.id2)

# Assorted Class Deffinitions, largely single use
class impdata:
    def __init__(self):
        self.ata = 0
        self.refloc = ""
        self.repl = 0
        self.str1 = "no message"
        self.str2 = ""
        self.x = 0
        self.err = 0

class getkey:
    def __init__(self):
        self.key = -1
        self.mlt = 0

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

class scoregroup():
    def __init__(self, dic = 0, trn = 0, egg = 0):
        self.dics = dic
        self.trns = trn
        self.eggs = egg

class rankchange():
    def __init__(self, rolist, rems):
        self.id1 = 0
        self.id2 = 0
        self.fin = 0
        self.rem = rems
        self.roles = rolist
        self.num_roles = len(rolist)

# Minor repeated use functions
def backuprecords(): #export dictionary to pickle backup file
    dict_out = open("ancientdict.pickle","wb")
    pickle.dump(ancientdict, dict_out)
    dict_out.close()

def backupmemos(): #export dictionary to pickle backup file
    memo_out = open("memos.pickle","wb")
    pickle.dump(memo, memo_out)
    memo_out.close()

def backupscores(): #export dictionary to pickle backup file
    score_out = open("scores.pickle","wb")
    pickle.dump(scores, score_out)
    score_out.close()

def updatescore(args, points):
    global scores
    rnkchg = rankchange(args["role"], 2)
    uname = str(args["user"])
    if uname in scores:
        scores[uname] = [x + y for x, y in zip(scores[uname],[points.dics,points.trns,points.eggs])]
    else:
        scores[uname] = [points.dics,points.trns,points.eggs]
    backupscores()
    if scores[uname][0] >= scorelims[0]:
        curroles = args["role"]
        num_roles = len(curroles)
        cntr = 0
        rnkchg.fin = 0
        for item in curroles:
            curole  = str(item)
            cntr += 1
            if rnkchg.fin == 0:
                if curole == role1:
                    rnkchg.fin = 1
                elif cntr == num_roles:
                    rnkchg.id1 = rank1
                    rnkchg.rem = 0
    if scores[uname][1] >= scorelims[1]:
        curroles = args["role"]
        num_roles = len(curroles)
        cntr = 0
        rnkchg.fin = 0
        for item in curroles:
            curole  = str(item)
            cntr += 1
            if rnkchg.fin == 0:
                if curole == role2:
                    rnkchg.fin = 1
                elif cntr == num_roles:
                    rnkchg.id1 = rank2
                    rnkchg.rem = 0
    if scores[uname][2] >= scorelims[2]:
        curroles = args["role"]
        num_roles = len(curroles)
        cntr = 0
        rnkchg.fin = 0
        for item in curroles:
            curole  = str(item)
            cntr += 1
            if rnkchg.fin == 0:
                if curole == role3:
                    rnkchg.fin = 1
                elif cntr == num_roles:
                    rnkchg.id1 = rank3
                    rnkchg.rem = 0
    return rnkchg

def csvexp(all = 0):
    holder = []
    for word in ancientdict.keys():
        holder.append({"Modern Word" : word, "Ancient Script" : (ancientdict[word])[0], "Ancient Word" : (ancientdict[word])[1]})
    csv_columns = ["Modern Word","Ancient Script", "Ancient Word"]
    try:
        with open("AD_for_import.csv", 'w', newline='') as csvfile:
            writer = csv.DictWriter(csvfile, fieldnames=csv_columns, delimiter="|", quotechar="'")
            writer.writeheader()
            writer.writerows(holder)
    except IOError:
        print("I/O error")
    if all == 1:
        try:
            with open("Ancient_Dictionary.csv", 'w', newline='') as csvfile:
                writer = csv.DictWriter(csvfile, fieldnames=csv_columns)
                writer.writeheader()
                writer.writerows(holder)
        except IOError:
            print("I/O error")

def csvimp(impdat):
    # print([impdat.ata,impdat.refloc,impdat.repl])
    global ancientdict
    if impdat.ata == 1:
        if impdat.refloc.endswith(".csv"):
            errchk = 0
            try:
                tempfile = requests.get(impdat.refloc)
                with open("temp.csv", "wb") as f:
                    f.write(tempfile.content)
                try:
                    tmpdict = {}
                    with open("temp.csv", "r", newline="") as tmpfile:
                        reader = csv.reader(tmpfile, delimiter=',')
                        hdrs = next(reader)
                        reader2 = csv.DictReader(tmpfile, delimiter=",")
                        if len(hdrs) == 2 or len(hdrs) == 3:
                            tmpfile.seek(0)
                            for row in reader2:
                                if len(hdrs) == 3:
                                    tmpdict[row[hdrs[0]]]=[row[hdrs[1]], row[hdrs[2]]]
                                else:
                                    tmpdict[row[hdrs[0]]]=[row[hdrs[1]], ""]
                        else:
                            errchk = 1
                            impdat.str1 = "Format Error: " + str(len(hdrs)) + " columns in file"
                            impdat.err = 1
                except:
                    impdat.str1 = "File Import Error"
                    impdat.err = 1
            except:
                impdat.str1 = "File Download Error"
                impdat.err = 1
            if errchk == 0:
                if impdat.repl == 1:
                    for key in tmpdict:
                        ancientdict[key] = [(tmpdict[key])[0],(tmpdict[key])[1]]
                    impdat.str1 = "Import Complete: " + str(len(tmpdict)) + " records added or updated."
                else:
                    cnt = 0
                    for key in tmpdict:
                        if key not in ancientdict:
                            cnt = cnt + 1
                            ancientdict[key] = [(tmpdict[key])[0],(tmpdict[key])[1]]
                    impdat.str1 = "Import Complete: " + str(cnt) + " records added."
        else:
            impdat.str1 = "Invalid file type detected. Please use a .csv file"
            impdat.err = 1
    else:
        ancientdict = None
        ancientdict = {}
        try:
            with open("AD_for_import.csv", "r", newline="") as csvfile:
                reader = csv.DictReader(csvfile, delimiter="|", quotechar="'")
                for row in reader:
                    ancientdict[row["Modern Word"]]=[row["Ancient Script"], row["Ancient Word"]]
            impdat.str1 = "Full Import Complete"
        except IOError:
            print("I/O error")
    backuprecords()
    return impdat

def get_key(val): #find key in dictionary from one of the values in its list\
    rkey = getkey()
    for key, value in ancientdict.items(): 
        if val in value:
            if rkey.key != -1:
                rkey.mlt = 1
                return rkey
            rkey.key = key
    return rkey

def get_keys(val): #find key in dictionary from one of the values in its list
    kys = []
    for key, value in ancientdict.items(): 
        if val in value: 
            kys.append(key)
    rkys = "[" + ", ".join(kys) + "]"
    return rkys

def trim(im): #tirms whitespace from image
    bg = Image.new(im.mode, im.size, im.getpixel((0,0)))
    diff = ImageChops.difference(im, bg)
    diff = ImageChops.add(diff, diff, 2.0, -100)
    bbox = diff.getbbox()
    if bbox:
        return im.crop(bbox)

def drawanc(str, wht = 0): #converts string into ancient.png image
    if wht == 0:
        pxc = 0
    else:
        pxc = 255
    img = Image.new("RGBA", (2000,40), color = (pxc,pxc,pxc,0))
    fnt = ImageFont.truetype("ancientrunes.ttf", 32)
    d = ImageDraw.Draw(img)
    d.text((0,0), str, font=fnt, fill=(pxc,pxc,pxc))
    imgc = trim(img)
    imgc.save("ancient.png", "PNG")

def exctm(wrd):
    nwst = wrd
    if wrd.endswith((".",",",";",":","?","!",'"',"'")):
        nwst = wrd[:-1]
    if nwst == "i":
        rtn = "I"
    else:
        rtn = nwst
    return rtn

def plrs(wrd):
    tmp = wrd
    if wrd.endswith("ies"):
        wrd = wrd[:-3] + "y"
        if wrd in ancientdict:
            return wrd
        else:
            wrd =tmp
    if wrd.endswith("es"):
        wrd = wrd[:-2]
        if wrd in ancientdict:
            return wrd
        else:
            wrd =tmp
        wrd = wrd[:-2] + "is"
        if wrd in ancientdict:
            return wrd
        else:
            wrd =tmp
        wrd = wrd[:-3]
        if wrd in ancientdict:
            return wrd
        else:
            wrd =tmp
    if wrd.endswith("ves"):
        wrd = wrd[:-3] + "f"
        if wrd in ancientdict:
            return wrd
        else:
            wrd =tmp
        wrd = wrd[:-3] + "fe"
        if wrd in ancientdict:
            return wrd
        else:
            wrd =tmp
    if wrd.endswith("i"):
        wrd = wrd[:-1] + "us"
        if wrd in ancientdict:
            return wrd
        else:
            wrd =tmp
    if wrd.endswith("s"):
        wrd = wrd[:-1]
        if wrd.endswith("s"):
            wrd = tmp
        if wrd in ancientdict:
            return wrd
        else:
            wrd =tmp
    return wrd

def mfix(wrd):
    if wrd == "i":
        wrd = "I"
    return wrd

def excta(wrd):
    nwst = wrd
    if wrd.endswith((".",",",";",":","?","!",'"',"'")):
        nwst = wrd[:-1]
    rtn = nwst
    return rtn

def diceroll(strg):
    try:
        splitl = strg.lower().split()
        chnks = re.split("d", splitl[1])
        sides = int(chnks[1].split(".")[0])
        dice = int(chnks[0].split(".")[0])
        roll = 0
        fail = 0
        crit = 0
        for j in range(dice):
            roll += random.randint(1,sides)
            if dice == 1 and sides == 20:
                if roll == 1:
                    fail = 1
                elif roll == 20:
                    crit = 1
        if len(splitl) == 3:
            roll += int(splitl[2].split(".")[0])
    except:
        return "error"
    if fail == 1:
        fails = ["drop your weapon.","go blind for 1 hour.","lose 12 hp.","trip and fall prone.","have been pwned by a grue.","alert the guards."]
        strng = "You have critically failed mistress; you " + random.choice(fails)
    elif crit == 1:
        crits = ["deal double damage.","trip your opponent.","suddenly feel as though you are paralized and a group of nerdy giants is looming over you.","seduce the dragon.","catch the arrow.","identify the gazebo."]
        strng = "A critical success mistress; you " + random.choice(crits)
    else:
        strng = str(roll)
    return strng

# Major User command functions
def translate(args, wht = 0): #function to control translation for shorthand command
    trans = transout()
    split_argsl = args["content"][1:].lower().split()
    split_argst = args["content"][1:].split()
    split_args = " ".join(split_argst[1:])
    cmd = split_argsl[0]
    if split_args != "":
        if cmd == "tmta" or cmd == "tmtaw": #for english
            if len(split_argsl) > 2:
                words = split_argsl[1:]
                awords = []
                full = 1
                nope = 1
                missing = []
                for item in words:
                    item = exctm(item)
                    drops = 0
                    if item in ["the","a","an","to"]:
                        drops = 1
                    if item in ancientdict:
                        awords.append((ancientdict[item])[0])
                        nope = 0
                    elif plrs(item) in ancientdict:
                        awords.append((ancientdict[plrs(item)])[0])
                        nope = 0
                    elif drops == 0:
                        full = 0
                        awords.append(item.upper())
                        missing.append(item)
                aphrase = " ".join(awords)
                if not aphrase:
                    aphrase = "EMPTY"
                if missing:
                    if len(missing) > 2:
                        misswrds = ", ".join(missing[:-1]) + ", and " + missing[-1]
                    elif len(missing) == 2:
                        misswrds = ", and ".join(missing)
                    else:
                        misswrds = missing[0]
                drawanc(aphrase, wht)
                trans.x = 1
                if full == 1:
                    trans.str1 = "I believe \"" + split_args + "\" was written..."
                else:
                    if nope == 1:
                        trans.x = 0
                        trans.str1 = "I am sorry mistress, I am not familiar with any of those words. Are you sure you intended to enter \"" + split_args + "\"?"
                    elif len(missing) != 1:
                        trans.str1 = "My records are missing the following " + str(len(missing)) + " words; " + misswrds + ". However, I believe the remainder was written..."
                    else:
                        trans.str1 = "My records are missing the following word; " + misswrds + ". However, I believe the remainder was written..."
            else:
                split_args = mfix(split_args.lower())
                if split_args in ancientdict:
                    drawanc((ancientdict[split_args])[0], wht)
                    if (ancientdict[split_args])[1] == "":
                        trans.x = 1
                        trans.str1 ="I believe \"" + split_args + "\" was written..."
                    else:
                        trans.x = 1
                        trans.str1 ="I believe \"" + split_args + "\" translates to \"" + (ancientdict[split_args])[1] + "\", and was written..."
                elif plrs(split_args) in ancientdict:
                    drawanc((ancientdict[plrs(split_args)])[0], wht)
                    if (ancientdict[plrs(split_args)])[1] == "":
                        trans.x = 1
                        trans.str1 ="I believe \"" + split_args + "\" was written..."
                    else:
                        trans.x = 1
                        trans.str1 ="I believe \"" + split_args + "\" translates to \"" + (ancientdict[plrs(split_args)])[1] + "\", and was written..."
                else:
                    trans.str1 = "I am sorry mistress, I am afraid I do not know that translation."
        elif cmd == "tatm" or cmd == "tatmw": #for ancient symbols
            if len(split_argst) > 2:
                words = split_argst[1:]
                mwords = []
                full = 1
                nope = 1
                glys = 1
                missing = []
                for item in words:
                    if get_key(item).key != -1:
                        mwords.append(get_key(item).key)
                        nope = 0
                        if ancientdict[get_key(item).key].index(item) == 1:
                            glys = 0
                    elif get_key(excta(item)).key != -1:
                        if ancientdict[get_key(excta(item)).key].index(excta(item)) == 1:
                            nope = 0
                            glys = 0
                            mwords.append(get_key(excta(item)).key)
                    else:
                        full = 0
                        mwords.append(item)
                        missing.append(item)
                mphrase = " ".join(mwords)
                if missing:
                    if len(missing) > 1:
                        misswrds = ", ".join(missing[:-1]) + ", and " + missing[-1]
                    elif len(missing) == 2:
                        misswrds = ", and ".join(missing)
                    else:
                        misswrds = missing[0]
                    missdraw = " ".join(missing)
                if glys == 1:
                    trans.x = 1
                    if full == 1:
                        drawanc(split_args, wht)
                        trans.str1 = "I believe \"" + mphrase + "\" is the modern form of..."
                    else:
                        drawanc(missdraw, wht)
                        if nope == 1:
                            drawanc(split_args, wht)
                            trans.str1 = "I am sorry mistress, I am not familiar with any of those words. Please be sure you intended to enter..."
                        elif len(missing) != 1:
                            trans.str1 = "I was able to translate some of the phrase as; \"" + mphrase + "\". However, I have no records for the following " + str(len(missing)) + " words..."
                        else:
                            trans.str1 = "I was able to translate some of the phrase as; \"" + mphrase + "\". However, I have no record for..."
                else:
                    if full == 1:
                        trans.str1 = "I believe the modern form of \"" + split_args + "\" is \"" + mphrase + "\"."
                    else:
                        if nope == 1:
                            trans.str1 = "I am sorry mistress, I am not familiar with any of those word. Are you sure you intended to enter \"" + split_args + "\"?"
                        elif len(missing) != 1:
                            trans.str1  = "My records are missing the following " + str(len(missing)) + " words; " + misswrds + ". However, I believe the remainder translates as \"" + mphrase + "\"."
                        else:
                            trans.str1  = "I have no record of \"" + misswrds + "\". However, I believe the remainer translates as \"" + mphrase + "\"."
            else:
                if get_key(split_args).key != -1:
                    if ancientdict[get_key(split_args).key].index(split_args) == 0: #symbols
                        drawanc(split_args, wht)
                        if ancientdict[get_key(split_args).key][1] == "":
                            trans.x = 2
                            trans.str1 ="I believe..."
                            trans.str2 = "...translates as \"" + get_key(split_args).key + "\"."
                        else:
                            trans.x = 2
                            trans.str1 ="I believe..."
                            trans.str2 = "...or \"" + ancientdict[get_key(split_args).key][1] + "\", translates as \"" + get_key(split_args) + "\"."
                    else: #words
                        drawanc(ancientdict[get_key(split_args).key][0], wht)
                        trans.x = 2
                        trans.str1 ="I believe \"" + split_args + "\", or..."
                        trans.str2 = "...translates as \"" + get_key(split_args).key + "\"."
                else:
                    trans.str1 = "I am sorry mistress, I am afraid I am not familiar with aspect of the ancient language."
        elif cmd == "tatmf" or cmd == "tatmfw": #for ancient symbols
            if len(split_argst) > 2:
                words = split_argst[1:]
                mwords = []
                full = 1
                nope = 1
                glys = 1
                missing = []
                for item in words:
                    if get_key(item).key != -1:
                        if get_key(item).mlt == 0:
                            mwords.append(get_key(item).key)
                            nope = 0
                            if ancientdict[get_key(item).key].index(item) == 1:
                                glys = 0
                        else:
                            tkeys = get_keys(item)
                            mwords.append(tkeys)
                    elif get_key(excta(item)).key != -1:
                        if ancientdict[get_key(excta(item)).key].index(excta(item)) == 1:
                            if get_key(excta(item)).mlt == 0:
                                nope = 0
                                glys = 0
                                mwords.append(get_key(excta(item)).key)
                            else:
                                nope = 0
                                glys = 0
                                tkeys = get_keys(excta(item))
                                mwords.append(tkeys)
                    else:
                        full = 0
                        mwords.append(item)
                        missing.append(item)
                mphrase = " ".join(mwords)
                if missing:
                    if len(missing) > 1:
                        misswrds = ", ".join(missing[:-1]) + ", and " + missing[-1]
                    elif len(missing) == 2:
                        misswrds = ", and ".join(missing)
                    else:
                        misswrds = missing[0]
                    missdraw = " ".join(missing)
                if glys == 1:
                    trans.x = 1
                    if full == 1:
                        drawanc(split_args, wht)
                        trans.str1 = "I believe \"" + mphrase + "\" is the modern form of..."
                    else:
                        drawanc(missdraw, wht)
                        if nope == 1:
                            trans.str1 = "I am sorry mistress, I am not familiar with any of those words. Please be sure you intended to enter..."
                        elif len(missing) != 1:
                            trans.str1 = "I was able to translate some of the phrase as; \"" + mphrase + "\". However, I have no records for the following " + str(len(missing)) + " words..."
                        else:
                            trans.str1 = "I was able to translate some of the phrase as; \"" + mphrase + "\". However, I have no record for..."
                else:
                    if full == 1:
                        trans.str1 = "I believe the modern form of \"" + split_args + "\" is \"" + mphrase + "\"."
                    else:
                        if nope == 1:
                            trans.str1 = "I am sorry mistress, I am not familiar with any of those word. Are you sure you intended to enter \"" + split_args + "\"?"
                        elif len(missing) != 1:
                            trans.str1  = "My records are missing the following " + str(len(missing)) + " words; " + misswrds + ". However, I believe the remainder translates as \"" + mphrase + "\"."
                        else:
                            trans.str1  = "I have no record of \"" + misswrds + "\". However, I believe the remainer translates as \"" + mphrase + "\"."
            else:
                if get_key(split_args).key != -1:
                    if get_key(split_args).mlt == 0:
                        if ancientdict[get_key(split_args).key].index(split_args) == 0: #symbols
                            drawanc(split_args, wht)
                            if ancientdict[get_key(split_args).key][1] == "":
                                trans.x = 2
                                trans.str1 ="I believe..."
                                trans.str2 = "...translates as \"" + get_key(split_args).key + "\"."
                            else:
                                trans.x = 2
                                trans.str1 ="I believe..."
                                trans.str2 = "...or \"" + ancientdict[get_key(split_args).key][1] + "\", translates as \"" + get_key(split_args) + "\"."
                        else: #words
                            drawanc(ancientdict[get_key(split_args).key][0], wht)
                            trans.x = 2
                            trans.str1 ="I believe \"" + split_args + "\", or..."
                            trans.str2 = "...translates as \"" + get_key(split_args).key + "\"."
                    else:
                        tkeys = get_keys(split_args)
                        if ancientdict[get_key(split_args).key].index(split_args) == 0: #symbols
                            drawanc(split_args, wht)
                            if ancientdict[get_key(split_args).key][1] == "":
                                trans.x = 2
                                trans.str1 ="I believe..."
                                trans.str2 = "...translates as \"" + tkeys + "\"."
                            else:
                                trans.x = 2
                                trans.str1 ="I believe..."
                                trans.str2 = "...or \"" + ancientdict[get_key(split_args).key][1] + "\", translates as \"" + tkeys + "\"."
                        else: #words
                            drawanc(ancientdict[get_key(split_args).key][0], wht)
                            trans.x = 2
                            trans.str1 ="I believe \"" + split_args + "\", or..."
                            trans.str2 = "...translates as \"" + tkeys + "\"."
                else:
                    trans.str1 = "I am sorry mistress, I am afraid I am not familiar with aspect of the ancient language."
    else:
        trans.str1 = "Mistress, I need to know *what* you want to translate..."
    return trans

def six_call(args): #interaction with Six, both comedic and for translation
    global memo
    uname = str(args["user"])
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
    elif args["content"].lower().startswith("hey, six"):
        if len(args["content"]) == 8:
            sixout.str1 = "Yes, mistress?"
            cmd = "nul"
            sixout.var = 1
        else:
            split_argsl = args["content"][9:].lower().split()
            split_argst = args["content"][9:].split()
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
                    sixout.str1 = "Is that a *word*, or a *phrase*, mistress?"
            else:
                sixout.str1 = "Translate *what*, mistress?"
        else:
            if split_argsl[2] == "modern":
                if split_argsl[3] == "phrase":
                    words = split_argsl[4:]
                    awords = []
                    full = 1
                    nope = 1
                    missing = []
                    for item in words:
                        item = exctm(item)
                        drops = 0
                        if item in ["the","a","an","to"]:
                            drops = 1
                        if item in ancientdict:
                            awords.append((ancientdict[item])[0])
                            nope = 0
                        elif plrs(item) in ancientdict:
                            awords.append((ancientdict[plrs(item)])[0])
                            nope = 0
                        elif drops == 0:
                            full = 0
                            awords.append(item.upper())
                            missing.append(item)
                    aphrase = " ".join(awords)
                    if not aphrase:
                        aphrase = "EMPTY"
                    if missing:
                        if len(missing) > 2:
                            misswrds = ", ".join(missing[:-1]) + ", and " + missing[-1]
                        elif len(missing) == 2:
                            misswrds = ", and ".join(missing)
                        else:
                            misswrds = missing[0]
                    drawanc(aphrase)
                    sixout.x = 1
                    if full == 1:
                        sixout.str1 = "I believe \"" + split_args + "\" was written..."
                    else:
                        if nope == 1:
                            sixout.x = 0
                            sixout.str1 = "I am sorry mistress, I am not familiar with any of those words. Are you sure you intended to enter \"" + split_args + "\"?"
                        elif len(missing) != 1:
                            sixout.str1 = "My records are missing the following " + str(len(missing)) + " words; " + misswrds + ". However, I believe the remainder was written..."
                        else:
                            sixout.str1 = "My records are missing the following word; " + misswrds + ". However, I believe the remainder was written..."
                else:
                    if split_args in ancientdict:
                        drawanc((ancientdict[split_args])[0])
                        if (ancientdict[split_args])[1] == "":
                            sixout.x = 1
                            sixout.str1 ="I believe \"" + split_args + "\" was written..."
                        else:
                            sixout.x = 1
                            sixout.str1 ="I believe \"" + split_args + "\" translates to \"" + (ancientdict[split_args])[1] + "\", and was written..."
                    elif plrs(split_args) in ancientdict:
                        drawanc((ancientdict[plrs(split_args)])[0])
                        if (ancientdict[plrs(split_args)])[1] == "":
                            sixout.x = 1
                            sixout.str1 ="I believe \"" + split_args + "\" was written..."
                        else:
                            sixout.x = 1
                            sixout.str1 ="I believe \"" + split_args + "\" translates to \"" + (ancientdict[plrs(split_args)])[1] + "\", and was written..."
                    else:
                        sixout.str1 = "I am sorry mistress, I am afraid I do not know that translation."
            elif split_argsl[2] == "ancient":
                if split_argsl[3] == "phrase":
                    words = split_argsl[4:]
                    mwords = []
                    full = 1
                    nope = 1
                    glys = 1
                    missing = []
                    for item in words:
                        if get_key(item).key != -1:
                            mwords.append(get_key(item).key)
                            nope = 0
                            if ancientdict[get_key(item).key].index(item) == 1:
                                glys = 0
                        elif get_key(excta(item)).key != -1:
                            if ancientdict[get_key(excta(item)).key].index(excta(item)) == 1:
                                nope = 0
                                glys = 0
                                mwords.append(get_key(excta(item)).key)
                        else:
                            full = 0
                            mwords.append(item)
                            missing.append(item)
                    mphrase = " ".join(mwords)
                    if missing:
                        if len(missing) > 1:
                            misswrds = ", ".join(missing[:-1]) + ", and " + missing[-1]
                        elif len(missing) == 2:
                            misswrds = ", and ".join(missing)
                        else:
                            misswrds = missing[0]
                        missdraw = " ".join(missing)
                    if glys == 1:
                        sixout.x = 1
                        if full == 1:
                            drawanc(split_args)
                            sixout.str1 = "I believe \"" + mphrase + "\" is the modern form of..."
                        else:
                            drawanc(missdraw)
                            if nope == 1:
                                sixout.str1 = "I am sorry mistress, I am not familiar with any of those words. Please be sure you intended to enter..."
                            elif len(missing) != 1:
                                sixout.str1 = "I was able to translate some of the phrase as; \"" + mphrase + "\". However, I have no records for the following " + str(len(missing)) + " words..."
                            else:
                                sixout.str1 = "I was able to translate some of the phrase as; \"" + mphrase + "\". However, I have no record for..."
                    else:
                        if full == 1:
                            sixout.str1 = "I believe the modern form of \"" + split_args + "\" is \"" + mphrase + "\"."
                        else:
                            if nope == 1:
                                sixout.str1 = "I am sorry mistress, I am not familiar with any of those word. Are you sure you intended to enter \"" + split_args + "\"?"
                            elif len(missing) != 1:
                                sixout.str1  = "My records are missing the following " + str(len(missing)) + " words; " + misswrds + ". However, I believe the remainder translates as \"" + mphrase + "\"."
                            else:
                                sixout.str1  = "I have no record of \"" + misswrds + "\". However, I believe the remainer translates as \"" + mphrase + "\"."
                else:
                    if get_key(split_args).key != -1:
                        if ancientdict[get_key(split_args).key].index(split_args) == 0: #symbols
                            drawanc(split_args)
                            if ancientdict[get_key(split_args).key][1] == "":
                                sixout.x = 2
                                sixout.str1 ="I believe..."
                                sixout.str2 = "...translates as \"" + get_key(split_args).key + "\"."
                            else:
                                sixout.x = 2
                                sixout.str1 ="I believe..."
                                sixout.str2 = "...or \"" + ancientdict[get_key(split_args).key][1] + "\", translates as \"" + get_key(split_args).key + "\"."
                        else: #words
                            drawanc(ancientdict[get_key(split_args).key][0])
                            sixout.x = 2
                            sixout.str1 ="I believe \"" + split_args + "\", or..."
                            sixout.str2 = "...translates as \"" + get_key(split_args).key + "\"."
                    else:
                        sixout.str1 = "I am sorry mistress, I am afraid I am not familiar with that aspect of the ancient language."
    if cmd == "do":
        sixout.var = 1
        if len(split_argsl) < 3:
            sixout.str1 = "Do *what*, mistress?"
        elif split_argsl[2] == "scan":
            if len(split_argsl) < 4:
                sixout.str1 = "A scan for *what*, mistress?"
            elif split_argsl[3] != "for":
                sixout.str1 = "A scan *for what*, mistress?"
            elif split_argsl[3] == "for" and len(split_argsl) > 4:
                sixout.x = 3
                focus = excta(" ".join(split_argst[4:]))
                sixout.str1 = "Please wait while I scan the area for " + focus + "..."
                sixout.str2 = "..."
                direc = ["north","northwest","northeast","south","southwest","southeast","west","east"]
                findarray = ["...I could not locate any sign of " + focus + " in range, mistress."] + ["...I believe I have detected " + focus + " to the " + random.choice(direc) + ", mistress."]
                sixout.str3 = random.choice(findarray)
            else:
                sixout.str1 = "A scan for *what*, mistress?"
    if cmd == "take":
        if len(split_argsl) >= 3:
            chkt = "".join(split_argsl[0:3])
            chk = excta(chkt)
        else:
            chk = "nul"
        if chk == 'takeamemo':
            if len(split_argsl) < 4:
                sixout.str1 = "*What* memo mistress?"
            else:
                memot = " ".join(split_argst[3:])
                if uname in memo:
                    if memo[uname][-1] == "":
                        memo[uname][-1] = memot
                        backupmemos()
                    else:
                        memo[uname].append(memot)
                        backupmemos()
                else:
                    memo[uname] = [memot]
                    backupmemos()
                sixout.str1 = "Very good mistress, I shall make a note."
    if cmd == "read":
        if len(split_argsl) >= 3:
            chk = "".join(split_argsl[0:3])
            spc = "".join(split_argsl[0:2])
            nm = split_argsl[2]
        else:
            chk = "nul"
            spc = "nul"
            nm = "0"
        if chk == "readlastmemo":
            if uname in memo:
                if memo[uname] != [""]:
                    sixout.str1 = "Mistress, your most recent memo reads: \"" + memo[uname][-1] + "\""
                else:
                    sixout.str1 = "I am sorry mistress, but you have not recorded any memos."
            else:
                sixout.str1 = "I am sorry mistress, but you have not recorded any memos."
        elif chk == "readfirstmemo":
            if uname in memo:
                if memo[uname] != [""]:
                    sixout.str1 = "Mistress, your first memo reads \"" + memo[uname][0] + "\""
                else:
                    sixout.str1 = "I am sorry mistress, but you have not recorded any memos."
            else:
                sixout.str1 = "I am sorry mistress, but you have not recorded any memos."
        elif chk == "readallmemos":
            strprt = "\n".join(memo[uname])
            sixout.str1 = "Mistress here all the memos I have recorded for you:\n" + strprt
        elif spc == "readmemo":
            if uname in memo:
                if len(memo[uname]) >= (int(nm)):
                    if int(nm) >= 1:
                        sixout.str1 = "Mistress, memo " + nm + " reads \"" + memo[uname][int(nm)-1] + "\""
                    else:
                        sixout.str1 = "I am sorry mistress, but I only assign positive values to your memo records."
                else:
                    sixout.str1 = "I am sorry mistress, but you have less than " + nm + " memos recorded."
            else:
                sixout.str1 = "I am sorry mistress, but you have not recorded any memos."
    if cmd == "scratch":
        if len(split_argsl) >= 2:
            chk = "".join(split_argsl[0:2])
        else:
            chk = "nul"
        if chk == "scratchthat":
            if uname in memo:
                del memo[uname][-1]
                backupmemos()
                sixout.str1 = "Very well mistress, I have deleted your last memo from my records."
            else:
                sixout.str1 = "I am sorry mistress, but you have not recorded any memos."
    if cmd == "erase":
        if len(split_argsl) >= 3:
            chk = "".join(split_argsl[0:3])
            spc = "".join(split_argsl[0:2])
            nm = split_argsl[2]
        else:
            chk = "nul"
            spc = "nul"
            nm = "0"
        if chk == "eraselastmemo":
            if uname in memo:
                del memo[uname][-1]
                backupmemos()
                sixout.str1 = "Very well mistress, I have deleted your last memo from my records."
            else:
                sixout.str1 = "I am sorry mistress, but you have not recorded any memos."
        elif chk == "eraseallmemos":
            if uname in memo:
                memo[uname] = [""]
                backupmemos()
                sixout.str1 = "Very well mistress, I have deleted all of your memos from my records."
            else:
                sixout.str1 = "I am sorry mistress, but you have not recorded any memos."
        elif spc == "eraselast":
            if uname in memo:
                if len(memo[uname]) >= (int(nm)):
                    del memo[uname][(len(memo[uname])-int(nm)):]
                    if memo[uname] == []:
                        memo[uname] = [""]
                    backupmemos()
                    sixout.str1 = "Very well mistress, I have deleted your last " + nm + " memos from my records."
                else:
                    sixout.str1 = "I am sorry mistress, but you have less than " + nm + " memos recorded. Perhaps you would like me to *erase all memos* instead?"
            else:
                sixout.str1 = "I am sorry mistress, but you have not recorded any memos."
    if cmd == "i":
        if len(split_argsl) >= 4:
            chk = "".join(split_argsl[0:4])
        else:
            chk = "nul"
        if chk == "iwanttovault":
            sixout.x = 4
            sixout.str1 = "Very well, if you are sure, mistress..."
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
    global ancientdict
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
                drawanc(anchr)
                if engl in ancientdict:
                    dictout.str1 = "This entry already exists."
                else:
                    dictout.x = 1
                    if len(brk) == 2:
                        dictout.str1 = "Entry Added:\n\"" + anchs + "\", meaning \"" + engl + "\", and written...\n"
                    else:
                        dictout.str1 = "Entry Added:\n\"" + engl + "\", written...\n"
                    ancientdict[engl] = [anchr,anchs]
                    backuprecords()
            else:
                dictout.str1 = "Invalid format. Please provide the translation"
        else:
            dictout.str1 = "Invalid format, please check your spacing"
    else:
        dictout.str1 = "Dictionary submissions are only accepted in the archive channel."
    return dictout

def updatedict(args): #function to edit a dictionary entry
    global ancientdict
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
                drawanc(anchr)
                guild = args["guild"]
                dictout.chn = discord.utils.get(guild.text_channels, name='general')
                if engl not in ancientdict:
                    dictout.str1 = "This entry does not yet exist."
                else:
                    dictout.x = 1
                    if len(brk) == 2:
                        dictout.str1 = "Entry Changed:\n\"" + anchs + "\", meaning \"" + engl + "\", and written...\n"
                    else:
                        dictout.str1 = "Entry Changed:\n\"" + engl + "\", written...\n"
                    ancientdict[engl] = [anchr,anchs]
                    backuprecords()
            else:
                dictout.str1 = "Invalid format. Please provide the translation"
        else:
            dictout.str1 = "Invalid format, please check your spacing"
    else:
        dictout.str1 = "Translation updates are only accepted in the archive channel."
    return dictout

def censordict(args): #function to remove a dictionary entry9
    global ancientdict
    dictout = dictoutcl()
    split_argsl = args["content"][1:].lower().split()
    if len(split_argsl) == 1:
        split_argsl.append("null")
    split_argst = args["content"][1:].split()
    if len(split_argst) == 1:
        split_argst.append("")
    if str(args["channel"]) == "archive":
        engl = " ".join(split_argst[1:])
        if engl == "":
            dictout.str1 = "Invalid format. Please provide the entry to be removed."
        else:
            guild = args["guild"]
            dictout.chn = discord.utils.get(guild.text_channels, name='general')
            if engl not in ancientdict:
                dictout.str1 = "This entry does not yet exist."
            else:
                drawanc((ancientdict[engl])[0])
                dictout.x = 1
                dictout.str1 = "Entry Removed:\n\"" + engl + "\""
                ancientdict.pop(engl)
                backuprecords()
    else:
        dictout.str1 = "Translation removal is allowed in the archive channel."
    return dictout

scheduler = BackgroundScheduler()
scheduler.add_job(func=csvexp, trigger="interval", hours=1)
scheduler.start()
# Shut down the scheduler when exiting the app
atexit.register(lambda: scheduler.shutdown())

# client.run("NTY5Mzk4OTE0NjQ2NTQwMzIz.XLwEhQ.Dw8US4osHL5FPSf6PN6YYoovGvs") #SHOP
client.run("NTY5MzgxOTk4NDMxNTY3ODcy.XLv0fA.U6UVquCagOzgl4eXkwi5cB05YMU") #LANG CLUB