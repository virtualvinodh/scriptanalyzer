import os
import codecs
import nltk
from nltk.util import *
from nltk.probability import LaplaceProbDist  
import nltk.probability
from nltk.model import NgramModel

path = "C:\Users\Administrator\Desktop\Script_Data_full"
 
files = [f for f in os.listdir(path) if "csv" in f]

scriptStrokes = {}

## Read 
for f in files:
        fl = codecs.open(path+"\\"+f,mode="r")
        listStrokes = []
        for line in fl.readlines()[1:]:
            strokesQuant =  line.split(",")[-1].replace("[","").replace("]","").replace(" ","").replace("\n","").split("|")
            listStrokes.append(['St']+strokesQuant+['En'])
        
        scriptStrokes[f.split(".")[0]] = listStrokes
        

#k = [("N","Grantha_1"),("N","Grantha_1"),("N","Grantha_1"),("N","Grantha_2"),("N","Grantha_2"),
#     ("N","Grantha_3")]

ScriptContStroke = {}

for script,listStrokes in scriptStrokes.iteritems():
    ScriptContStroke[script] = reduce(lambda x,y:x+y,listStrokes)

ScriptBiGrams = {}    

for script,listStrokes in ScriptContStroke.iteritems():
    ScriptBiGrams[script] = ngrams(listStrokes,2)     
    
#estimator = lambda fdist, bins: LaplaceProbDist(fdist, len(ScriptBiGrams['Devanagari_1'])+1)
#model = NgramModel(2,ScriptBiGrams['Devanagari_1'],estimator=estimator) 

directions = ["N","S","E","W","NE","SE","SW","NW"]

strokeCounts = []
for dirc in directions:
    for script, strokelist in scriptStrokes.iteritems():
        if "Grantha" in script and "7" not in script:
            for strokes in strokelist:
                if dirc in strokes:
                    strokeCounts.append((dirc,script))

cfd = nltk.ConditionalFreqDist(strokeCounts) 
cpd = nltk.ConditionalProbDist(cfd,LaplaceProbDist)
# Use the completd version of the script 
#use probability instead of absolute counts
#Normalize the numbers
cfd.tabulate()
#print cpd['NE'].prob()

print "------------------------------------------------------------"




