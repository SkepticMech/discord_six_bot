import discord
import random
import os
import pickle
import asyncio
from PIL import Image, ImageDraw, ImageFont, ImageChops
from ancientdictionary import wordlist, phraselist
from keep_alive import keep_alive

wordlist = {
}
inv_wordlist = {
}
word_in = open("worddict.pickle", "rb")
wordlist = pickle.load(word_in)
inv_word_in = open("inv_worddict.pickle", "rb")
inv_wordlist = pickle.load(inv_word_in)
def backupwords():
    word_out = open("worddict.pickle","wb")
    pickle.dump(wordlist, word_out)
    word_out.close()
    inv_word_out = open("inv_worddict.pickle","wb")
    pickle.dump(inv_wordlist, inv_word_out)
    inv_word_out.close()

phraselist = {
}
inv_phraselist = {
}
phrase_in = open("phrasedict.pickle", "rb")
phraselist = pickle.load(phrase_in)
inv_phrase_in = open("inv_phrasedict.pickle", "rb")
inv_phraselist = pickle.load(inv_phrase_in)
def backupphrases():
    phrase_out = open("phrasedict.pickle","wb")
    pickle.dump(phraselist, phrase_out)
    phrase_out.close()
    inv_phrase_out = open("inv_phrasedict.pickle","wb")
    pickle.dump(inv_phraselist, inv_phrase_out)
    inv_phrase_out.close()

async def user_metrics_background_task():
    await client.wait_until_ready()
    while not client.is_closed():
        try:
            word_out = open("worddict.pickle","wb")
            pickle.dump(wordlist, word_out)
            word_out.close()
            inv_word_out = open("inv_worddict.pickle","wb")
            pickle.dump(inv_wordlist, inv_word_out)
            inv_word_out.close()
            phrase_out = open("phrasedict.pickle","wb")
            pickle.dump(phraselist, phrase_out)
            phrase_out.close()
            inv_phrase_out = open("inv_phrasedict.pickle","wb")
            pickle.dump(inv_phraselist, inv_phrase_out)
            inv_phrase_out.close()
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
    print(f"We have logged in as {client.user}")

