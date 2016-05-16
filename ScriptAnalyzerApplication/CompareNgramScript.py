import os
import codecs
import nltk
from nltk.util import *
from nltk.probability import LaplaceProbDist  
from nltk.model import NgramModel

path = "C:\Users\Administrator\Desktop\Script_Data"
 
files = [f for f in os.listdir(path) if "csv" in f]

scriptStrokes = {}

## Read stroke data from files into variables
for f in files:
        fl = codecs.open(path+"\\"+f,mode="r")
        listStrokes = []
        for line in fl.readlines()[1:]:
            strokesQuant =  line.split(",")[-1].replace("[","").replace("]","").replace(" ","").replace("\n","").split("|")
            listStrokes.append(['St']+strokesQuant+['En'])
        
        scriptStrokes[f.split(".")[0]] = listStrokes