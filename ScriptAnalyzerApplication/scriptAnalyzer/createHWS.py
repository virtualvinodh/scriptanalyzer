'''
Created on 13 Apr 2015

@author: Administrator
'''

# http://ac.els-cdn.com/000169189390006D/1-s2.0-000169189390006D-main.pdf?_tid=19951ffc-e46f-11e4-be37-00000aab0f6b&acdnat=1429212835_692b363602c9a5cab27b93edfa607c8e
# 

def createSignal(hws,glyphName): 
    import codecs
    import numpy as np
    
    filePath = "C:\Users\Administrator\Desktop\\"
    
    fileS = codecs.open(filePath+glyphName+".hws",mode="w")
    
    nl = "\n"
    
    fileS.write("TypeFichier: HWS"+nl)
    fileS.write("NombrePoints: "+str(len(hws))+nl)
    fileS.write("FrequenceEchantillonage(Hz): 200.00"+nl)
    
    for t,startPosX,startPosY in hws:
        fileS.write("%.6f %.6f %.6f %.6f %.6f %.6f %.6f %.6f" % (t,startPosX,-startPosY,0,1.0,0,0,0)) #
        fileS.write(nl)

    fileS.close()
