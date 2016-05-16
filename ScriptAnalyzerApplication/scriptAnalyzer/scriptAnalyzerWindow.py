import sys

from PySide.QtCore import *
from PySide.QtGui import *
from PySide.QtUiTools import *
from utilities import util as utilt ### Utilities functions that are re-usable
from glyphAnalyzer import glyphAnalyzerWindow as MW
from glyphAnalyzer import glyphAnalyzerItems as GI
import numpy, math, pylab
import vizFeature as vf
import cPickle as pickle
from sympy import *
import dtw
import metrics
from collections import OrderedDict as OrderedDict


from pandas import *
import matplotlib.pyplot as plt

# Script tabs for the Script Analyzer
class scriptTab(QTabWidget):
    def __init__(self, *args, **kwargs):
        super(scriptTab,self).__init__( *args, **kwargs)
        
    # Right double click
    def mouseDoubleClickEvent(self,event):
        # Prompt for changing names of script tabs
        text, ok = QInputDialog.getText(self, 'Input Dialog', 'Enter script name:')
        
        if ok:
            self.setTabText(self.currentIndex(),text)

# Glyph thumbnails

# http://zetcode.com/gui/pysidetutorial/
# https://qt.gitorious.org/pyside/pyside-examples/source/64c8a787acff514513a4172f8f97e078d6acf251:examples/painting/svgviewer/svgviewer.py#L108
class glyphThumbnail(QGraphicsScene):
    def __init__(self, *args, **kwargs):
        super(glyphThumbnail,self).__init__( *args, **kwargs)
        
        self.glyph = None
        self.glyphDump = ""
        self.glyphtxt = ""
    
        self.created = False
    
        # Right Click menu for glyph thumbnail
        self.thumbRightClickMenu = QMenu(self.parent())
        
        self.openAction = self.thumbRightClickMenu.addAction(self.tr("Open..."))
        #self.openAction.setShortcut(QKeySequence(self.tr("Ctrl+O")))
        self.dispAction = self.thumbRightClickMenu.addAction(self.tr("Disp Traj..."))
        #self.quitAction.setShortcut(QKeySequence(self.tr("Ctrl+Q")))   
        self.metricAction = self.thumbRightClickMenu.addAction(self.tr("Metrics..."))   
        
        self.connect(self.dispAction,SIGNAL("triggered()"),self.dispTraj)
        

    ## Display Trajectory 
    def dispTraj(self):
            self.windowS = MW.mainWindow()
            self.windowS.parentWid = self
            self.windowS.setParent(self.parent())
        
            self.windowS.loadGlyphString(self.glyphDump)            
                        
            self.windowS.dispTrajectory() #  self.windowS.mainWindow.rankTrajList.setCurrentRow(0) - Displaying first trajectory in the list ?
            self.windowS.close()      
            
    ### Popup menu - Right Click
    def mousePressEvent(self,event):
        if str(event.button()) == "PySide.QtCore.Qt.MouseButton.RightButton":
            pos =  QWidget.mapToGlobal(QWidget(),QPoint(int(event.scenePos().x()),int(event.scenePos().y())))           
            self.thumbRightClickMenu.popup(QCursor.pos())
        
    ### Openup glyph on double click
    def mouseDoubleClickEvent(self,event):
        ## Think of using a constructor for this
        self.windowS = MW.mainWindow()
        self.windowS.parentWid = self
        self.windowS.setParent(self.parent())
        self.windowS.mainWindow.show()        

        ## Load glyphDump only if its been created already
        if self.glyphDump != "":
            self.windowS.loadGlyphString(self.glyphDump)
            
    ### Insert Label text at the position
    def insGlyphID(self,txt):
        label = QGraphicsTextItem(txt)
        self.addItem(label)
        
        label.setPos(70,40)             
        
    ### Create thumbnails
    def thumbNail(self):
        self.clear()

        for points in self.glyph:       
            path = QPainterPath()
            segment = QPolygonF([QPointF(x, y) for x, y in points])
            path.addPolygon(segment)
            
            splinePath = QGraphicsPathItem(path)
            splinePath.scale(0.22,0.22) #splinePath.scale(0.22,0.22)
            
            self.addItem(splinePath)
            
        self.insGlyphID(self.glyphtxt)
        
        self.created = True
            
