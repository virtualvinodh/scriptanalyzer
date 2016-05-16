import matplotlib.pyplot as plt
from pandas import *
import os
import codecs

path = "C:\Users\Administrator\Dropbox\Similarity_Data\Similarities_Corrected_Static"
scripts = ["Grantha","Devanagari","Kannada","Tamil"]

pathMap = "C:\Users\Administrator\Desktop\HeatMaps\Static_2sigma\\"
def dataFramize(fpath):
    similarityMatrix = []
    fl = codecs.open(fpath)
    for i, row in enumerate(fl.readlines()):
        if i==0:
            glyphNames = row.split(",")[:]
            print len(glyphNames)
            removeSuffix = lambda x: x[:x.find("_")]
            glyphNames = map(removeSuffix,glyphNames)
        else:
            similarityMatrix.append(map(float,row.split(",")[1:]))
            
    df = DataFrame(similarityMatrix, index=glyphNames, columns=glyphNames)    
    fl.close()
    return df

def heatMapPlot(similarityMatrix,name,rang):
    name = name.replace("\"","")
    plt.pcolormesh(np.asarray(similarityMatrix),cmap = plt.get_cmap('OrRd'), vmin=0, vmax=rang)# 
    plt.yticks(np.arange(0.5, len(similarityMatrix.index), 1), similarityMatrix.index, fontsize = 3)
    plt.xticks(np.arange(0.5, len(similarityMatrix.columns), 1), similarityMatrix.columns, fontsize = 3)
    plt.colorbar()
    plt.title(name)
    plt.savefig(pathMap+name+".pdf")
    plt.clf()
## Normalize the scripts to same number

simDF = {}

for s in scripts:
    simDF[s] = []
    for i in range(1,7):
        fl = path + "\\" + (s + "_" + str(i))*2 +"NormTrueFalseSim.csv1"
        simDF[s].append(dataFramize(fl))
        
        
for s in scripts:
    for i in range(0,6):
        print s,i
        rang = simDF[s][i].values.mean() + (2 * simDF[s][i].values.std())
        heatMapPlot(simDF[s][i],s+str(i+1),rang)
        

'''
for f in files[1:2]:
    f = "Grantha_1TrueFalseSim.csv1"
    print "Displaying ",f
    fl = codecs.open(path+"\\"+f)
    similarityMatrix = []
    for i, row in enumerate(fl.readlines()):
        if i==0:
            glyphNames = row.split(",")[1:-1]
        else:
            similarityMatrix.append(map(float,row.split(",")[1:-1]))
            
    df = DataFrame(similarityMatrix, index=glyphNames, columns=glyphNames)

    plt.pcolormesh(np.asarray(similarityMatrix),cmap = plt.get_cmap('OrRd') )
    plt.yticks(np.arange(0.5, len(df.index), 1), df.index)
    plt.xticks(np.arange(0.5, len(df.columns), 1), df.columns)
    plt.colorbar()
    plt.show()
        
    plt.clf()
'''
