import codecs
import math
from pandas import *
import itertools

script = "OverallSim"

path = "C:\Users\Administrator\Dropbox\Similarity_Data\Similarities_Corrected_Static\\"
name = script*2+"NormTrueFalseSim.csv1"

name= "overallStaticSimilarityNorm.csv"

fl = codecs.open(path+name,mode="r")
lines = fl.readlines()
fl.close()

similarityMatrix = []

listValues = []

for i,row in enumerate(lines):
    if i==0:
        removeQuotes = lambda x: x.replace("\"","")
        glyphNames = map(removeQuotes,row.split(",")[:])
        print glyphNames
    else:
        values = map(float,row.split(",")[1:])
        simTrans = lambda x: (1/float(x+1))**(float(1)/2)
        similarityMatrix.append(map(simTrans,values))
        listValues.extend(map(simTrans,values))
                
df = DataFrame(similarityMatrix, index=glyphNames, columns=glyphNames) 

glyphPairs= list(itertools.combinations(glyphNames,2))

print len(glyphPairs)

listValues = [x for x in listValues if x!=1]

minL = min(listValues)
maxL = max(listValues)

print minL,maxL
 
pathWamp = "C:\\Users\\Administrator\\Desktop\\"
name = script+".csv"
fl = codecs.open(pathWamp+name,mode="w")

fl.write("Source,Target,Type,Weight"+"\n")
for glyphR, glyphC in glyphPairs:
            simVal = df[glyphR][glyphC]
            simVal = (simVal - minL)/(maxL - minL)
            fl.write(glyphR.replace("\n","")+","+glyphC.replace("\n","")+",Undirected,"+str(simVal)+"\n")


#fl.write("sequences="+str(len(glyphNames))+"\n")

#fl.write("<seq>"+"\n")
#for glyph in glyphNames:
#    fl.write(">"+glyph+"\n")
#fl.write("</seq>"+"\n")

#fl.write("{\"similarities\":[\n")
#
#for i,glyphR in enumerate(glyphNames):
#    for j,glyphC in enumerate(glyphNames):
#        if glyphC != glyphR:
#            simVal = df[glyphR][glyphC]
#            simVal = (simVal - minL)/(maxL - minL)
#            fl.write("{\"Glyph1\":\""+glyphR.replace("\n","")+"\","+"\"Glyph2\":\""+glyphC.replace("\n","")+"\","+"\"sim\":"+str(simVal)+"},\n")
#
#
#fl.write("]}")

fl.close()
print "Done"







   
    