class mainWindow(QMainWindow):
    def __init__(self):
        super(mainWindow,self).__init__()
        
        Loader = QUiLoader()
        Loader.registerCustomWidget(scriptTab)

        self.scriptIndex = 1
        self.thumbNails = []
        
        uiFile = QFile("../resources/scriptAnalyzerWindow.ui")
        uiFile.open(QFile.ReadOnly)
        self.mainWindow = Loader.load(uiFile)
             
        self.addScriptTab()
    
        self.mainWindow.functCmb.addItems(["getAllHandwritingSignal","initAngle","majorAngle","divergenceAngle","directionCode","similarityMap","getOverallSimilarity","listAngles"])
        
        #self.mainWindow.clearBtn.clicked.connect(self.clear)
        self.mainWindow.vizBtn.clicked.connect(self.vizFeature)
        
        self.mainWindow.displayBtn.clicked.connect(self.dispStrokes)
        self.mainWindow.displayBtnNJ.clicked.connect(self.dispStrokesNJ)
        
        self.mainWindow.addScriptBtn.clicked.connect(self.addScriptTab)
        self.mainWindow.analyzeAllBtn.clicked.connect(self.analyzeAll)
        self.mainWindow.exportCSVBtn.clicked.connect(self.exportCSV)
        self.mainWindow.vizFeatGlyph.clicked.connect(self.vizFeatGlyphs)
        
        self.mainWindow.initAngleBtn.clicked.connect(self.execFunc)
        
        self.mainWindow.featCmb.currentIndexChanged.connect(self.featTypeSelect)
        
        self.mainWindow.actionSave.triggered.connect(self.saveScript)
        self.mainWindow.actionOpen.triggered.connect(self.openScript)
        
        self.glyphDump = ""
        
        #self.mainWindow.graphicsView.scene().addStuff()
        
        ## Geometric Features
        self.geoFeatVal = {"Length":'length',
                           'Divergence':'divergence',
                           'Size':'size',
                           'LBIndex':'LBIndex',
                           'AvgCurv' : 'avgCurv',
                           'Compactness':'compactness',
                           'Openness':'openness',
                           'Descendancy':'descendancy',
                           'Ascension':'ascension',
                           'Circularity':'circularity',
                           'Rectangularity':'rectangularity',                           
                           'Eccentricity':'eccentricity',
                           'Perpendicularity':'perpendicularity'}
        
        ## Not Geometric - 'Aspect':'aspect' :: 
        
        self.strokeNumFeatVal = {"Total Pen Strokes":'pen', 
                                 'Disjoint Strokes':'disjoint', 
                                 'Retraces':'retrace',
                                 'Up Strokes':'up',
                                 'Down Strokes':'down'}
        
        self.prodFeatVal = {'penCount':'penC',
                            'disjointCount' : 'disjointC',
                            'primitiveCount' : 'primitiveC',
                            'retraceCount' : 'retraceC',
                            'upCount' : 'upC',
                            'downCount' : 'downC',
                            'up' : 'up',
                            'down' : 'down',
                            'NIV' : 'NIV',
                            
                            'majorLengths' : 'majorLengths',
                            'strokeLengths' : 'strokeLengths',
                            
                            'changeability' : 'changeability',
                            'disfluency': 'disfluency',
                            'entropy' : 'entropy',
                            
                            'disjointAngles' : 'disjointAngles',
                            'strokeAngles': 'strokeAngles',
                            'penDrag' : 'penDrag',
                            
                            'Avg.Direction':'avgDirections'}
        
        self.strokePropFeatVal = {'Stroke Ratio':'updown',
                                  'Pen Drag':'pendrag',
                                  'Descendancy':'descendancy',
                                  'Ascension':'ascension'}
        
        self.cognFeatVal= {'Minimum Points':'minimumPoints'}
        
        self.FeatSelect = {#"Stroke No.":'strokeNumFeat',
                           "Production":'prodFeat',
                           'Geometric':'geoFeat',
                           #'Stroke Feat.':'strokePropFeat',
                           #'Cognitive':'cognFeat'
                           }        
        
    def exportCSV(self):        
        minPoints = []
        
        self.allProps = []
        
        for nameM,prop in self.FeatSelect.iteritems(): ## Works only for Geoval for now.. Extend it to others laters
            for name,val in getattr(self,prop+'Val').iteritems(): #
                self.allProps.append((prop,val))
        
        csv = open('C:\Users\Administrator\Desktop\Script_Data\\'+self.mainWindow.tabWidget.tabText(self.mainWindow.tabWidget.currentIndex())+'.csv1','w+')
                
        csv.write("glyph,")
        for num,prop in enumerate(self.allProps):
            if num == len(self.allProps):
                csv.write(prop[1]+",")
            else:
                csv.write(prop[1]+",")
        
        csv.write("DirCodes"+"\n")        
        
        for thumb in self.thumbNails[self.mainWindow.tabWidget.currentIndex()]:
            if thumb.scene().created:
                #feat = getattr(thumb.scene().windowS,self.FeatSelect[self.mainWindow.featCmb.currentText()])
                #subFeat = getattr(self,self.FeatSelect[self.mainWindow.featCmb.currentText()]+'Val')[self.mainWindow.subFeatCmb.currentText()]
                #minPoints.append(feat[subFeat])
                csv.write(thumb.scene().glyphtxt+",")
                for num,prop in enumerate(self.allProps):
                    print prop[0],prop[1]
                    try:
                        feat = getattr(thumb.scene().windowS,prop[0]) 
                        if num == len(self.allProps):
                            csv.write(str(feat[prop[1]]).replace("'","").replace(",","|")+",")
                        else:
                            try:
                                csv.write(str(feat[prop[1]]).replace("'","").replace(",","|")+",")
                            except KeyError:
                                csv.write(",")   
                    except:
                        csv.write(",")
                            
        
                csv.write(str(thumb.scene().windowS.directionAngle()).replace("'","").replace(",","|")+"\n")
        