@client.event
async def on_message(message): #The main bot functions
    args = {
        "user": message.author,
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
        if len(split_argsl) == 1:
            split_argsl.append("null")
        split_argst = args["content"][1:].split()
        if len(split_argst) == 1:
            split_argst.append("")
        split_args = " ".join(split_argst[2:])
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
        #translate command
        elif cmd == "translate":
            if split_argsl[1] == "word":
                if split_args in wordlist:
                    drawanc(wordlist[split_args])
                    await message.channel.send(file=discord.File("ancient.png"), content = "I believe \"" + split_args + "\"" + " was written...")
                elif len(split_argst) > 3 :
                    await message.channel.send("I am sorry mistress, you seem to be trying to translate a phrase as a word.")
                else:
                    await message.channel.send("I am sorry mistress, I am afraid I do not know that word.")
            elif split_argsl[1] == "phrase":
                if split_args in phraselist:
                    drawanc(phraselist[split_args])
                    await message.channel.send(file=discord.File("ancient.png"), content = "I believe \"" + split_args + "\"" + " was written...")
                elif len(split_argst) < 4 :
                    await message.channel.send("I am sorry mistress, you seem to be trying to translate a word as a phrase.")
                else:
                    await message.channel.send("I am sorry mistress, I am afraid I do not know that phrase.")
            else:
                await message.channel.send("I am sorry mistress, I need to know if you want that translated as a word or a phrase.")
        #inverse translate command
        elif cmd == "invtranslate":
            if split_argsl[1] == "word":
                if split_args in inv_wordlist:
                    drawanc(split_args)
                    await message.channel.send(file=discord.File("ancient.png"), content = "I believe \"" + inv_wordlist[split_args] + "\"" + " is the modern form of...")
                elif len(split_argst) > 3 :
                    await message.channel.send("I am sorry mistress, you seem to be trying to translate a phrase as a word.")
                else:
                    await message.channel.send("I am sorry mistress, I am afraid I do not know that word.")
            elif split_argsl[1] == "phrase":
                if split_args in inv_phraselist:
                    drawanc(split_args)
                    await message.channel.send(file=discord.File("ancient.png"), content = "I believe \"" + inv_phraselist[split_args] + "\"" + " is the modern form of...")
                elif len(split_argst) < 4 :
                    await message.channel.send("I am sorry mistress, you seem to be trying to translate a word as a phrase.")
                else:
                    await message.channel.send("I am sorry mistress, I am afraid I do not know that phrase.")
            else:
                await message.channel.send("I am sorry mistress, I need to know if you want that translated as a word or a phrase.")
        #add dictionary entry
        if cmd == "add":
            if str(args["channel"]) == "archive":
                if "_" in split_argst:
                    brk = split_argst.index("_")
                    engl = " ".join(split_argst[2:brk])
                    anch = " ".join(split_argst[(brk+1):])
                    drawanc(anch)
                    guild = args["guild"]
                    channel = discord.utils.get(guild.text_channels, name='general')
                    await message.channel.send("Checking Submission...")
                    if split_argsl[1] == "word":
                        if len(split_argst) > 5 :
                            await message.channel.send("This seems to be a phrase, not a word.")
                        elif engl in wordlist:
                            await message.channel.send("This entry already exists.")
                        else:
                            await message.channel.send(file=discord.File("ancient.png"), content = "Entry Added:\n" + engl + ":\n")
                            await channel.send('New dictionary submission from ' + str(message.author.display_name))
                            wordlist[engl] = anch
                            inv_wordlist[anch] = engl
                    if split_argsl[1] == "phrase":
                        if len(split_argst) < 6 :
                            await message.channel.send("This seems to be a word, not a phrase.")
                        elif engl in phraselist:
                            await message.channel.send("This entry already exists.")
                        else:
                            await message.channel.send(file=discord.File("ancient.png"), content = "Entry Added:\n" + engl + ":\n")
                            await channel.send('New dictionary submission from ' + str(message.author.display_name))
                            phraselist[engl] = anch
                            inv_phraselist[anch] = engl                            # await client.wait_for('message', backupphrases=backupphrases)
                else:
                    await message.channel.send("Invalid format, missing : character")
            else:
                await message.channel.send("Dictionary submissions are only accepted in the archive channel.")
        if cmd == "update":
            if str(args["channel"]) == "archive":
                if "_" in split_argst:
                    brk = split_argst.index("_")
                    engl = " ".join(split_argst[2:brk])
                    anch = " ".join(split_argst[(brk+1):])
                    drawanc(anch)
                    guild = args["guild"]
                    channel = discord.utils.get(guild.text_channels, name='general')
                    await message.channel.send("Checking Update...")
                    if split_argsl[1] == "word":
                        if len(split_argst) > 5 :
                            await message.channel.send("This seems to be a phrase, not a word.")
                        elif engl not in wordlist:
                            await message.channel.send("This entry does not yet exist.")
                        else:
                            await message.channel.send(file=discord.File("ancient.png"), content = "Entry Updated:\n" + engl + ":\n")
                            await channel.send('New translation update by ' + str(message.author.display_name))
                            wordlist[engl] = anch
                            inv_wordlist[anch] = engl                            # await client.wait_for('message', backupwords=backupwords)
                    if split_argsl[1] == "phrase":
                        if len(split_argst) < 6 :
                            await message.channel.send("This seems to be a word, not a phrase.")
                        elif engl not in phraselist:
                            await message.channel.send("This entry does not yet exist.")
                        else:
                            await message.channel.send(file=discord.File("ancient.png"), content = "Entry Updated:\n" + engl + ":\n")
                            await channel.send('New translation update by ' + str(message.author.display_name))
                            phraselist[engl] = anch
                            inv_phraselist[anch] = engl                            # await client.wait_for('message', backupphrases=backupphrases)
                else:
                    await message.channel.send("Invalid format, missing : character")
            else:
                await message.channel.send("Translation updates are only accepted in the archive channel.")
        if cmd == "remove":
            if str(args["channel"]) == "archive":
                if "_" in split_argst:
                    brk = split_argst.index("_")
                    engl = " ".join(split_argst[2:brk])
                    anch = " ".join(split_argst[(brk+1):])
                    guild = args["guild"]
                    channel = discord.utils.get(guild.text_channels, name='general')
                    await message.channel.send("Checking Update...")
                    if split_argsl[1] == "word":
                        if len(split_argst) > 5 :
                            await message.channel.send("This seems to be a phrase, not a word.")
                        elif engl not in wordlist:
                            await message.channel.send("This entry does not exist.")
                        else:
                            drawanc(wordlist[engl])
                            await message.channel.send(file=discord.File("ancient.png"), content = "Entry Removed:\n" + engl + ":\n")
                            await channel.send('Translation removed by ' + str(message.author.display_name))
                            wordlist.pop(engl)
                            inv_wordlist.pop(anch)                            # await client.wait_for('message', backupwords=backupwords)
                    if split_argsl[1] == "phrase":
                        if len(split_argst) < 6 :
                            await message.channel.send("This seems to be a word, not a phrase.")
                        elif engl not in phraselist:
                            await message.channel.send("This entry does not exist.")
                        else:
                            drawanc(phraselist[engl])
                            await message.channel.send(file=discord.File("ancient.png"), content = "Entry Removed:\n" + engl + ":\n")
                            await channel.send('Translation removed by ' + str(message.author.display_name))
                            phraselist.pop(engl)
                            inv_phraselist.pop(anch)                            # await client.wait_for('message', backupphrases=backupphrases)
                else:
                    await message.channel.send("Invalid format, missing : character")
            else:
                await message.channel.send("Translation updates are only accepted in the archive channel.")
    elif args["content"].lower().startswith("hey six") or args["content"].lower().startswith("six"):
        await message.channel.send(ProcessNameCall(args))
    elif args["content"].lower().startswith("hey enkei") or args["content"].lower().startswith("enkei"):
        await message.channel.send(ProcessNameCallEnkei(args))

def trim(im): #tirms whitespace from image
    bg = Image.new(im.mode, im.size, im.getpixel((0,0)))
    diff = ImageChops.difference(im, bg)
    diff = ImageChops.add(diff, diff, 2.0, -100)
    bbox = diff.getbbox()
    if bbox:
        return im.crop(bbox)

def drawanc(str): #converts string into ancient.png image
	img = Image.new("RGBA", (2000,40), color = (255,255,255, 0))
	fnt = ImageFont.truetype("ancientrunes.ttf", 32)
	d = ImageDraw.Draw(img)
	d.text((0,0), str, font=fnt, fill=(255,255,255))
	imgc = trim(img)
	imgc.save("ancient.png", "PNG")

def ProcessNameCall(args):
    lc_mess = args["content"].lower()
    if (lc_mess.find("do a scan") != -1) and (lc_mess.find("for") == -1):
        reply = "A scan for *what*, mistress?"
    elif lc_mess.find("for") != -1:
	    focus = lc_mess.split("for ",1)[1]
	    reply = "Please wait while I scan the area for " + focus + "...\n...\nI could not locate any " + focus +" in range, mistress."
    else:
        reply = "Yes, mistress?"
    return reply

def ProcessNameCallEnkei(args):
    insultarray = ["pauper","imbicile","Elborethian rat","child"]
    lc_mess = args["content"].lower()
    if (lc_mess.find("do a scan") != -1):
        reply =  "I am not your slave, " + random.choice(insultarray) + "."
    else:
        reply = "What is it, " + random.choice(insultarray) + "?"
    return reply


keep_alive()
token = os.environ.get("LANG_CLUB")
client.loop.create_task(user_metrics_background_task())
client.run(NTY5Mzk4OTE0NjQ2NTQwMzIz.XLwEhQ.Dw8US4osHL5FPSf6PN6YYoovGvs)