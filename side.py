import pickle
ancientdict = {
}
dict_in = open("ancientdict.pickle", "rb")
ancientdict = pickle.load(dict_in)

ancientdict["I"]=["r.1","yauki"]
ancientdict["Heaven's Vault"]=["""'u.)hi "sii""","Bo-cataliti ifarali"]

def backuprecords():
    dict_out = open("ancientdict.pickle","wb")
    pickle.dump(ancientdict, dict_out)
    dict_out.close()

backuprecords()