#        for i, data in enumerate(minPoints):
#                csv.write(str(data)+"\n")
            
        csv.close()
        
        print "Exported as CSV"
        
        
    def featTypeSelect(self):                
        self.mainWindow.subFeatCmb.clear()
        
        for key,value in getattr(self,self.FeatSelect[self.mainWindow.featCmb.currentText()]+'Val').iteritems():
            self.mainWindow.subFeatCmb.addItem(key)
            
    def execFunc(self):
        #print "Executing ",self.mainWindow.functCmb.currentText()
        getattr(self,self.mainWindow.functCmb.currentText())()
            
    def initAngle(self):
        angle = []
        
        for thumb in self.thumbNails[self.mainWindow.tabWidget.currentIndex()]:
            if thumb.scene().created:
                #print "Calculating for Glyph", thumb.scene().glyphTxt
                angle.append(thumb.scene().windowS.initAngle())
                
        vf.plotAngle(angle)
                
    def majorAngle(self):        
        angle = []        
        for thumb in self.thumbNails[self.mainWindow.tabWidget.currentIndex()]:
            if thumb.scene().created:
                angle.append(thumb.scene().windowS.majorAngle())
                
        vf.plotAngle(angle)
        
    def divergenceAngle(self):
        angle = []        
        for thumb in self.thumbNails[self.mainWindow.tabWidget.currentIndex()]:
            if thumb.scene().created:
                angle.append(thumb.scene().windowS.divergenceAngle())
                
        vf.plotAngle(angle)        
        
    def listAngles(self):
        angleD, angleA = [], []
                
        for thumb in self.thumbNails[self.mainWindow.tabWidget.currentIndex()]:
            if thumb.scene().created:
                angleD.append(thumb.scene().windowS.listDisjointAngle())
        
        
        for thumb in self.thumbNails[self.mainWindow.tabWidget.currentIndex()]:
            if thumb.scene().created:
                angleA.append(thumb.scene().windowS.listAllStrokeAngle())
            
        print angleD        
        print angleA
        
    def listStrokeLength(self):
        length = []
        
        for thumb in self.thumbNails[self.mainWindow.tabWidget.currentIndex()]:
            if thumb.scene().created:
                length.append(thumb.scene().windowS.listDisjointAngle())
        
    def ngramModel(self):
        #TODO
        
        return
                   
    def directionCode(self):
        strokes = []
        s={"N":1,"NE":2,"E":3,"SE":4,"S":5,"SW":6,"W":7,"NW":8}
        
        y = lambda x: s[x] 
        
        for thumb in self.thumbNails[self.mainWindow.tabWidget.currentIndex()]:
            if thumb.scene().created:
                strokes.append(map(y,thumb.scene().windowS.directionAngle()))
                
        print strokes
                        
        #vf.parallelStrokeDir(strokes)                
                            
    def vizFeatGlyphs(self):
        feat = self.mainWindow.subFeatCmb.currentText()
        
        glyphNames = [thumb.scene().glyphtxt for thumb in self.thumbNails[0] if thumb.scene().created]
        print len(glyphNames)
        
        ScriptAll = []
        scriptFeat = []

        for ind in range(self.mainWindow.tabWidget.count()):
            for thumb in self.thumbNails[ind]:
                if thumb.scene().created:
                    feat = getattr(thumb.scene().windowS,self.FeatSelect[self.mainWindow.featCmb.currentText()])
                    subFeat = getattr(self,self.FeatSelect[self.mainWindow.featCmb.currentText()]+'Val')[self.mainWindow.subFeatCmb.currentText()]
                    scriptFeat.append(feat[subFeat])
                    
            ScriptAll.append(scriptFeat)
            scriptFeat = []
            
        print ScriptAll
                    
        glyphSet = zip(*ScriptAll)
        
        print len(glyphSet)
        
        for i,glyph in enumerate(glyphSet):
            pylab.plot(list(glyph),label=glyphNames[i])
            
        scriptNames = [self.mainWindow.tabWidget.tabText(ind) for ind in range(self.mainWindow.tabWidget.count())]
                
        pylab.legend(bbox_to_anchor=(0., 1.02, 1., .102), loc=3, ncol=2, mode="expand", borderaxespad=0.)   
        pylab.xticks(range(len(scriptNames)),scriptNames) 

        pylab.show()
                    
    def vizFeature(self):
        minPoints = []
        
        col = ['b','g','r','c','m','y','k','w']
        
        boxpoints = []
                
        feat = self.mainWindow.subFeatCmb.currentText()
        
        bplot = self.mainWindow.boxPlotCheck.checkState()
        
        glyphNames = [thumb.scene().glyphtxt for thumb in self.thumbNails[0] if thumb.scene().created]
        #print glyphNames
        
        for ind in range(self.mainWindow.tabWidget.count()):
            for thumb in self.thumbNails[ind]:
                if thumb.scene().created:
                    feat = getattr(thumb.scene().windowS,self.FeatSelect[self.mainWindow.featCmb.currentText()])
                    subFeat = getattr(self,self.FeatSelect[self.mainWindow.featCmb.currentText()]+'Val')[self.mainWindow.subFeatCmb.currentText()]
                    
                    minPoints.append(feat[subFeat])
        
            if not bplot:
                pylab.plot(minPoints,col[ind],label=self.mainWindow.tabWidget.tabText(ind))
                pylab.plot(minPoints,'ro')
            else:
                boxpoints.append(minPoints)
                
                
            minPoints = []
            
        scriptNames = [self.mainWindow.tabWidget.tabText(ind) for ind in range(self.mainWindow.tabWidget.count())]
            
#        pylab.legend(bbox_to_anchor=(0., 1.02, 1., .102), loc=3, ncol=2, mode="expand", borderaxespad=0.)    
        
        if not bplot:
            pylab.xticks(range(len(glyphNames)),glyphNames)  
            pylab.legend(bbox_to_anchor=(0., 1.02, 1., .102), loc=3, ncol=2, mode="expand", borderaxespad=0.)        
            pylab.show()           
        else:
            pylab.legend(bbox_to_anchor=(0., 1.02, 1., .102), loc=3, ncol=2, mode="expand", borderaxespad=0.)   
            pylab.xticks(range(len(scriptNames)),scriptNames)             
            pylab.boxplot(boxpoints)
            pylab.show()
        
#        import rpy2.robjects as R
#        
#        result = R.r['t.test'](R.IntVector(boxpoints[0]),R.IntVector(boxpoints[1]))
#
#        k =  str(result)[str(result).find('p-value = '):]
#
#        print k        

        points1 = []
        points2 = []
        
        strokes = []

#        for thumb in self.thumbNails[0]:
#            if thumb.scene().created:
#                strokes.append(thumb.scene().windowS.quadChangeAct)
#                points1.append(thumb.scene().windowS.geoFeat['openness'])
#                points2.append(thumb.scene().windowS.geoFeat['compactness'])

#        from scipy.stats.stats import pearsonr
#
#        pylab.plot(points1,points2,'gx')
#        pylab.show()
#        
#        r, p =  pearsonr(list(reversed(points1)),list(reversed(points2)))
#        
#        print "Correlation of", r,"with",p,"probability"

        #print strokes      
        
    def transformP(self,points,first=True):
        coOrd = lambda lst,cord : [p[cord] for p in lst]
        
        if first:
            points = map(lambda x: (x[0]-points[0][0],x[1]-points[0][1]),points)
        else:
            xP ,yP = coOrd(points,0), coOrd(points,1)
#            print xP
#            print yP
#            print min(xP), min(yP)
            points = map(lambda x: (x[0]-min(xP),x[1]-min(yP)),points)
