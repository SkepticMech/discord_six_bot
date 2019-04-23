import pickle
import random
from PIL import Image, ImageDraw, ImageFont, ImageChops



ancientdict = {
}
dict_in = open("ancientdict.pickle", "rb")
ancientdict = pickle.load(dict_in)

class dictoutcl:
    def __init__(self):
        self.chn = 0
        self.str1 = ""
        self.str2 = ""
        self.str3 = ""
        self.x = 0


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

def get_key(val): 
    for key, value in ancientdict.items(): 
         if val in value: 
             return key 
    return -1

def addword(args):
    dictout = dictoutcl()
    split_argsl = args[1:].lower().split()
    if len(split_argsl) == 1:
        split_argsl.append("null")
    split_argst = args[1:].split()
    if len(split_argst) == 1:
        split_argst.append("")
    cmd = split_argsl[0]
    
def censordict(args):
    dictout = dictoutcl()
    split_argsl = args[1:].lower().split()
    if len(split_argsl) == 1:
        split_argsl.append("null")
    split_argst = args[1:].split()
    if len(split_argst) == 1:
        split_argst.append("")
    if 1 == 1: #if str(args["channel"]) == "archive":
        engl = " ".join(split_argst[1:])
        print(engl)
        if engl == "":
            dictout.str1 = "Invalid format. Please provide the entry to be removed."
        else:
            dictout.x = 1
            # guild = args["guild"]
            # dictout.chn = discord.utils.get(guild.text_channels, name='general')
            dictout.str1 = "Checking Deletion..."
            if engl not in ancientdict:
                dictout.str2 = "This entry does not yet exist."
            else:
                dictout.x = 2
                dictout.str2 = "Entry Remove:\n\"" + engl + "\""
                dictout.str3 = "Dictionary entry removed by " #+ args["name"]
                ancientdict.pop(engl)
    else:
        dictout.str1 = "Translation removal is allowed in the archive channel."
    return dictout
args = "!remove you"
test=censordict(args)
print(test.str2)
print(ancientdict)