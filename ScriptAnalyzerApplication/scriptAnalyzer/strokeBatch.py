import gc, sys, itertools
from PySide.QtCore import *
from PySide.QtGui import *
from PySide.QtUiTools import *
from multiprocessing import Process
from multiprocessing import Pool

import os

from scriptAnalyzer import scriptAnalyzerWindow as SA

if __name__ == "__main__":

    #mW.show()
    #sys.exit(app.exec_())
    
    # List files
    
    print "Starting"
    
    pref = "C:\Users\Administrator\Documents\Script Folder\Corrected Full"
    prefCSV = "C:\Users\Administrator\Desktop\Script_Data"
    
    scripts = ["Tamil","Grantha","Devanagari","Kannada"]
    scriptsAll = ["Tamil_1","Tamil_2","Tamil_3","Tamil_4","Tamil_5","Tamil_6",
                  "Grantha_1","Grantha_2","Grantha_3","Grantha_4","Grantha_5","Grantha_6",
                  "Devanagari_1","Devanagari_2","Devanagari_3","Devanagari_4","Devanagari_5","Devanagari_6",
                  "Kannada_1","Kannada_2","Kannada_3","Kannada_4","Kannada_5","Kannada_6"]
    
    
    #scriptsAll = ["demoA","demoB"]
    
    scriptStrokeNJCount = {}
    scriptStrokeCount = {}

    app = QApplication(sys.argv)
            
    for script in scripts:
        scriptP = pref+"\\"+script+" Corrected Full"
        files = os.listdir(scriptP)
        files = [f for f in files if script in f]
        
        for fileS in files:
            if os.path.isfile(scriptP+"\\"+fileS):# and not os.path.isfile(prefCSV+"\\"+fileS+".csv1"):
                print "Loaded", fileS
                w = SA.mainWindow()
                mW = w.mainWindow  
                w.openScriptBatch(scriptP+"\\"+fileS)
                
#                countNJ = w.dispStrokesNJ()
#                print fileS, "StrokeNJ", countNJ
#                scriptStrokeNJCount[fileS] = countNJ
                
                count = w.dispStrokes()
                print fileS, "Stroke", count
                scriptStrokeCount[fileS] = count                
                
                #w.similarityMap(True,False)
                #w.similarityMap(False,True)
                
                #w.analyzeAll()
                #w.exportCSV()
            

#print "----------------ScriptNJ----------------------"
#print scriptStrokeNJCount
print "----------------Script----------------------"
print scriptStrokeCount
#            
            
        