#            xP ,yP = coOrd(points,0), coOrd(points,1)
#            print xP
#            print yP            
#            
        return points          
    
    def getOverallGlyph(self, index, static = True):
        if not static:
            glyphList = [ thumb.scene().windowS.getAllPoints() for thumb in self.thumbNails[index] if thumb.scene().created]
        else:
            print index, self.thumbNails                
            glyphList = [ thumb.scene().windowS.getStaticPoints() for thumb in self.thumbNails[index] if thumb.scene().created]     
            
        coOrd = lambda lst,cord : [p[cord] for p in lst]

        overallGlyph = []   
        
        for i,glyph in enumerate(glyphList):
            if i==0:
                #print glyph
                overallGlyph.extend(self.transformP(glyph,first=False))
                #print overallGlyph
            else:
                x1P ,y1P = coOrd(overallGlyph,0), coOrd(overallGlyph,1)
                x2P ,y2P = coOrd(glyph,0), coOrd(glyph,1)
                
                #print x1P, y1P, x2P, y2P
                
                delx, dely = max(x1P) - min(x2P), max(y1P) - min(y2P)
                
                glyph = map(lambda x: (x[0]+delx,x[1]+dely),glyph)
                #print glyph
                
                overallGlyph.extend(glyph)
                        
        return overallGlyph

    def getOverallSimilarity(self):
        print "Comparing Glyphs"
        
        for ind in range(self.mainWindow.tabWidget.count()):
            print ind
            
        print "hello"
        
        Oglyph1 = self.getOverallGlyph(0)
        print "Calculating for second matrix"
        Oglyph2 = self.getOverallGlyph(1)
        
        dtwCost = dtw.dynamicTimeWarp(Oglyph1, Oglyph2)
        
        print "The Cost is ", dtwCost
        
        return 
    
    def getAllHandwritingSignal(self):
        glyphList = [ thumb.scene() for thumb in self.thumbNails[0] if thumb.scene().created]
        #glyphNames = [thumb.scene().glyphtxt for thumb in self.thumbNails[0] if thumb.scene().created]
        
        for glyph in glyphList:
            self.getHandwritingSignal(glyph)
        
        return
    
    def similarityMap(self,static=False,first=True):
        if not static:
            glyphListA = [ thumb.scene().windowS.getAllPoints() for thumb in self.thumbNails[0] if thumb.scene().created]
        else:
            glyphListA = [ thumb.scene().windowS.getStaticPoints() for thumb in self.thumbNails[0] if thumb.scene().created]
            
        if not static:
            glyphListB = [ thumb.scene().windowS.getAllPoints() for thumb in self.thumbNails[1] if thumb.scene().created]
        else:
            glyphListB = [ thumb.scene().windowS.getStaticPoints() for thumb in self.thumbNails[1] if thumb.scene().created]            
        
        print "Calculating Similarity Matrix"
                
        #similarityMatrix =  [[dtw.dynamicTimeWarp(g,glyph) for g in glyphList] for glyph in glyphList]
                
        similarityMatrix = []
        
        glyphNamesA = [thumb.scene().glyphtxt for thumb in self.thumbNails[0] if thumb.scene().created]
        glyphNamesB = [thumb.scene().glyphtxt for thumb in self.thumbNails[1] if thumb.scene().created]        
        
        for i,glyph in enumerate(glyphListA):
            glyph = self.transformP(glyph,first)

            #print "Calculating similarity for",glyphNamesA[i],"th Glyph of", self.mainWindow.tabWidget.tabText(0)
            s =[]
            for j,g in enumerate(glyphListB):
                g = self.transformP(g,first)
                #print g
                #print glyph
                #g = map(lambda x: (x[0]-g[0][0],x[1]-g[0][1]),g)
                print "Calculating similarity for ",glyphNamesA[i],"and",glyphNamesB[j],
                dtwCost = dtw.dynamicTimeWarp(g, glyph)
                print ". And the Cost is", dtwCost
                s.append(dtwCost)
            
            similarityMatrix.append(s)  
                
            #similarityMatrix.append([dtw.dynamicTimeWarp(g,glyph) for g in glyphList])
        
        simCSV = open('C:\Users\Administrator\Desktop\Similarities_Correct\\'+
                      self.mainWindow.tabWidget.tabText(0)+self.mainWindow.tabWidget.tabText(1)+
                      str(static)+str(first)+
                      'Sim.csv1','w+')
        
        simCSV.write("Glyph,")
        
        for j,roww in enumerate(similarityMatrix[0]):
            simCSV.write(glyphNamesB[j]+",")
        
        simCSV.write("\n")
            
        for i,roww in enumerate(similarityMatrix):
            for j,itemm in enumerate(roww):
                if j==0:
                    simCSV.write(glyphNamesA[i]+",")
                    simCSV.write(str(itemm)+",")
                else:
                    simCSV.write(str(itemm)+",")
            simCSV.write("\n")
            
        df = DataFrame(similarityMatrix, index=glyphNamesA, columns=glyphNamesB)
        
        #print df
        
        plt.pcolormesh(np.asarray(similarityMatrix),cmap = plt.get_cmap('OrRd') )
        plt.yticks(np.arange(0.5, len(df.index), 1), df.index)
        plt.xticks(np.arange(0.5, len(df.columns), 1), df.columns)
        plt.colorbar()
        #plt.show()
        plt.savefig('C:\Users\Administrator\Desktop\Similarities_Correct\\'+
                    self.mainWindow.tabWidget.tabText(0)+self.mainWindow.tabWidget.tabText(1)+
                      str(static)+str(first)+
                      'Sim.svg')
        #print similarityMatrix[0][0], similarityMatrix[0][0]
        
        plt.clf()

        #print map(len,glyphList)

    def analyzeAll(self):
        count = 0
        for thumb in self.thumbNails[self.mainWindow.tabWidget.currentIndex()]:
            try:
                if thumb.scene().created:     
                    count += 1
                    print "Glyph", count 
                    #thumb.scene().windowS.classifyStrokeActual()
                    thumb.scene().windowS.strokeViewUpdate(retainCurvature=True)     
                    #thumb.scene().windowS.exstrokeViewUpdate()
                    thumb.scene().windowS.parentWid = thumb.scene()
                    thumb.scene().windowS.setParent(thumb.scene().parent())   
                    thumb.scene().windowS.cls()
            except AttributeError:
                pass
        
    def saveScript(self):
        scripts = []
        
        scriptName = self.mainWindow.tabWidget.tabText(self.mainWindow.tabWidget.currentIndex())
        
        self.mainWindow.statusBar().showMessage("Saving "+scriptName+". Please Wait...",1000000)
        
        for i, thumb in enumerate(self.getActiveThumbs()):
            print "Saving Glyph"
            scripts.append((thumb.scene().windowS.glyphDumpScene(), thumb.scene().windowS.shapeDumpScene()))
            
        saveScript = QFileDialog.getSaveFileName(self.mainWindow, "Save Glyph", "C:\Users\Administrator\Documents\Script Folder\Corrected Full")
        
                
        pickle.dump((scripts,scriptName),open(saveScript[0],"wb"),-1)
        
        self.mainWindow.statusBar().showMessage(scriptName+" saved. "+str(i+1)+" glyphs present",30000)
        
                
    def openScript(self):
        thumbs =  self.thumbNails[self.mainWindow.tabWidget.currentIndex()]
        
        dumpGlyph= None
        
        self.loadGlyphName = QFileDialog.getOpenFileName(self.mainWindow, "Open Glyph", "C:\Users\Administrator\Documents\Script Folder\Corrected Full")
        scriptName = "Unnamed"
        
        try:
            dumpGlyph, scriptName = pickle.load(open(self.loadGlyphName[0],"rb"))
        except ValueError:
            dumpGlyph = pickle.load(open(self.loadGlyphName[0],"rb"))
            
        self.mainWindow.statusBar().showMessage("Loading "+scriptName+". Please Wait...",1000000)            
        
        self.mainWindow.tabWidget.setTabText(self.mainWindow.tabWidget.currentIndex(),scriptName)
        
        for i,glyphs in enumerate(dumpGlyph):
            print "Loading.. ",
            glyphD,glyph = glyphs
            thumbs[i].scene().glyphDump = glyphD
            thumbs[i].scene().glyph = glyph
            thumbs[i].scene().created = True
            thumbs[i].scene().windowS = MW.mainWindow()
            thumbs[i].scene().windowS.loadGlyphString(glyphD)
            thumbs[i].scene().thumbNail()
            try:
                thumbs[i].scene().glyphtxt = thumbs[i].scene().windowS.glyphTxt
                print thumbs[i].scene().windowS.glyphTxt
                thumbs[i].scene().insGlyphID(thumbs[i].scene().windowS.glyphTxt)
            except Exception:
                pass
            
            
        self.mainWindow.statusBar().showMessage(scriptName+" loaded. "+str(i+1)+" glyphs present",30000)

        del dumpGlyph
        import gc
        gc.collect()
        
        
    def getCharList(self,dumpGlyph):
        glyphList = OrderedDict()
          
        for glyphD,glyph in dumpGlyph:
            tempW = MW.mainWindow()
            tempW.loadGlyphString(glyphD)
            glyphList[tempW.glyphTxt] = (glyphD,glyph)      
        
        return glyphList
        
    def openScriptAA(self): ## Filling missing characters
        thumbs =  self.thumbNails[self.mainWindow.tabWidget.currentIndex()]
        dumpGlyph= None
        
        self.loadGlyphName = QFileDialog.getOpenFileName(self.mainWindow, "Open Glyph", "C:\Users\Administrator\Documents\Script Folder")

        dumpGlyph, scriptName = pickle.load(open(self.loadGlyphName[0],"rb"))    
        
        self.mainWindow.tabWidget.setTabText(self.mainWindow.tabWidget.currentIndex(),scriptName)
        
        glyphList = self.getCharList(dumpGlyph)  
        
        spl = self.loadGlyphName[0].split("_")
        new_s = spl[0] + "_" + str(int(spl[1])-1)
        
        dumpGlyph2, scriptName = pickle.load(open(new_s,"rb")) 
        glyphListO = self.getCharList(dumpGlyph2) 
        
        print self.loadGlyphName[0]
        print new_s
        print list(glyphListO.iterkeys())
        print list(glyphList.iterkeys())
        
        i = 0
        
        print set(glyphListO.iterkeys()) - set(glyphList.iterkeys())
        
        for char,glyphs in glyphListO.iteritems():
            print char 
            if char in glyphList:
                glyphD,glyph = glyphList[char]
            else:
                glyphD,glyph = glyphListO[char]
            thumbs[i].scene().glyphDump = glyphD
            thumbs[i].scene().glyph = glyph
            thumbs[i].scene().created = True
            thumbs[i].scene().windowS = MW.mainWindow()
            thumbs[i].scene().windowS.loadGlyphString(glyphD)
            thumbs[i].scene().thumbNail()
            try:
                thumbs[i].scene().glyphtxt = thumbs[i].scene().windowS.glyphTxt
                print thumbs[i].scene().windowS.glyphTxt
                thumbs[i].scene().insGlyphID(thumbs[i].scene().windowS.glyphTxt)
            except Exception:
                pass
            
            i += 1
            
    def openScriptCompare(self,scriptA,scriptB):
        for thumb in self.thumbNails[0]:
            thumb.scene().created=False
            
        if len(self.thumbNails) > 1:
            for thumb in self.thumbNails[1]:
                thumb.scene().created=False     
        else:
            self.addScriptTab()       
        
        thumbsA =  self.thumbNails[0]
        thumbsB =  self.thumbNails[1]
            
        path = "C:\Users\Administrator\Documents\Script Folder\Corrected Full\All\\"

        dumpGlyphA, scriptNameA = pickle.load(open(path+scriptA,"rb"))
        dumpGlyphB, scriptNameB = pickle.load(open(path+scriptB,"rb"))
            
        self.mainWindow.tabWidget.setTabText(0,scriptNameA)
        self.mainWindow.tabWidget.setTabText(1,scriptNameB)
            
        for i,glyphs in enumerate(dumpGlyphA):
            #print "Loading.. 1", scriptNameA
            glyphD,glyph = glyphs
            thumbsA[i].scene().glyphDump = glyphD
            thumbsA[i].scene().glyph = glyph
            thumbsA[i].scene().created = True
            thumbsA[i].scene().windowS = MW.mainWindow()
            thumbsA[i].scene().windowS.loadGlyphString(glyphD)
            thumbsA[i].scene().thumbNail()
            try:
                thumbsA[i].scene().glyphtxt = thumbsA[i].scene().windowS.glyphTxt + "_" + scriptNameA
                print thumbsA[i].scene().windowS.glyphTxt
                thumbsA[i].scene().insGlyphID(thumbsA[i].scene().windowS.glyphTxt + "_" + scriptNameA)
            except Exception:
                pass

        #print i+1,"Glyphs were loaded from", scriptA
                    
        for i,glyphs in enumerate(dumpGlyphB):
            #print "Loading.. 2", scriptNameB
            glyphD,glyph = glyphs
            thumbsB[i].scene().glyphDump = glyphD
            thumbsB[i].scene().glyph = glyph
            thumbsB[i].scene().created = True
            thumbsB[i].scene().windowS = MW.mainWindow()
            thumbsB[i].scene().windowS.loadGlyphString(glyphD)
            thumbsB[i].scene().thumbNail()
            try:
                thumbsB[i].scene().glyphtxt = thumbsB[i].scene().windowS.glyphTxt + "_" + scriptNameB
                print thumbsB[i].scene().windowS.glyphTxt
                thumbsB[i].scene().insGlyphID(thumbsB[i].scene().windowS.glyphTxt + "_" + scriptNameB)
            except Exception:
                pass        

        #print i+1,"Glyphs were loaded from", scriptB

        del thumbsA
        del thumbsB
        import gc
        gc.collect()
        
        
    def openScriptBatch(self,scriptFile):
        for thumb in self.thumbNails[self.mainWindow.tabWidget.currentIndex()]:
            thumb.scene().created=False
            
        thumbs =  self.thumbNails[0]
        
        self.loadGlyphName = scriptFile
        scriptName = "Unnamed"
        
        try:
            dumpGlyph, scriptName = pickle.load(open(self.loadGlyphName,"rb"))
        except ValueError:
            dumpGlyph = pickle.load(open(self.loadGlyphName,"rb"))           
            
        self.mainWindow.tabWidget.setTabText(self.mainWindow.tabWidget.currentIndex(),scriptName)
        
        for i,glyphs in enumerate(dumpGlyph):
            print "Loading.. ",
            glyphD,glyph = glyphs
            thumbs[i].scene().glyphDump = glyphD
            thumbs[i].scene().glyph = glyph
            thumbs[i].scene().created = True
            thumbs[i].scene().windowS = MW.mainWindow()
            thumbs[i].scene().windowS.loadGlyphString(glyphD)
            thumbs[i].scene().thumbNail()
            try:
                thumbs[i].scene().glyphtxt = thumbs[i].scene().windowS.glyphTxt
                print thumbs[i].scene().windowS.glyphTxt
                thumbs[i].scene().insGlyphID(thumbs[i].scene().windowS.glyphTxt)
            except Exception:
                pass
            
        del dumpGlyph
        import gc
        gc.collect()        
        
    def addScriptTab(self):
        scrollArea = QScrollArea()
        widgt = QWidget()
        
        widgt.setGeometry(0,0,1240,550)
        widgt.setLayout(self.newScriptLayout())
        
        scrollArea.setWidget(widgt)
        scrollArea.ensureWidgetVisible(widgt,10,10)
        
        #print scrollArea.widget().size()
        
        self.mainWindow.tabWidget.addTab(scrollArea,"Script"+str(self.scriptIndex))
        self.mainWindow.tabWidget.setCurrentIndex(self.scriptIndex-1)
        self.scriptIndex += 1
        
    def newScriptLayout(self):
        layout = QGridLayout()
        
        self.thumbNailCurrent = []
        
        for i in range(1,7): # was range(1,7)
            for j in range(1,11): # was range(1,11)
                thumbView = QGraphicsView()
                self.thumbNailCurrent.append(thumbView)
                thumbView.setScene(glyphThumbnail(self))
                layout.addWidget(thumbView,i,j)
                
        self.thumbNails.append(self.thumbNailCurrent)
                
        return layout
    
    def getActiveThumbs(self):
        for thumb in self.thumbNails[self.mainWindow.tabWidget.currentIndex()]:
            if thumb.scene().created: 
                yield thumb    
                
    def UniqueLists(self,L):
        return [list(x) for x in set(tuple(x) for x in L)]
                  
    def dispStrokesNJ(self):
        Loader = QUiLoader()
        Loader2 = QUiLoader()
        
        uiFile = QFile("C:/Qt/Qt5.0.1/Tools/QtCreator/bin/ScriptAnalyzerNew/strokewindow.ui")
        uiFile.open(QFile.ReadOnly)
        self.strokeWindow = Loader.load(uiFile)
        uiFile.close()
        
        uiFile = QFile("C:/Qt/Qt5.0.1/Tools/QtCreator/bin/ScriptAnalyzerNew/strokewindow.ui")
        uiFile.open(QFile.ReadOnly)
        self.strokeWindow2 = Loader2.load(uiFile)
        uiFile.close()
        
        layout = QGridLayout()
        layout2 = QGridLayout()
        
        subStrokesListAll = []
        
        count = 0
        for thumb in self.thumbNails[self.mainWindow.tabWidget.currentIndex()]:
            if thumb.scene().created:     
                count += 1
                print "Glyph", count
                #subStrokesListAll.extend(thumb.scene().windowS.updStrokes#
                subStrokesListAll.extend(thumb.scene().windowS.majorStrokePointList)
                
        OldCount = len(subStrokesListAll)
                
        count = 0
        for i in range(0,15):
            for j in range(0,15):
                view = QGraphicsView()
                layout2.addWidget(view,i,j)
                #print i,j
                scene = QGraphicsScene()
                
                path = QPainterPath()
                #print count
                #print subStrokesListAll[count]
                #print subStrokesListAll[count][0]
                
                strokeAP = GI.BSpline(subStrokesListAll[count]).points
                
                strokeAP = map(lambda x: (x[0]-strokeAP[0][0],x[1]-strokeAP[0][1]),strokeAP)
                
                segment = QPolygonF([ QPointF(x, y) for x, y in strokeAP])
                path.addPolygon(segment)
    
                splinePath = QGraphicsPathItem() 
                splinePath.setPath(path)  
                splinePath.scale(0.2,0.2)
                    
                scene.addItem(splinePath)
                view.setScene(scene)

                count += 1
                
                if count == len(subStrokesListAll):
                    print "Count", count
                    break
                
            if count == len(subStrokesListAll):
                    print "Count", count
                    break
        
        self.strokeWindow2.strokeslist.setLayout(layout2);
        
        self.strokeWindow2.show()    
                
       # print len(subStrokesListAll)   
       
       # Reduce Stroke Inventory by imposing a threshold
       
        print "Reducing Strokes...", len(subStrokesListAll)
        
        #subStrokesListAll = subStrokesListAll[:10]
        
        print "Reducing Strokes...", len(subStrokesListAll)
        subStrokesListAllNew = subStrokesListAll
        
        equality = []
       
        for i,m in enumerate(subStrokesListAll):
            equEl = [i]
            for j,n in enumerate(subStrokesListAll):
                stroke1 = GI.BSpline(m).points
                stroke2 = GI.BSpline(n).points
                stroke1 = map(lambda x: (x[0]-stroke1[0][0],x[1]-stroke1[0][1]),stroke1)
                stroke2 = map(lambda x: (x[0]-stroke2[0][0],x[1]-stroke2[0][1]),stroke2)
                print i,j, len(stroke1), len(stroke2)
                dtwcost = dtw.dynamicTimeWarp(stroke1,stroke2)
                #print dtwcost
                if dtwcost < 3000 and i!=j:
                    print i,j, "equal"
                    count += 1
                    if count > 0:
                        equEl.append(j)
            print "Adding", equEl
            equality.append(equEl)

        print "---------------Similar Strokes-------------------------"
        
        equality = map(sorted,equality)
        #print equality, len(equality)
        #print self.UniqueLists(equality), len(self.UniqueLists(equality))
        equality = sorted(self.UniqueLists(equality),key=len,reverse=True)
        #print len(equality)
        
        equality = map(sorted,[eq for eq in equality if len(eq)>1])
        
        #print len(equality)   
        
                             
        for eq in equality:
            print eq
            
        eql = zip([eq[0] for eq in equality],[eq[1:] for eq in equality])
        orig = {}
        remAll  = []
        
        for ori,rem in eql:
            if ori not in orig.keys():
                orig[ori] = rem
                remAll.extend(rem)
            else:
                remTo = list(set(rem)-set(orig[ori]))
                remAll.extend(remTo)    
                
        subStrokesListAll = [stroke for i,stroke in enumerate(subStrokesListAll) if i not in remAll]      
            
        print "-------------------------------------------------------" 
       
        print "Reducing Strokes Complete...", len(subStrokesListAll)
        NewCount = len(subStrokesListAll)
        
        count = 0
        
        for i in range(0,15):
            for j in range(0,15):
                view = QGraphicsView()
                layout.addWidget(view,i,j)
                scene = QGraphicsScene()
                
                path = QPainterPath()
                #print subStrokesListAll[count]
                #print subStrokesListAll[count][0]
                
                strokeAP = GI.BSpline(subStrokesListAll[count]).points
                
                strokeAP = map(lambda x: (x[0]-strokeAP[0][0],x[1]-strokeAP[0][1]),strokeAP)
                
                segment = QPolygonF([ QPointF(x, y) for x, y in strokeAP])
                path.addPolygon(segment)
    
                splinePath = QGraphicsPathItem() 
                splinePath.setPath(path)  
                splinePath.scale(0.2,0.2)
                    
                scene.addItem(splinePath)
                view.setScene(scene)

                count += 1
                
                if count == len(subStrokesListAll):
                    break
                
            if count == len(subStrokesListAll):
                    break
        
        self.strokeWindow.strokeslist.setLayout(layout);
        self.strokeWindow.show()  
        
        return (OldCount,NewCount)
    
    def lognorm(self,t,s,m,d):
        pref = (d/(s*(2*pi)**0/5)*t)
        v = pref*exp(-(1/(2*s**2))*(log(t)-m)**2)
        return v
    
    def getHandwritingSignal(self,glyph):
        speed = 100 #units/per second
            
        strokeList = glyph.windowS.subStrokesAll
        strokeListNew = []
        
        strokeListNew.append(strokeList[0])
        
        for i in range(1,len(strokeList)):
            x1,y1,x2,y2 = strokeList[i-1][-1][0], strokeList[i-1][-1][1], strokeList[i][0][0], strokeList[i][0][1]
            dist = utilt.dist((x1,y1),(x2,y2))
            if dist < 1:
                strokeListNew.append(strokeList[i])
            else:
                pointsLine = utilt.get_line(x1,y1,x2,y2)
                print "Line Added"
                strokeListNew.append(pointsLine)
                strokeListNew.append(strokeList[i])
        
            
        print glyph.glyphtxt
                
        velocity = []
        hws = []
        t = 0
                    
        for i,stroke in enumerate(strokeListNew):

            length = utilt.lengthPnts(stroke)
            totTime = float(length)/speed
            #print "Stroke", i
            #print "Length", length
            #print "Total Time", totTime
                    
            velocity = [self.lognorm(tim,0.5,-1.498,length) for tim in np.arange(0.005,totTime,0.005)]
            #print "Points, ", len(velocity)
            #plt.plot(velocity)
            #plt.show()
                    
            hws.append((t*0.005,stroke[0][0],stroke[0][1]))
            t += 1
            ds = 0
            start = 1
                    
            count = 0
            for i,v in enumerate(velocity[:]):
                #print i,v,
                tm = t * 0.005 # Total Time Elapsed
                d =  v * 0.005 # Dist Travel for this vel
                ds +=  d
             #   print "distance", d, "total", ds, "time", t, tm
                        
                if ds > length:
                    count += 1
                    hws.append((tm,stroke[start][0],stroke[start][1]))
                    if count > 1:
                        break
                            
                for l in range(start,len(stroke)):
                    err =  math.fabs(utilt.lengthPnts(stroke[:l]) - ds)                        
                    if err < 0.03:
                        hws.append((tm,stroke[l][0],stroke[l][1]))
              #          print "Found", l
                        start = l
                        break
                
                t += 1
                        
                        
        import createHWS
        createHWS.createSignal(hws,glyph.glyphtxt)
                     
#                plt.plot(velocity)
#                plt.show()
                       
                 
                #signal.append(thumb.scene().windowS.initAngle())        
        
        
        return
                         
        
    def dispStrokes(self):
        Loader = QUiLoader()
        Loader2 = QUiLoader()
        
        uiFile = QFile("C:/Qt/Qt5.0.1/Tools/QtCreator/bin/ScriptAnalyzerNew/strokewindow.ui")
        uiFile.open(QFile.ReadOnly)
        self.strokeWindow = Loader.load(uiFile)
        uiFile.close()
        
        uiFile = QFile("C:/Qt/Qt5.0.1/Tools/QtCreator/bin/ScriptAnalyzerNew/strokewindow.ui")
        uiFile.open(QFile.ReadOnly)
        self.strokeWindow2 = Loader2.load(uiFile)
        uiFile.close()
        
        layout = QGridLayout()
        layout2 = QGridLayout()
        
        subStrokesListAll = []
        
        count = 0
        for thumb in self.thumbNails[self.mainWindow.tabWidget.currentIndex()]:
            if thumb.scene().created:     
                count += 1
                print "Glyph", count
                #print thumb.scene().windowS.updStrokes
                subStrokesListAll.extend(thumb.scene().windowS.updStrokes)
                #subStrokesListAll.extend(thumb.scene().windowS.majorStrokePointList)
                
        #print len(subStrokesListAll)   
        OldCount = len(subStrokesListAll)
        print "Total Substrokes", len(subStrokesListAll)
        
        count = 0
        for i in range(0,15):
            for j in range(0,15):
                view = QGraphicsView()
                layout.addWidget(view,i,j)
                scene = QGraphicsScene()
                
                path = QPainterPath()
                #print subStrokesListAll[count][0]
                #segment = QPolygonF([ QPointF(x, y) for x, y in subStrokesListAll[count][0] ])
                segment = QPolygonF([ QPointF(x, y) for x, y in subStrokesListAll[count][0] ])
                path.addPolygon(segment)
    
                splinePath = QGraphicsPathItem() 
                splinePath.setPath(path)  
                splinePath.scale(0.2,0.2)
                    
                scene.addItem(splinePath)
                view.setScene(scene)

                count += 1
                
                if count == len(subStrokesListAll):
                    break
                
            if count == len(subStrokesListAll):
                    break
        
        self.strokeWindow.strokeslist.setLayout(layout)
        self.strokeWindow.show()
        
        equality = []
       
        for i,m in enumerate(subStrokesListAll):
            equEl = [i]
            for j,n in enumerate(subStrokesListAll):
                print "i","j",i,j
                stroke1 = [ (x, y) for x, y in subStrokesListAll[i][0] ]
                stroke2 = [ (x, y) for x, y in subStrokesListAll[j][0] ]
                stroke1 = map(lambda x: (x[0]-stroke1[0][0],x[1]-stroke1[0][1]),stroke1)
                stroke2 = map(lambda x: (x[0]-stroke2[0][0],x[1]-stroke2[0][1]),stroke2)
                print "i","j",i,j, len(stroke1), len(stroke2)
                
                stepStroke1 = len(stroke1)/200
                if stepStroke1 == 0:
                    stepStroke1 = 1
                    
                stepStroke2 = len(stroke2)/200
                if stepStroke2 == 0:
                    stepStroke2 = 1                    
                
                stroke1 = [stroke1[k] for k in range(0,len(stroke1),stepStroke1)]
                stroke2 = [stroke2[k] for k in range(0,len(stroke2),stepStroke2)]
                print "i","j",i,j, len(stroke1), len(stroke2)
                
                dtwcost = dtw.dynamicTimeWarp(stroke1,stroke2)
                #print dtwcost
                if dtwcost < 3000 and i!=j:
                    print i,j, "equal"
                    count += 1
                    if count > 0:
                        equEl.append(j)
            print "Adding", equEl
            equality.append(equEl)

        print "---------------Similar Strokes-------------------------"
        
        equality = map(sorted,equality)
        #print equality, len(equality)
        #print self.UniqueLists(equality), len(self.UniqueLists(equality))
        equality = sorted(self.UniqueLists(equality),key=len,reverse=True)
        #print len(equality)
        
        equality = map(sorted,[eq for eq in equality if len(eq)>1])
        
        #print len(equality)   
        
                             
        for eq in equality:
            print eq
            
        eql = zip([eq[0] for eq in equality],[eq[1:] for eq in equality])
        orig = {}
        remAll  = []
        
        for ori,rem in eql:
            if ori not in orig.keys():
                orig[ori] = rem
                remAll.extend(rem)
            else:
                remTo = list(set(rem)-set(orig[ori]))
                remAll.extend(remTo)    
                
        subStrokesListAll = [stroke for i,stroke in enumerate(subStrokesListAll) if i not in remAll]      
            
        print "-------------------------------------------------------" 
       
        print "Reducing Strokes Complete...", len(subStrokesListAll)
        NewCount = len(subStrokesListAll)  
        
        count = 0

        for i in range(0,15):
            for j in range(0,15):
                view = QGraphicsView()
                layout2.addWidget(view,i,j)
                scene = QGraphicsScene()
                
                path = QPainterPath()
                #print subStrokesListAll[count][0]
                #segment = QPolygonF([ QPointF(x, y) for x, y in subStrokesListAll[count][0] ])
                segment = QPolygonF([ QPointF(x, y) for x, y in subStrokesListAll[count][0] ])
                path.addPolygon(segment)
    
                splinePath = QGraphicsPathItem() 
                splinePath.setPath(path)  
                splinePath.scale(0.2,0.2)
                    
                scene.addItem(splinePath)
                view.setScene(scene)

                count += 1
                
                if count == len(subStrokesListAll):
                    break
                
            if count == len(subStrokesListAll):
                    break
        
        self.strokeWindow2.strokeslist.setLayout(layout2)
        self.strokeWindow2.show()
        
        return (OldCount,NewCount)
        
        #self.strokeWindow.show()
        
            
if __name__ == "__main__":
    app = QApplication(sys.argv)
    newWindow = mainWindow()
    newWindow.mainWindow.show()
    sys.exit(app.exec_())