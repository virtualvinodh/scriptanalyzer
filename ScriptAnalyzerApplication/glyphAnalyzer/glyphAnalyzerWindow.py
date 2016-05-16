## -*- coding: utf-8 -*-

### Bunch of stuff to make sure Matplotlib graphs can be embedded inside PySide Windows
import matplotlib
matplotlib.use('Qt4Agg')
matplotlib.rcParams['backend.qt4']='PySide'
from matplotlib.backends.backend_qt4agg import FigureCanvasQTAgg as FigureCanvas
from matplotlib.figure import Figure
import time

import sys, time, copy, ast, itertools, math,numpy,pylab
import codecs
import cPickle as pickle # cPickle is faster and don't create Memory Dump Error. Pickle can't handle large files
from scipy.interpolate import splprep,splev

### Pyside Imports
from PySide.QtCore import *
from PySide.QtGui import *
from PySide.QtUiTools import *

from glyph import classGlyph as CG
import trajectoryDisplay as TD ### Pygame display of Trajectory
import douglas as dg ### Ramer-Douglas-Peucker Algorthism to reduce points
from utilities import util ### Utilities functions that are re-usable

from glyphAnalyzerItems import *
from glyphAnalyzerScenes import *

import cv2

### Look into this: https://opencv-python-tutroals.readthedocs.org/en/latest/py_tutorials/py_imgproc/py_contours/py_contour_features/py_contour_features.html

class mainWindow(QMainWindow):
    
    ### Change it to variable parameter
    def __init__(self):
        super(mainWindow,self).__init__()
        
        #self.parentWid = parentWid
        self.colors =["#FE2E2E","#01DF01","#2E2EFE","#FE2EF7","#04B4AE","#FE2E2E","#01DF01","#2E2EFE","#FE2EF7","#04B4AE"] * 4
        self.parentWid = ""
        
        Loader = QUiLoader()
        uiFile = QFile("../resources/glyphAnalyzerWindow.ui")
        uiFile.open(QFile.ReadOnly)        
        self.mainWindow = Loader.load(uiFile)
                        
        self.addScenes()
        self.addButtons()
        self.addMenu()
        
        self.mainWindow.minLengthCheck.setCheckState(Qt.Checked)
        self.mainWindow.minCurveCheck.setCheckState(Qt.Checked)
        self.mainWindow.dirCheck.setCheckState(Qt.Checked)
        self.mainWindow.L2RCheck.setCheckState(Qt.Checked)
        self.mainWindow.T2BCheck.setCheckState(Qt.Checked)
        
        self.colorsd = ["r","g"] * 30
        
        self.log = ""

        self.features = ['strokeNum','geo','strokeProp']
        
        self.geoPos = {'breadthIndex':0,'compactness':1,'openness':2,'aspect':3,'length':4,'avgCurv':5}
        self.strokeNumPos = {'pen':0, 'disjoint':1, 'retrace':2, 'up':3, 'down': 4 }
        self.strokePropPos = {'updown':0,'NIV':1, 'pendrag':2}   
        
        self.strokeNumFeat = {} 
            
        self.write = False
        
        #self.mainWindow.glyphView.scene().addImage(["C:\Users\Administrator\Desktop\g.png",""])

        self.mainWindow.closeEvent = self.myCloseEvent
        
        self.closeEvent = self.myCloseEvent

    def addScenes(self):
        self.mainWindow.glyphView.setScene(glyphScene(self))     
        self.mainWindow.glyphView.setRenderHints(QPainter.Antialiasing | QPainter.TextAntialiasing)   
        
        self.mainWindow.traceView.setScene(traceScene(self))     
        self.mainWindow.traceView.setMouseTracking(True)
        self.mainWindow.traceView.setRenderHints(QPainter.Antialiasing | QPainter.TextAntialiasing)     
        
        self.mainWindow.strokeView.setScene(strokeScene())     
        self.mainWindow.strokeView.setRenderHints(QPainter.Antialiasing | QPainter.TextAntialiasing)            

        self.mainWindow.subStrokeView.setScene(subStrokeScene())     
        self.mainWindow.subStrokeView.setRenderHints(QPainter.Antialiasing | QPainter.TextAntialiasing)            
                
    def addButtons(self):
        self.mainWindow.importImgBtn.clicked.connect(self.selectFile)
        
        self.mainWindow.clearBtn.clicked.connect(self.clearScene)

        self.mainWindow.autoTraceBtn.clicked.connect(self.autoTraceNodes)
        self.mainWindow.autoTraceBtn_2.clicked.connect(self.autoTraceEdges)
        self.mainWindow.closeBtnN.clicked.connect(self.cls)

        
        self.mainWindow.trajGenBtn.clicked.connect(self.generateTrajectory)
        self.mainWindow.trajDispBtn.clicked.connect(self.dispTrajectory)  
        
        self.mainWindow.rankTrajList.doubleClicked.connect(self.editTrajectory)
        self.mainWindow.rankTrajList.itemChanged.connect(self.logTrajectory)
        
        self.mainWindow.zoomSpin.valueChanged.connect(self.zoomView)
        
        self.mainWindow.strokeAnalyzeBtn.clicked.connect(self.strokeViewUpdate)
        self.mainWindow.reAnalyzeBtn.clicked.connect(self.classifyStrokeActual)
        
        self.mainWindow.viewLog.clicked.connect(self.viewChangeLog)
        
    def addMenu(self):
        self.mainWindow.actionOpen_Image.triggered.connect(self.selectFile)
        self.mainWindow.actionOpen_Glyph.triggered.connect(self.loadGlyph)
        self.mainWindow.actionSave_Glyph.triggered.connect(self.saveGlyph)
                
    def glyphDumpScene(self):
        return self.glyphDump(self.mainWindow.glyphView.scene())
    
    def shapeDumpScene(self):
        return self.shapeDump(self.mainWindow.glyphView.scene())
    
    def viewChangeLog(self):
        
        Loader = QUiLoader()
        uiFile = QFile("../resources/logwindow.ui")
        uiFile.open(QFile.ReadOnly)   
        self.logwindow = Loader.load(uiFile)
        uiFile.close()
        
        self.logwindow.textEdit.insertPlainText(self.log)
        
        self.logwindow.show()
        
    def cls(self):
        self.parentWid.glyph = self.shapeDump(self.mainWindow.glyphView.scene())
        self.parentWid.glyphDump = self.glyphDump(self.mainWindow.glyphView.scene())
        self.parentWid.glyphtxt = self.mainWindow.glyphIDTxt.text()
        
        self.parentWid.thumbNail()
        
        self.mainWindow.close()
        
    def autoTraceNodes(self):
        self.mainWindow.statusBar().showMessage("Autotracing Glyph. Please wait...",1000000)
        
        import cv2.cv as cv
        import numpy as np
        
        filename = "thinned.png"
        
        img = cv2.imread(filename)
        gray = cv2.cvtColor(img,cv2.COLOR_BGR2GRAY)
                
        gray = np.float32(gray)
        dst = cv2.cornerHarris(gray,2,7,0.08)
                
        #result is dilated for marking the corners, not important
        dst = cv2.dilate(dst,None)
                
        # Threshold for an optimal value, it may vary depending on the image.
        img[dst>0.2*dst.max()]=[5,6,255]
                
        import Image
        
        print 
        
        cv2.imwrite('thinnedCorner.png',img)
        
        #cv2.imshow('Corners Detected',img)

        img = numpy.asarray(Image.open('thinnedCorner.png'))
        
        coOrds = []
        
        for i,r in enumerate(img):
            for j,d in enumerate(r):
                if len(set(d)) != 1:
                    coOrds.append((i,j))
        
        for x,y in coOrds:
            self.mainWindow.glyphView.scene().addNode(y,x)                
                
        self.mainWindow.statusBar().showMessage("Autotracing nodes complete",30000)
        
                
        return
    
    def autoTraceEdges(self):
        self.mainWindow.statusBar().showMessage("Autotracing edges. Please wait...",1000000)
        
        import Image
        
        img = numpy.asarray(Image.open('thinned.png').convert('L'))      
        img.setflags(write=True) 
        
        edgeCreated = True
        
        while(edgeCreated != False):
            img,edgeCreated = self.drawEdges(img)
    
        #print "Traj Points", len(writCoords)

        self.mainWindow.statusBar().showMessage("Autotracing edges complete.",30000)
        
        #cv2.imshow('Drawn Edges',blank_image)
        #cv2.imshow('Remaining Edges',img)
        
        return
    
    def drawEdges(self,img):
        thinnedCoord = []

        for i,row in enumerate(img):
            for j, d in enumerate(row):
                if d == 0:
                    thinnedCoord.append((j,i))        
            
        #print [util.getclosestpnt(thinnedCoord,(node.xP,node.yP)) for node in self.mainWindow.glyphView.scene().Nodes]

        nodes = [thinnedCoord[util.getclosestpnt(thinnedCoord,(node.xP,node.yP))] for node in self.mainWindow.glyphView.scene().Nodes if util.getclosestpnt(thinnedCoord,(node.xP,node.yP)) != None]
        
        print "Total number of Nodes", len(nodes)
        print "The Nodes are", nodes
        
        blank_image = numpy.zeros((img.shape[0],img.shape[1],3), numpy.uint8)
        
        edgeCreated = False
        
        for node in nodes:
            print "Searching edges from ", node
        
            y,x = node
            nd = node
    
            x,y = self.checkWindow(x, y, img)
            
            writCoords = []
            writCoords.append((x,y))

            nodesN = nodes[:]
             
            nodesN.remove(nd)
    
            count = 0
            nodeNear = False
    
            #while((x,y) not in nodes):
            while(not nodeNear):
                count += 1
                #print "Connect points are", x,y
                img[x][y] = 255
    
                x,y = self.checkWindow(x, y, img)
    
                if (x,y) == (-1,-1):
                    #print writCoords
                    break
                
                writCoords.append((x,y))
                blank_image[x,y] = [0,0,255]
                
                nearDist = sorted(map(lambda p:util.dist(p,(y,x)),nodesN))
                
                #print nearDist 
                
                if count > 10 and nearDist[0] < 5:
                    nodeNear = True
                
            writCoords = [p for i,p in enumerate(map(lambda x:(x[1],x[0]),writCoords)) if i%3 ==0]
            
            if len(writCoords) > 10:       
                print "Found Edge", len(writCoords)
                self.writeStrokePnts(writCoords)
                edgeCreated = True
                
            else:
                print "Edges too short", len(writCoords)        
        
        return (img,edgeCreated)
    
    def checkWindow(self,x,y,img):
        #print "Checking Window"
        
        if img[x+1][y] == 0:
            #print "x+1",x+1,"y",y,img[x+1][y]
            return (x+1,y)
        elif img[x-1][y] == 0:
            #print "x-1",x+1,"y",y,img[x-1][y]
            return (x-1,y)
        elif img[x][y+1] == 0:
            #print "x",x,"y+1",y,img[x][y+1]
            return (x,y+1)
        elif img[x][y-1] == 0:
            #print "x",x,"y-1",y,img[x][y-1]
            return (x,y-1)        
        else:
            #print (-1,-1)
            return (-1,-1)
        
    def checkWindowRec(self,x,y,img):
        #print "Checking Window"
        
        connectComp = []
        
        if img[x+1][y] == 0:
            #print "x+1",x+1,"y",y,img[x+1][y]
            connectComp.append((x+1,y))
        if img[x-1][y] == 0:
            #print "x-1",x+1,"y",y,img[x-1][y]
            connectComp.append((x-1,y))
        if img[x][y+1] == 0:
            #print "x",x,"y+1",y,img[x][y+1]
            connectComp.append((x,y+1))
        if img[x][y-1] == 0:
            #print "x",x,"y-1",y,img[x][y-1]
            connectComp.append((x,y-1))        
        else:
            #print (-1,-1)
            connectComp.append((-1,-1))        
        
    # Convert handwritten stroke into Spline
    
    def writeStroke(self):
        pnts =  [(p.x(),p.y()) for p in self.mainWindow.traceView.scene().pointList]
        
        self.writeStrokePnts(pnts)

    def writeStrokePnts(self,pnts):
        self.mainWindow.statusBar().showMessage("Converting to spline. Please wait...",1000000)
        
        pnts2 = pnts
        
        ndF,ndL = 0,0
        nodeF,nodeL = 0,0
        
        EdgeOverlap = []
        
        for ndA,ndB,bs in self.mainWindow.glyphView.scene().Edges:
            for ind, pnt in enumerate(bs.points):
                if util.dist(pnt,pnts[0]) < 5 and ind > 30 and ind < len(bs.points) - 30 :
                    cutPnt = bs.points.index(pnt)
                    EdgeOverlap.append((ndA,ndB,bs,pnt,bs.points[:cutPnt+1],bs.points[cutPnt:]))
                    
                    break
        
        if len(EdgeOverlap) > 0:
            print "Overlapped Edges are ", EdgeOverlap[0][0].label.toPlainText(), EdgeOverlap[0][1].label.toPlainText()
#            self.mainWindow.glyphView.scene().addNode(int(EdgeOverlap[0][2][0]),int(EdgeOverlap[0][2][1]))

            # Removing older Splines

            self.mainWindow.glyphView.scene().Edges.remove((EdgeOverlap[0][0],EdgeOverlap[0][1],EdgeOverlap[0][2]))
            self.mainWindow.glyphView.scene().removeNode(EdgeOverlap[0][0])
            self.mainWindow.glyphView.scene().removeNode(EdgeOverlap[0][1])
            self.mainWindow.glyphView.scene().removeSpline(EdgeOverlap[0][2])
            
            self.mainWindow.glyphView.scene().addNode(EdgeOverlap[0][2].points[0][0],EdgeOverlap[0][2].points[0][1])
            self.mainWindow.glyphView.scene().addNode(EdgeOverlap[0][3][0],EdgeOverlap[0][3][1])
            
            pnts = EdgeOverlap[0][4]
            
            cpx,cpy = self.getSplineInterimPoints(pnts) 
                
            NdB, NdA = self.mainWindow.glyphView.scene().Nodes[-1], self.mainWindow.glyphView.scene().Nodes[-2]    
            BS = BSpline(zip(cpx,cpy))
            self.mainWindow.glyphView.scene().addItem(BS)
            self.mainWindow.glyphView.scene().Edges.append((NdA,NdB,BS))

            self.mainWindow.glyphView.scene().addNode(EdgeOverlap[0][2].points[-1][0],EdgeOverlap[0][2].points[-1][1])
            
            pnts = EdgeOverlap[0][5]
            
            cpx,cpy = self.getSplineInterimPoints(pnts) 
                
            NdB, NdA = self.mainWindow.glyphView.scene().Nodes[-1], self.mainWindow.glyphView.scene().Nodes[-2]    
            BS = BSpline(zip(cpx,cpy))
            self.mainWindow.glyphView.scene().addItem(BS)   
            self.mainWindow.glyphView.scene().Edges.append((NdA,NdB,BS))         
            
        pnts = pnts2
                        
        for nodeF in self.mainWindow.glyphView.scene().Nodes:
            ndF = (nodeF.x(),nodeF.y())
            if util.dist(ndF,pnts[0]) < 10:
                pnts[0] = ndF
                #print "Found"
                break
                
        for nodeL in self.mainWindow.glyphView.scene().Nodes:
            ndL = (nodeL.x(),nodeL.y())            
            if util.dist(ndL,pnts[-1]) < 10:
                pnts[-1] = ndL
                #print "Fount"
                break
            
        cpx,cpy = self.getSplineInterimPoints(pnts)
            
        NdCh = False
        
        if pnts[0] != ndF and pnts[-1] != ndL:
            self.mainWindow.glyphView.scene().addNode(cpx[-1],cpy[-1])
            self.mainWindow.glyphView.scene().addNode(cpx[0],cpy[0])
            NdA, NdB = self.mainWindow.glyphView.scene().Nodes[-1], self.mainWindow.glyphView.scene().Nodes[-2]
        
        elif pnts[0] == ndF and pnts[-1] != ndL:
            self.mainWindow.glyphView.scene().addNode(cpx[-1],cpy[-1])
            NdB = self.mainWindow.glyphView.scene().Nodes[-1]
            NdA = nodeF
            
        elif pnts[0] != ndF and pnts[-1] == ndL:
            self.mainWindow.glyphView.scene().addNode(cpx[0],cpy[0])
            NdA = self.mainWindow.glyphView.scene().Nodes[-1]
            NdB = nodeF            
            
        elif pnts[-1] == ndL and pnts[0] == ndF:
            NdB = nodeL
            NdA = nodeF
                    
        BS = BSpline(zip(cpx,cpy))
        self.mainWindow.glyphView.scene().addItem(BS)
        self.mainWindow.glyphView.scene().Edges.append((NdA,NdB,BS))
                       
        self.mainWindow.traceView.setScene(traceScene(self))
        self.updateTraceView()
        
        self.write = True
        self.mainWindow.traceView.scene().pointList = []
        self.mainWindow.statusBar().showMessage("Spline conversion complete",30000)
        
        
    def getSplineInterimPoints(self,pnts):
        import imageProcess.sketchBeautification as sb

        if sb.checkShape(pnts) == 'line':
            print "Line"
            cpx,cpy = [pnts[0][0],(pnts[0][0]+pnts[-1][0])/float(2),pnts[-1][0]],[pnts[0][1],(pnts[0][1]+pnts[-1][1])/float(2),pnts[-1][1]]            
    
        else:
            cpPnts,tck = dg.reduceP(pnts,6) 
            if tck != None:
                cpx,cpy = util.coOrd(cpPnts,0), util.coOrd(cpPnts,1)
            else:
                print "Simplified Points less than 3"
                cpx,cpy = [pnts[0][0],(pnts[0][0]+pnts[-1][0])/float(2),pnts[-1][0]],[pnts[0][1],(pnts[0][1]+pnts[-1][1])/float(2),pnts[-1][1]]
            
        return (cpx,cpy)
    
    # Classify Strokes into disjoint and retraces
    def getStrokeClasses(self,penStroke):
        print "Extracting trace classes"
        
        trajectory= self.gl.getStrokePath(penStroke.split("->"))
        
        print trajectory
            
        strokes, disjointStrokes, retraceStrokes, juncPoint = [],[],[],[]
        
        j1,j2 = 0,0
        
        # Differentiating into disjoint Strokes - without disruption
        
        for i in range(len(trajectory)-1):
            if trajectory[i][1] != trajectory[i+1][0]:
                strokes.append((trajectory[j1:i+1]))
                j1 = i+1
                
            if set(trajectory[i]) == set(trajectory[i+1]):
                retraceStrokes.append((trajectory[i:i+2]))
                
            strokeA, strokeB = trajectory[i],trajectory[i+1]
            
            print strokeA,strokeB,self.gl.CostCurv(strokeA,strokeB)
            
            if set(strokeA)!=set(strokeB) and strokeA[1]==strokeB[0] and self.gl.CostCurv(strokeA,strokeB) >= 22.5:
                print "Disjoint Stokes Angle", strokeA, strokeB, self.gl.CostCurv(strokeA,strokeB)
                juncPoint.append(list(set([strokeA[0],strokeA[1]]) & set([strokeB[0],strokeB[1]]))[0])  
                print trajectory, j2, i+1       
                disjointStrokes.append(trajectory[j2:i+1])     
                j2= i+1
                
        strokes.append((trajectory[j1:]))
        disjointStrokes.append((trajectory[j2:]))
        
        ### Removing retraces from the disjoint strokes like :: Recheck
        
        print "Now disjoint strokes are", disjointStrokes
        
        #disjointActual = disjointStrokes[:]
        
        disjointActual = []
        
        retraceStrokesNew  =  []
        
        for strokes in disjointStrokes[:]:
            strokesNew = strokes[:]
            r  = []

            for ind, i in enumerate(range(len(strokes)-1)):
                if [strokes[i],strokes[i+1]] in retraceStrokes:
                    r.append(i+1)
                    retraceStrokesNew.append((strokes[i],strokes[i+1]))
#                    if ind == 0:
#                        r.append(i)
#                        strokesNew.remove(strokes[i])
#                        
#                    else:
#                        r.append(i+1)
#                        strokesNew.remove(strokes[i+1])
#                        retraceStrokesNew.append(strokes[i+1])
                        
                    #strokesNew.remove(strokes[i+1])
                    print "Removed:",strokes[i],strokes[i+1]
#                    try:
#                        disjointStrokes.remove(strokes)
#                    except ValueError:
#                        pass
            
            if len(r)  == 0:
                disjointActual.append(strokesNew)
            else:
                strokesN = []
                r= [0]+r+[len(strokes)]
                print "Breaking Points are",r
                for j in range(len(r)-1):
                    disjointActual.append(strokesNew[r[j]:r[j+1]])
                #disjointActual.append(strokesN)
                
            print "Added",strokesNew
         
        print "Disjoint Actual is", disjointActual
        
        #print strokes, disjointStrokes, retraceStrokes, juncPoint                        
        
        return strokes, disjointStrokes, disjointActual, retraceStrokesNew, juncPoint
            
    def strokeViewUpdate(self,retainCurvature=False):
        subStrokePoints = []
        
        if retainCurvature:
            for item in self.mainWindow.subStrokeView.scene().items():
            #print item
                if isinstance(item,QGraphicsEllipseItem):
                    subStrokePoints.append(item)
        
            curvPoints = [(node.scenePos().x(),node.scenePos().y()) for node in subStrokePoints]
            
        self.createGlyph()
        
        self.mainWindow.tabWidget.setCurrentIndex(1)
        
        self.mainWindow.strokeView.setScene(strokeScene())  
        self.mainWindow.subStrokeView.setScene(subStrokeScene())    
        
        self.penStrokes = self.mainWindow.rankTrajList.currentItem().text().split(" ")
        
        print "Pen Strokes", self.penStrokes
        
        #self.penStrokePoints = []
        
        strokes, disjointStrokes, disjointActual, retraceStrokes, juncPoint = [],[],[],[],[]
        
        self.penSubStrokes = []
        
        for penStroke in self.penStrokes:
            strokesL, disjointStrokesL, disjointActualL, retraceStrokesL, juncPointL = self.getStrokeClasses(penStroke)
            
            
            self.penSubStrokes.append(disjointActualL)
            
            strokes.extend(strokesL)
            disjointStrokes.extend(disjointActualL)
            disjointActual.extend(disjointStrokesL)
            retraceStrokes.extend(retraceStrokesL)
            juncPoint.extend(juncPointL)
            
        
        #print disjointStrokesL,disjointStrokes
        
        #disjointStrokes = util.UniqueLists(disjointStrokes)
        
        print "-------------------------------------------"    
        print "Strokes", strokes
        print "Disjoint Strokes", disjointStrokes
        print "Retrace Strokes",retraceStrokes
        print "Junction Points", juncPoint
        print "-------------------------------------------"
        
                
        self.drawBoundinBoxRotatedBox() #- Update this

#        self.mainWindow.tableWidget.setItem(1,0,QTableWidgetItem(str(len(disjointStrokes))))
#        self.mainWindow.tableWidget.setItem(2,0,QTableWidgetItem(str()))      
            
        # Fusing fluent strokes into a single contiguous path
        
        self.majorStrokePointList = []
        self.majorStrokePointListActual = []
        
        #print "The Disjoint Strokes are", util.UniqueLists(disjointStrokes)
        
        print "Pen disjoint Strokes are ", self.penSubStrokes
        print "Total disjoint stokres are", disjointStrokes
        
        
        for strokes in disjointStrokes:
            strokePoints = []
            print "Strokes", strokes
            for stroke in strokes:
                print "Substrokes", stroke
                interimPoints = self.getInterim(stroke)
                print "Substrokes", stroke, interimPoints
                strokePoints.extend(interimPoints[:-1])
                
            self.majorStrokePointList.append((strokes,strokePoints+[interimPoints[-1]]))          
            
        # Representing the contiguous path as splines
        
        self.majorStrokeSpline = []
        
        self.UpstrokeCnt = 0
        self.DownstrokeCnt  = 0      
        self.velocityInversion = 0
        
        self.updStrokes  = []
        self.upStrokes = []
        self.downStrokes = []        
        
        print "MajorStrokePointList are", self.majorStrokePointList
        
#        self.majorStrokePointListN = []
#        
#        for stroke,retrace,points in self.majorStrokePointList:
#            if len(retrace) == 0:
#                self.majorStrokePointListN.append(points)
#            else:
#                
#            elif retrace[0] == 1:
#               
#                self.majorStrokePointListN.append(self.getInterim(retrace[1]))
#                self.majorStrokePointListN.append(points)
#                
#            elif retrace[0] == 2:
#                print "retracePoints are 1", retrace[1],points
#                self.majorStrokePointListN.append(points)
#                self.majorStrokePointListN.append(self.getInterim(retrace[1]))                
#                
#        self.majorStrokePointList = self.majorStrokePointListN        
        
    
        for stroke,majorStrokePoints in self.majorStrokePointList: # ,retrace,majorStrokePoints
            subStrokePath = QGraphicsPathItem()
            strokePath = QGraphicsPathItem()

            BS1 = BSpline(majorStrokePoints)
            BS2 = BSpline(majorStrokePoints)
            
            strokePath.setPath(BS1.path)
            subStrokePath.setPath(BS2.path)  
            
            strokePath.setPen(QColor(self.colors.pop()))
            ### Fix Retraces ###
            #self.mainWindow.strokeView.scene().addItem(BS1)
            self.mainWindow.strokeView.scene().addItem(strokePath)                     
    
            subStrokePath.setPen(QColor("#000000"))   
            self.mainWindow.subStrokeView.scene().addItem(subStrokePath)
              
            crvPnts = self.getCurvature(BS1)
            
            crvPnts = util.conjoinLists(crvPnts, 20)
            
            self.majorStrokeSpline.append((BS1.tck,BS1.interimPoints,crvPnts))
            
            if not retainCurvature:
                if crvPnts != None:
                    for x,y in crvPnts:
                        self.mainWindow.subStrokeView.scene().drawNodes(x,y)     
                    
                    
        self.majorStrokeSplineActual  = []
        
        self.majorStrokePointList = [m[1] for m in self.majorStrokePointList] # if retraces in
        
        if retainCurvature:
            for x,y in curvPoints:
                self.mainWindow.subStrokeView.scene().drawNodes(x,y)                      
    #                    
    #            @@@@@ Classify Strokes for Straight Lines @@@@@@ TODO TODO 
                #self.classifyStrokes(BS1.tck)    
                      
        # Displaying Disjoint junction points in Glyph View
                
        self.junctionPoints = []
        
        print "~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~"
        print "Major Stroke Num", len(self.majorStrokeSpline)         
        print "~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~"
        
        for point in juncPoint:
            xC, yC = self.gl.G.node[point]['x'], self.gl.G.node[point]['y']
            self.junctionPoints.append((xC,yC))
            
            curvNode = QGraphicsEllipseItem(-4,-4,8,8)
            curvNode.setPos(xC,yC)
            curvNode.setBrush(QColor("#FFFFFF"))
            curvNode.setFlags(QGraphicsItem.ItemIsMovable | QGraphicsItem.ItemSendsGeometryChanges)     
            
            self.mainWindow.strokeView.scene().addItem(curvNode)


        self.penN = len(self.penStrokes)
        self.disjointN = len(disjointStrokes)
        self.retraceN = len(retraceStrokes)
        self.upstrokeN = self.UpstrokeCnt
        self.downstrokeN = self.DownstrokeCnt
                          
        #self.strokeNumFeat = { 'pen': len(self.penStrokes), 'disjoint' : len(disjointStrokes), 'retrace': len(retraceStrokes), 'up': self.UpstrokeCnt, 'down': self.DownstrokeCnt }

        
        #self.fillFeatures(self.strokeNumFeat)
        
        self.classifyStrokeActual()
                    
        return 
    
    def drawBoundingBox(self):
        xMax, xMin, yMin, yMax = self.gl.getBoundingBox()
        
        pen = QPen(QColor("#BFBFBF"))
        
        self.mainWindow.strokeView.scene().addLine(xMin, yMin, xMin, yMax, pen)
        self.mainWindow.strokeView.scene().addLine(xMax, yMin, xMax, yMax, pen)
        
        self.mainWindow.strokeView.scene().addLine(xMin, yMin, xMax, yMin, pen)
        self.mainWindow.strokeView.scene().addLine(xMin, yMax, xMax, yMax, pen)
        
    def drawBoundinBoxRotatedBox(self):
        
        return
        
        #im = cv2.ellipse(img,ellipse,(0,255,0),2)    
#        
#        cv2.imshow('Lines Detected',im)        
                
    
    def getPathfromSpline(self,spline,color='#000000'):
        path = QGraphicsPathItem()
        path.setPen(QColor(color))
        path.setPath(spline.path)
        
        return path
        
    def classifyStrokeActual(self):
        print "Item Changed 2"
        for item in self.mainWindow.subStrokeView.scene().items():
            if isinstance(item,QGraphicsPathItem):
                self.mainWindow.subStrokeView.scene().removeItem(item)
                
        subStrokePoints =[]
                
        for item in self.mainWindow.subStrokeView.scene().items():
            #print item
            if isinstance(item,QGraphicsEllipseItem):
                subStrokePoints.append(item)
                
        curvPoints = [(node.scenePos().x(),node.scenePos().y()) for node in subStrokePoints]
        
        self.log += time.asctime( time.localtime(time.time())) + "\n"
        self.log += "Analyzing Segementation with the following points\n"
        for x,y in curvPoints:
            self.log += str(x) + " , " + str(y) + "\n"
        
        self.log += "\n\n"    
        
        print self.log
        
        #### Make the above variable to change the slope            
                
        self.UpstrokeCnt,self.DownstrokeCnt = 0,0
        
        self.updStrokes  = []
        self.upStrokes = []
        self.downStrokes = []  
        self.subStrokesAll = []
        
        self.strokeStructure = []
            
        for i, spl in enumerate(self.majorStrokeSpline):
            tck, iP, crvPnts = spl
            strokesLocal = self.classifyStrokes(tck)
            self.strokeStructure.append((self.majorStrokePointList[i],strokesLocal))

        self.upstrokeN = self.UpstrokeCnt
        self.downstrokeN = self.DownstrokeCnt
        
        print "Upstroke counts are", self.UpstrokeCnt, self.DownstrokeCnt
            
        self.fillFeatures()
        
    def fillFeatures(self):
        # Stroke Numbers
        #print "Filling Features"
        
        for feat,value in self.strokeNumFeat.iteritems():
            self.mainWindow.strokeNumFeatTbl.setItem(self.strokeNumPos[feat],0,QTableWidgetItem(str(value)))
            
        # Geometric Features
        from metrics import metrics
        
        allPoints = self.getAllPoints()
        
        self.geoFeat = {}
        
        self.geoFeat['length'] = metrics.totalLength(self.majorStrokePointList) ## Length
        self.glyphDistFL = metrics.distFirstLastPoint(allPoints) ## distance between first and last points
        
        try:
            self.hullArea = metrics.convexHullArea(allPoints) ## Convex Hull Area
        except Exception:
            print "QHull error. Possibly QHull attempted on line"
        
        self.glyphArea = metrics.boundingArea(allPoints) ## Convex hull are or bounding area which to use
        
        print "GlyphArea is ", self.glyphArea
        
        k = [metrics.avgCurvature(strokes) for strokes in self.majorStrokePointList] ## Curvature
        pp = [metrics.Perpendicularity(strokes) for strokes in self.majorStrokePointList]
        
        ########### Ration of Up/Down
        
        self.upStrokeLength = sum(map(util.lengthPnts,self.upStrokes))
        self.downStrokeLength = sum(map(util.lengthPnts,self.downStrokes))   
        
        try:
            upDownRatio = float(self.upStrokeLength)/self.downStrokeLength
        except ZeroDivisionError:
            upDownRatio = -1  
            
        self.velocityInversion = metrics.velocityInversion(self.updStrokes)
        
        self.penStrokesPoints = self.getAllPoints(penStrokes=True)
        self.glyphPenMove = metrics.penMoveDistance(self.penStrokesPoints)
        
        self.majorLengths = [util.lengthPnts(stroke) for stroke in self.majorStrokePointList]
        self.strokeLengths = [util.lengthPnts(stroke) for stroke in self.subStrokesAll]
        
        ### Geometric Features
                
        self.geoFeat['length'] = self.geoFeat['length'] # 1
        self.geoFeat['divergence'] = self.glyphDistFL #2
        self.geoFeat['size'] = self.glyphArea #3
        self.geoFeat['LBIndex'] = metrics.breathIndex(allPoints) #4
        self.geoFeat['avgCurv'] = numpy.mean(k) #5
        self.geoFeat['compactness'] = float(self.geoFeat['length'])/self.glyphArea #6
        self.geoFeat['openness'] = float(self.glyphDistFL)/self.geoFeat['length'] #7
        self.geoFeat['descendancy'] = 0#metrics.Descendancy(self.mainWindow.traceView.scene().baseLines[1], allPoints) #8
        self.geoFeat['ascension'] = 0#metrics.Ascension(self.mainWindow.traceView.scene().baseLines[0], allPoints) #8
        self.geoFeat['circularity'] = metrics.circularity(allPoints) #9
        self.geoFeat['rectangularity'] = metrics.rectangularity(allPoints) #9
        
        print "GeoFeat is", self.geoFeat
        
        ### Production Features
        self.prodFeat = {}
        
        # Counts 5.1 
        self.prodFeat['penC'] = self.penN
        self.prodFeat['disjointC'] = self.disjointN
        self.prodFeat['primitiveC'] = self.upstrokeN +self.downstrokeN
        self.prodFeat['retraceC'] = self.retraceN
        self.prodFeat['upC'] =  self.upstrokeN
        self.prodFeat['downC'] = self.downstrokeN
        self.prodFeat['up'] =  float(self.upStrokeLength)
        self.prodFeat['down'] = float(self.downStrokeLength)
        
        self.prodFeat['majorLengths'] = self.majorLengths # 5.2
        self.prodFeat['strokeLengths'] = self.strokeLengths # 5.2
        
        self.prodFeat['changeability'] = upDownRatio #5.3
        
        self.prodFeat['disfluency'] = len(self.curvPoints) + (self.disjointN-1) + (self.penN-1) #5.4 #Perhaps?
        self.prodFeat['NIV'] = self.velocityInversion # 5,4
        
        self.prodFeat['entropy'] = metrics.Entropy(self.subStrokesAll) #5.5
        
        
        
        ### Metrics - 5.6 Ngram - Do it later
        
        self.prodFeat['disjointAngles'] = self.listDisjointAngle() # 5.7
        self.prodFeat['strokeAngles'] = self.listAllStrokeAngle() #5.7
        
        self.prodFeat['penDrag'] = self.glyphPenMove # Absolute ; so dividing my length? #5.8
        
        print "prodFeat is", self.geoFeat
        
        self.geoFeat['breadthIndex'] = metrics.breathIndex(allPoints) ## LBI
        self.geoFeat['compactness_1'] = float(self.geoFeat['length'])/self.glyphArea
        self.geoFeat['compactness_2'] = float(self.geoFeat['length'])/self.glyphDistFL
        self.geoFeat['openness_1'] = float(self.glyphDistFL)/self.glyphArea
        self.geoFeat['openness_2'] = float(self.glyphDistFL)/self.geoFeat['length']
        self.geoFeat['avgCurv'] = numpy.mean(k)
                
        self.geoFeat['twistedness'] = 0
        self.geoFeat['closure'] = 0
        self.geoFeat['curviness'] = 0
                
        self.geoFeat['eccentricity'] = metrics.eccentricity(allPoints)
        self.geoFeat['perpendicularity'] = numpy.mean(pp)
        
        for f,v in self.geoFeat.iteritems():
            print f,v
            
        self.mainWindow.geoFeatTbl.setItem(0, 0, QTableWidgetItem(str(self.geoFeat['breadthIndex'])))
        self.mainWindow.geoFeatTbl.setItem(1, 0, QTableWidgetItem(str(self.geoFeat['compactness_1'])))
        self.mainWindow.geoFeatTbl.setItem(2, 0, QTableWidgetItem(str(self.geoFeat['openness_1'])))
        self.mainWindow.geoFeatTbl.setItem(3, 0, QTableWidgetItem(str(self.geoFeat['avgCurv'])))
        
#        self.geoFeat['aspect'] = math.degrees(metrics.aspect(allPoints)) #### Perhaps the distance... from the baseLine:-/ : Where to put this ?        
        
        ## Stroke numbers
        
        self.strokeNumFeat['pen'] = self.penN ### Check
        self.strokeNumFeat['disjoint'] = self.disjointN
        self.strokeNumFeat['retrace'] = self.retraceN
        self.strokeNumFeat['up'] = self.upstrokeN
        self.strokeNumFeat['down'] = self.downstrokeN
        
        for f,v in self.strokeNumFeat.iteritems():
            print f,v

        #for feat,value in self.strokeNumFeat.iteritems():
            #self.mainWindow.strokeNumFeatTbl.setItem(self.strokeNumPos[feat],0,QTableWidgetItem(str(value)))  
            
        self.mainWindow.strokeNumFeatTbl.setItem(0, 0, QTableWidgetItem(str(self.strokeNumFeat['pen'])))
        self.mainWindow.strokeNumFeatTbl.setItem(1, 0,QTableWidgetItem( str(self.strokeNumFeat['disjoint'])))
        self.mainWindow.strokeNumFeatTbl.setItem(2, 0, QTableWidgetItem(str(self.strokeNumFeat['retrace'])))
        self.mainWindow.strokeNumFeatTbl.setItem(3, 0, QTableWidgetItem(str(self.strokeNumFeat['up'])))                          
        
        ## Product features
        
        #self.prodFeat = {}
        
        #self.prodFeat['entropy'] = metrics.Entropy(self.subStrokesAll)
        self.prodFeat['avgDirections'] = metrics.avgDirections(allPoints)
        #self.prodFeat['NIV'] = len(self.curvPoints) + (self.disjointN-1) + (self.penN-1)
        
        self.mainWindow.tableWidget_2.setItem(0, 0, QTableWidgetItem(str(self.prodFeat['disfluency'])))
        self.mainWindow.tableWidget_2.setItem(1, 0,QTableWidgetItem( str(self.prodFeat['entropy'])))
        self.mainWindow.tableWidget_2.setItem(2, 0, QTableWidgetItem(str(self.prodFeat['changeability'])))
        self.mainWindow.tableWidget_2.setItem(3, 0, QTableWidgetItem(str(self.prodFeat['strokeLengths'])))
        
        for f,v in self.prodFeat.iteritems():
            print f,v               
        
        ## Stroke property features
        
        self.upStrokeLength = sum(map(util.lengthPnts,self.upStrokes))
        self.downStrokeLength = sum(map(util.lengthPnts,self.downStrokes))
        
        #print sum(map(util.lengthPnts,self.upStrokes)), sum(map(util.lengthPnts,self.downStrokes)) 
        
        try:
            upDownRatio = float(self.upStrokeLength)/self.downStrokeLength
        except ZeroDivisionError:
            upDownRatio = -1        
            
        self.penStrokesPoints = self.getAllPoints(penStrokes=True)
        self.glyphPenMove = metrics.penMoveDistance(self.penStrokesPoints)            
        
        self.strokePropFeat = {}
        
        self.strokePropFeat['updown'] = upDownRatio
        self.strokePropFeat['pendrag'] = self.glyphPenMove/self.geoFeat['length'] # Absolute ; so dividing my length
        #self.strokePropFeat['descendancy'] = metrics.Descendancy(self.mainWindow.traceView.scene().baseLines[1], allPoints)
        #self.strokePropFeat['ascension'] = metrics.Ascension(self.mainWindow.traceView.scene().baseLines[0], allPoints)
        
        self.misc = {}
        
        self.misc['length'] = self.geoFeat['length']
        self.misc['fl'] = self.glyphDistFL
        self.misc['area'] = self.glyphArea
   
        self.mainWindow.strokePropFeatTbl.setItem(0, 0, QTableWidgetItem(str(self.initAngle())))
        self.mainWindow.strokePropFeatTbl.setItem(1, 0, QTableWidgetItem(str(self.majorAngle())))
        self.mainWindow.strokePropFeatTbl.setItem(2, 0, QTableWidgetItem(str(self.divergenceAngle())))
        self.mainWindow.strokePropFeatTbl.setItem(3, 0, QTableWidgetItem(str(self.listAllStrokeAngle())))
        
        for f,v in self.strokePropFeat.iteritems():
            print f,v        
        
        ### Cognitive Features
        
        self.cognFeat = {} 
                
        #self.cognFeat['minimumPoints'] = metrics.minimumPoints(self.penStrokesPoints)
                
        try:
            self.initialAngle = metrics.initialAngle(self.updStrokes[0][0])
        except Exception:
            pass
        
        self.mainWindow.strokePropFeatTbl.setItem(4, 0, QTableWidgetItem(str(self.initialAngle)))
        
        for f,v in self.cognFeat.iteritems():
            print f,v        
            
        #self.glyphCrossings = metrics.crossings(self.getAllPoints(invisibleStroke=False));
        
        self.glyphPenAngle = metrics.angleBetweenPenstrokes(self.penStrokesPoints)
        
        return    
        
        #print len(self.upStrokes), len(self.downStrokes)
        
        
        
        
        ### Inverted  V doesn't work 
        
     #   metrics.minimumPoints(self.penStrokesPoints)

        self.mainWindow.tableWidget_5.setItem(0, 0, QTableWidgetItem(str(metrics.minimumPoints(self.penStrokesPoints))))
        
        self.glyphCrossings = metrics.crossings(self.getAllPoints(invisibleStroke=False));
        
#        self.quadDist = metrics.getDirectionDist(allPoints)
#        
#        ### Calculating this for strokes.. instead of points !
#        
#        self.quadChange = metrics.getDirectionChange(allPoints)
#        
#        print "_____________________________________________________________________________"
#        
#        print self.quadDist
#        print self.quadChange
#        
#        print "_____________________________________________________________________________"
#        
        
        #self.quadChangeAct =  []
        
        #self.quadChangeAct.append(self.quadChange[0][0])
        
#        for i in range(len(self.quadChange)-1):
#            if self.quadChange[i][1] == self.quadChange[i+1][0] and self.quadChange[i][1]!=0 :
#                self.quadChangeAct.append(self.quadChange[i+1][0])
#            
#        for i in range(len(self.quadChangeAct[:])-1):
#            if self.quadChangeAct[i] == self.quadChangeAct[i+1]:
#                self.quadChangeAct[i] = -1
#                
#        self.quadChangeAct.append(self.quadChange[-1][1])
#                
#        print self.quadChangeAct 
#                
#        self.quadChangeAct = [e for e in self.quadChangeAct if e!=-1 and e!=0]
#        
#        if len(self.quadChangeAct) > 14:
#            self.quadChangeAct = self.quadChangeAct[:23]
#        
#        print self.quadChangeAct
        
        
        
        self.strokePropFeat = {'updown':str(self.upDownRatio),'NIV':str(self.velocityInversion),'pendrag':str(self.glyphPenMove)} 
        
        #print self.strokePropFeat
        
        for feature in self.features:
            for feat,value in getattr(self,feature+'Feat').iteritems():
                getattr(self.mainWindow,feature+'FeatTbl').setItem(getattr(self,feature+'Pos')[feat],0,QTableWidgetItem(str(value)))

#        

#        print "^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^"
#        print "Crossings", self.glyphCrossings
        
        #######################################################################
            
    def classifyStrokes(self,tck):
        substrokesLocal = []
        
        subStrokePoints = []
        
        for item in self.mainWindow.subStrokeView.scene().items():
            #print item
            if isinstance(item,QGraphicsEllipseItem):
                subStrokePoints.append(item)
        
        #### Make the above variable to change the slope
        
        self.curvPoints = [(node.scenePos().x(),node.scenePos().y()) for node in subStrokePoints]
        
        #print "****************Classifying Strokes********************"
        
        #print len(self.mainWindow.subStrokeView.scene().subStrokePoints), len(self.curvPoints), self.curvPoints
        
        uout = util.u_interval(5000)
        
        x,y = splev(uout,tck)
        
        strokePoints = zip(x,y)        
        
        strokeBreaks = sorted([0]+[self.getclosestpnt(strokePoints,point) for point in self.curvPoints if self.getclosestpnt(strokePoints,point) !=None ]+[len(strokePoints)-1])
        
        #print "StrokeBreaks", strokeBreaks
        
        subStrokeIndex = [(strokeBreaks[i],strokeBreaks[i+1]) for i in range(len(strokeBreaks)-1)]
        
        subStrokes = [strokePoints[index[0]:index[1]] for index in subStrokeIndex]
        
        #print "SubStrokes are", len(subStrokes)
        
        subStrokesNew = []
        
        subStrokesJoined = []
        
        #print subStrokes[0]
        
        subStrokesnotNull = [subStroke for subStroke in subStrokes if len(subStroke) > 0]
        
        print "Substroke Null",
        for substroke in subStrokesnotNull:
            print "Substroke", substroke[0],substroke[-1]
        
        j1 = 0
        j2 = 0
                
        # For Strokes without inflection points
        
        # TODO for straight like: left strokes as downstroeks (arms contracting), rightsrokes as upsrokes(arm expanding)
        if len(subStrokes) == 0 :
            subStrokes = [strokePoints]
                    
        for i,subStroke in enumerate(subStrokes[:]):
            #print i,"th Time"
            
            if len(subStroke) > 0:
                #print subStroke[0], subStroke[-1]
                dy = subStroke[0][1] - subStroke[-1][1]
                angle =  math.degrees(util.angle(subStroke[0], subStroke[-1]))
                
                
                if angle > 0:
                    angle = 90 - angle
                else:
                    angle = 90 + angle
                    
                downC = False
                
                #print "Stroke Angle ", angle, 
                    
                if dy < 0:
                    if angle > 0:
                        if angle >=0 and angle <= 60:
                            downC = True
                    else:
                        if angle >=0 and angle <=60:
                            downC = True
                    
                #print "Stroke Angle ", angle, 
                
                print "Loop Stroke", subStroke[0], subStroke[-1]
                
                if not downC: #subStroke[0][1] - subStroke[-1][1] > 0:
                    #print "Found Upstroke"
                    self.UpstrokeCnt += 1
                    self.upStrokes.append(subStroke)
                    self.mainWindow.subStrokeView.scene().addItem(self.returnPath(subStroke,"#FE2E2E"))                
                    subStrokesNew.append((subStroke,"1"))
                    
                    self.updStrokes.append((subStroke,1))
                    substrokesLocal.append(subStroke)
                    self.subStrokesAll.append(subStroke)
                    
                #else:
                if downC: 
                    #print "Downstroke"
                    self.DownstrokeCnt += 1
                    self.downStrokes.append(subStroke)
                    self.mainWindow.subStrokeView.scene().addItem(self.returnPath(subStroke,"#01DF01"))                
                    subStrokesNew.append((subStroke,"0"))
                    
                    self.updStrokes.append((subStroke,0))
                    substrokesLocal.append(subStroke)
                    self.subStrokesAll.append(subStroke)
                    
                    
        return substrokesLocal
                    
        
        #print "Assigning Substrokes"
        
        #self.subStrokes = [subStroke for subStroke in subStrokes if len(subStroke) > 0]
                
        #print "Stroke Count", len(self.upStrokes), len(self.downStrokes)
#                pnt = subStrokesNew[i][0][-1]
#                self.mainWindow.subStrokeView.scene().drawNodes(pnt[0],pnt[1],color="#000000")
#                
#        self.mainWindow.tableWidget.setItem(3,0,QTableWidgetItem(str((self.UpstrokeCnt))))
#        self.mainWindow.tableWidget.setItem(4,0,QTableWidgetItem(str((self.DownstrokeCnt))))


                
    def initAngle(self):
        #print self.subStrokes
        
        print "Initial Angle"
        
        for substroke in self.subStrokesAll:
            print "substroke", substroke[1],substroke[-1]
        
        
        p1,p2 = self.subStrokesAll[0][1],self.subStrokesAll[0][-1]
        x1,y1 = p1
        x2,y2 = p2
        ang = util.angle(p1,p2)
        
        #print p1,p2,math.degrees(ang)
        
        if x1 == x2 and y1 > y2:
            return abs(ang)
        elif x1 == x2 and y2 > y1:
            return abs(ang) +(math.pi)
        elif y1 == y2 and x2 > x1:
            return abs(ang)
        elif y1 == y2 and x1 > x2:
            return abs(ang) +(math.pi)
        elif y1 > y2 and x2 > x1:
            return abs(ang)
        elif y1 > y2 and x1 > x2:
            return (math.pi)-abs(ang)
        elif y2 > y1 and x2 > x1:
            return (2*math.pi)-abs(ang)
        elif y2 >y1 and x1 >x2:
            return (math.pi+abs(ang))
        

    def majorAngle(self):
        #print self.subStrokes
        
        #print "here"
        
        majorStroke = sorted([(util.dist(stroke[0],stroke[-1]),stroke) for stroke in self.subStrokesAll],reverse=True)[0][1]
        
        #print majorStroke    
        
        p1,p2 = majorStroke[0],majorStroke[-1]
        x1,y1 = p1
        x2,y2 = p2
        ang = util.angle(p1,p2)
        
        #print p1,p2,math.degrees(ang)
        
        if x1 == x2 and y1 > y2:
            return abs(ang)
        elif x1 == x2 and y2 > y1:
            return abs(ang) +(math.pi)
        elif y1 == y2 and x2 > x1:
            return abs(ang)
        elif y1 == y2 and x1 > x2:
            return abs(ang) +(math.pi)
        elif y1 > y2 and x2 > x1:
            return abs(ang)
        elif y1 > y2 and x1 > x2:
            return (math.pi)-abs(ang)
        elif y2 > y1 and x2 > x1:
            return (2*math.pi)-abs(ang)
        elif y2 >y1 and x1 >x2:
            return (math.pi+abs(ang))
        
        #print "Direction code", self.directionCodes()
        
    def divergenceAngle(self):
        allPoints = self.getAllPoints()
        
        p1,p2 = allPoints[0],allPoints[-1]
        x1,y1 = p1
        x2,y2 = p2
        ang = util.angle(p1,p2)
        
        #print p1,p2,math.degrees(ang)
        
        if x1 == x2 and y1 > y2:
            return abs(ang)
        elif x1 == x2 and y2 > y1:
            return abs(ang) +(math.pi)
        elif y1 == y2 and x2 > x1:
            return abs(ang)
        elif y1 == y2 and x1 > x2:
            return abs(ang) +(math.pi)
        elif y1 > y2 and x2 > x1:
            return abs(ang)
        elif y1 > y2 and x1 > x2:
            return (math.pi)-abs(ang)
        elif y2 > y1 and x2 > x1:
            return (2*math.pi)-abs(ang)
        elif y2 >y1 and x1 >x2:
            return (math.pi+abs(ang))    
        
        
    def listDisjointAngle(self):
        #print self.strokeStructure
        #print "Major Strokes"
#        for i,m in enumerate(self.strokeStructure):
#            print i
#            print m[0]
#            print len(m[1])
            
        self.listAngles = []
        
        penStrNum =  [0] + list(numpy.cumsum(map(len,self.penSubStrokes)))
        
        print "penStrNum", penStrNum
        
        penStrokes = [self.strokeStructure[penStrNum[i]:penStrNum[i+1]] for i in range(len(penStrNum)-1)]
        
        for penStroke in penStrokes:
            for i in range(len(penStroke)-1):
                
                self.listAngles.append(util.angleStrokes(penStroke[i][1][-1],penStroke[i+1][1][0]))
        
        #self.listAngles = [util.angleStrokes(self.majorStrokePointList[i],self.majorStrokePointList[i+1]) for i in range(len(self.majorStrokePointList)-1)]            
        
        return self.listAngles          
    
    def listAllStrokeAngle(self):
        self.listAngles = []
        
        penStrNum =  [0] + list(numpy.cumsum(map(len,self.penSubStrokes)))
        
        penStrokes = [self.strokeStructure[penStrNum[i]:penStrNum[i+1]] for i in range(len(penStrNum)-1)]

        for penStroke in penStrokes:
            penStrokesD = []
            for stroke in penStroke:
                penStrokesD.extend(stroke[1])
            
            for i,ps in enumerate(penStrokesD):
                print i,ps[0:5]
            
            for i in range(len(penStrokesD)-1):
                self.listAngles.append(util.angleStrokes(penStrokesD[i],penStrokesD[i+1]))
        
        #self.listAngles = [util.angleStrokes(self.subStrokesAll[i],self.subStrokesAll[i+1]) for i in range(len(self.subStrokesAll)-1)]
        
        return self.listAngles          
        
    def directionAngle(self):
        #print "Then number of subStrokes are", self.subStrokesAll
        dirCode = [util.directionCodes(stroke) for stroke in self.subStrokesAll]
        
        #print "Direction Code", dirCode
        
        return dirCode
        
    def returnPath(self,points,color="#000000"):
        path = QPainterPath()
        seg = QPolygonF([QPointF(x, y) for x, y in points])
        path.addPolygon(seg)
        
        pathItem = QGraphicsPathItem()
        pathItem.setPen(QColor(color))
        pathItem.setPath(path)
        
        return pathItem        
    
    def getLocalMax(self,curv,kGlob):
        maxx = []
        kMax = []
        iMax =  []
        
        k = numpy.mean([c[1] for c in curv])
        
        for i in range(1,len(curv)-1):
            if curv[i][1] > curv[i+1][1] and curv[i][1] > curv[i-1][1] and curv[i][1] > k and curv[i][1] > kGlob :
                #print "Inside"
                maxx.append(curv[i][0])
                iMax.append(i)
                kMax.append((curv[i][1]))
                    
        #print "local Maximum", maxx
        
        fused = (maxx,kMax,iMax)
        
        fus = zip(maxx,kMax,iMax)
        
        #print "fus", fus
        
        i = 0
        j = 0
        
        nearest = []
        indv = []
        near = []
        
        print "List of Local Maxes are", fus
        
        fus =  [f for f in fus if f[1] > 0.003] ### Curvature Threshold
        fus.append((0,0,0))
        
        print "List of Local Maxes - thresholded -  are", fus
        
        while i < len(fus)-1:
            #print "Inside While Loop", near
            if abs(fus[i][0] - fus [i+1][0]) < 0.2: # Change threshold if im,porting images
                #print "Inside If"
                #print "Comparing", fus[i][0], fus[i+1][0]
                near.append(fus[i][0])
            else:
                #print "Else Loop"
                near.append(fus[i][0])
                if len(near) > 0:
                    #print "mean", near, numpy.mean(near)
                    nearest.append(numpy.mean(near))
                    near = []
            i += 1
            
        if len(fus) == 2 and len(nearest) == 0:
            #print "I am here"
            #print fus
            nearest.append(fus[0][0])
            
            
        #print nearest
                    
        return nearest
        
    def getLocalMin(self,curv):
        minn = []
        for i in range(1,len(curv)-1):
            if curv[i][1] < curv[i+1][1] and curv[i][1] < curv[i-1][1]:
                minn.append(curv[i][0])
                    
        #print "local Minimum", minn
        
        return minn     
    
    def getclosest(self,ls,nm):
        dif = sorted([(abs(float(l) - nm),i) for i,l in enumerate(ls)])
        return dif[0][1]
    
    def getclosestpnt(self,ls,nm):
        dif = sorted([(util.dist(l,nm),l,i) for i,l in enumerate(ls)])
        #print "Diff", dif
        
        #print "Closest of", nm, "is", dif[0][1]
        
        if dif[0][0] < 3:
            return dif[0][2]
        else:
            return
    
    ### Look into this: http://dsp.stackexchange.com/questions/9631/removing-unwanted-peaks-from-signal
    ### Median filtering and other filters :-/
    ### Peak detection python  - numpy
    
    def getCurvature(self,bs):
        #print "****** Finding Curvature Points ***************"
        
        tck = bs.tck
        
        ### If line, there is  no point of curvature return empty array
        
        #print "Trying to fit a line"
        
        interimPoints = map(util.getXY,bs.interimPoints)
        X, Y = util.coOrd(interimPoints,0), util.coOrd(interimPoints,1)
        
        if(util.checkLine(X,Y)):
            print "Checking Here"
            #print "This is a line"
            return []
        
        if(util.checkCircle(X,Y,2)):
            xMax, xMin, yMax, yMin = max(X), min(X), max(Y), min(Y)
            
            idealRad = numpy.mean([(xMax-xMin),(yMax-yMin)])
            
#            ell = QGraphicsEllipseItem(xMin,yMin,idealRad,idealRad)
#            ell.setPen(QPen("#000000"))
#            self.mainWindow.subStrokeView.scene().addItem(ell)
#            
            print "This is a Circle"
            
            uout = util.u_interval(5000)
            x,y = splev(uout,tck)
            
            yDel = [(y[i]-y[i+1])/abs(y[i]-y[i+1]) for i in range(len(y)-1)]
            uExtr = [uout[i] for i in range(len(yDel)-1) if yDel[i] != yDel[i+1]]
            
            xC,yC = splev(uExtr,tck)
            
            return zip(xC,yC)
            
        
        ### Check if its a circle / Ellipse
        
        ### Have no curvature :-/ ?
        
        #### <<< Write Code here !!!!! to check if it is circle or not >>
        
        ### Find Curvature 
                
        uout = util.u_interval(5000)
        
        t = list(tck[0])[:1] + list(tck[0])[3:-2]
        #t = t[:1]+t[3:-2]
        
        tInterval = [(t[i],t[i+1]) for i in range(len(t)-1)]
        
        #print "*** Uout Blocks *** for each subcurve"
        
        #print "t subcurves", t
        
        kAll = []
        
        dx,dy = splev(uout,tck,der=1)
        d2x,d2y = splev(uout,tck,der=2)
        
        slope = [yd/yx for yd,yx in zip(dx,dy)]
        
        kA = abs(((dx*d2y) - (dy*d2x))) / (dx**2 + dy**2)**1.5
        #kold = k
        
        knum2 = zip(uout,kA)
        
        uExtr  = []
        
        #print "=========================================="        
    
        for u0,un in tInterval:
            uoutB = uout[self.getclosest(uout,u0):self.getclosest(uout,un)+1]
            
            k = util.calcCurvature(uoutB, tck)
            #kAll.extend(k)
            
            #print "From", u0, "to", un
            
            #print "Average K", numpy.mean(k), ":", numpy.mean(kA)
            
            #if numpy.mean(k) >= numpy.mean(kA):
            
                #kAll.extend(k)
                
            knum = zip(uoutB,k)
            
            lm = self.getLocalMax(knum,numpy.mean(kA))
            
            #print "LocalMax", lm , "Mean", numpy.mean(kA)
            
            uExtr += lm
            #print "Found Local Maxima", lm
            print 
            print
                
        print len(tInterval), len(uExtr)

        #print "Extrema", uExtr
            
        #print "=========================================="

        #uExtr = self.getLocalMax(knum2)
        

        # http://stackoverflow.com/questions/13590989/peak-curvature-in-scipy-spline
        
#        cl= self.colorsd.pop()
        
        #pylab.plot(kA,cl)
                
        
#        for u in t:
#            pylab.axvline(self.getclosest(uout,u))
            
        #pylab.axhline(numpy.mean(kA),0,500,cl)
        
#        pylab.plot(uExtr[2],uExtr[1],'bo')
#        pylab.show()
        
        x,y = splev(uout,tck)
        
        xd = [x[i]-x[i+1] for i in range(499)]
        yd = [y[i]-y[i+1] for i in range(499)]
        
        xZero = [(x[i],y[i]) for i in range(498) if (xd[i] > 0 and xd[i+1] < 0) or (xd[i] < 0 and xd[i+1] > 0) ]
        yZero = [(x[i],y[i]) for i in range(498) if (yd[i] > 0 and yd[i+1] < 0) or (yd[i] < 0 and yd[i+1] > 0) ]
        
        print xZero
        print yZero
#        
#        
#        pylab.plot(xd,'go')
#        pylab.plot(yd,'ro')
        
        #pylab.show()
        
        if len(uExtr) !=0:
        
            xC,yC = splev(uExtr,tck)
        #return xZero+yZero
        else:
            return None
        
        return zip(xC,yC)


    # Fix Zoom View
    def zoomView(self):
        changeScale = float(self.mainWindow.zoomSpin.value())/100
        self.mainWindow.glyphView.scale(changeScale,changeScale)
        self.mainWindow.traceView.scale(changeScale,changeScale)
        
              
    def clearScene(self):   
        self.mainWindow.glyphView.setScene(glyphScene(self))
        self.mainWindow.traceView.setScene(traceScene(self))
        self.mainWindow.strokeView.setScene(strokeScene())  
        self.mainWindow.subStrokeView.setScene(subStrokeScene())        
        
        self.mainWindow.singleTrajList.clear()
        self.mainWindow.multiTrajList.clear()
        self.mainWindow.rankTrajList.clear()
        
    def createGlyph(self):
        edgs = [(u.label.toPlainText(),v.label.toPlainText(),{'bs':w}) for u,v,w in self.mainWindow.glyphView.scene().Edges]
        spl = [w for u,v,w in self.mainWindow.glyphView.scene().Edges]
        
        if self.mainWindow.L2RCheck.isChecked():
            L2R = True
        if self.mainWindow.R2LCheck.isChecked():
            L2R = False
        
        if self.mainWindow.T2BCheck.isChecked():
            T2B = True
        if self.mainWindow.B2TCheck.isChecked():
            T2B = False
            
        ScriptDir = (L2R,T2B)
        retrace = self.mainWindow.retraceCheck.isChecked()
        
        heuristic = (ScriptDir, retrace)
        
        self.gl = CG.Glyph("glyph",edgs,heuristic)
        
        self.trajdir ={}
        
        for ed in edgs:
            for edg in self.gl.G.edges():
                if tuple([ed[0],ed[1]]) == tuple([edg[0],edg[1]]):
                    self.trajdir[(edg[0],edg[1])] = True
                elif tuple(sorted([ed[0],ed[1]])) == tuple(sorted([edg[0],edg[1]])):
                    self.trajdir[(edg[0],edg[1])] = False
                            
        for num, nod in enumerate(self.gl.G.nodes()):
            for nd in self.mainWindow.glyphView.scene().Nodes:
                if nd.label.toPlainText() == nod:
                    self.gl.G.node[nod] = {'x': nd.scenePos().x(), 'y': nd.scenePos().y()}
        
        
    def generateTrajectory(self):
        self.mainWindow.statusBar().showMessage("Generating Trajectory",1000000)
        
        self.createGlyph()
                                        
        self.mainWindow.singleTrajList.clear()
        self.mainWindow.multiTrajList.clear()
        self.mainWindow.rankTrajList.clear()
        
        import networkx as nx
        
        if len(nx.connected_components(self.gl.G)) > 1:
            #print "Contains more that two components", nx.connected_components(self.gl.G)
            Shortest = ['edit-path']
        else:
            Shortest  = self.gl.GetShortestTrajectory(self.mainWindow.minLengthCheck.isChecked(),self.mainWindow.minCurveCheck.isChecked(),self.mainWindow.dirCheck.isChecked())
        
        self.mainWindow.singleTrajLCD.display(len(Shortest))
        
        for num, path in enumerate(Shortest):
            #p = [(path[i], path[i + 1]) for i in range(len(path) - 1)]
            #print p
            
            self.mainWindow.singleTrajList.addItem("->".join(path)) 
#            self.mainWindow.multiTrajList.addItem("->".join(path))    
            self.mainWindow.rankTrajList.addItem("->".join(path))   
            
#            self.mainWindow.singleTrajList.addItem("->".join(path)) 
#            self.mainWindow.multiTrajList.addItem("->".join(path))    
#            self.mainWindow.rankTrajList.addItem("->".join(path))             
            
#        MultiPath = list(self.gl.GetTrajectoryMulti())
#        
#        print "Multipath"
#        
#        for path in MultiPath:   
#            print path
#            self.mainWindow.multiTrajList.addItem("->".join(path))    
#            self.mainWindow.rankTrajList.addItem("->".join(path))    
#
#            
#        MultiPath2 =self.gl.GetTrajectoryMulti2()
#        
#        print "Multipath 2"
#        
#        for path in MultiPath2:   
#            print path
#            self.mainWindow.multiTrajList.addItem("->".join(path))    
#            self.mainWindow.rankTrajList.addItem("->".join(path))                

#
#        self.mainWindow.multiTrajLCD.display(len(MultiPath+MultiPath2)) 
#        self.mainWindow.rankTrajLCD.display(len(MultiPath+MultiPath2)+(len(Shortest)))
        
        self.mainWindow.statusBar().showMessage("Trajectory Generated",20000)
#        
        
    def updateTraceView(self):
        for spline in self.mainWindow.traceView.scene().items(): 
            if isinstance(spline,QGraphicsPathItem):
                self.mainWindow.traceView.scene().removeItem(spline)
                
        self.splines = []
            
        for spline in self.mainWindow.glyphView.scene().items():
            if isinstance(spline,BSpline):
                self.splines.append(copy.copy(spline))
                self.mainWindow.traceView.scene().addItem(copy.copy(spline))
                
    def selectFile(self):
        fileName = QFileDialog.getOpenFileName(self.mainWindow,"Open File", "C:\Users\Administrator\Dropbox\Evaluation Documents\images")
        self.mainWindow.glyphView.scene().addImage(fileName)
    
    def zoomin(self):
        self.viewGlyph.zoomIn()
        self.viewStroke.zoomIn()

    def zoomout(self):
        self.viewGlyph.zoomOut()
        self.viewStroke.zoomOut()
        
        
    def getStaticPoints(self):
        allPoints = self.getAllPoints(invisibleStroke=False)
        
        allPoints.sort()
            
        return allPoints
        
        
    def getAllPoints(self,penStrokes=False,invisibleStroke=True): #penStrokes gives different array of points not a single contiguous array
                                             # (A->B B-C) => Two arrays [points of a to b] [points of b-c]
                                             # if false => Singgle [points of a to b, points of b-c] 
        allPoints = []
        #print "definitely here 23"
        
        self.penStrokes = self.mainWindow.rankTrajList.currentItem().text().split(" ")
        
        for i,penStroke in enumerate(self.penStrokes):
            traj = self.gl.getStrokePath(penStroke.split("->"))
            
            # List points forming the Trajectory 
            points = list(itertools.chain(*[self.getPath(edges) for edges in traj]))
            if not penStrokes:
                if not invisibleStroke:
         #           print "here 2"
                    allPoints.extend(points)
                else:
          #          print i
           #         print "here 3"
                    if i > 0:
                        x1,y1,x2,y2 = (allPoints[-1])[0], (allPoints[-1])[1], (list(points)[0])[0], (list(points)[0])[1]
                        pointsLine = util.get_line(x1,y1,x2,y2)
                        allPoints.extend(pointsLine)
                        allPoints.extend(points)
                    else:
            #            print "here 4"
                        allPoints.extend(points)
            else:
             #   print "not here"
                allPoints.append(list(points))        
        
        return allPoints
    
    
    def logTrajectory(self,current):
        if(self.trajClicked and self.trajprev != current.text()):
            print "Old", self.trajprev
            print "changed", current.text()
            self.log += time.asctime( time.localtime(time.time())) + "\n"
            self.log += "Trajectory Change\n"
            self.log += "From: " + self.trajprev + " To: " + current.text() + "\n\n"
            self.trajClicked = False
  
        
    def editTrajectory(self):
        prev =  self.mainWindow.rankTrajList.currentItem().text()
        
        item = self.mainWindow.rankTrajList.currentItem()
        item.setFlags(item.flags() | Qt.ItemIsEditable)
        self.mainWindow.rankTrajList.editItem(item)
        
        self.trajClicked = True
        
        self.trajprev = self.mainWindow.rankTrajList.currentItem().text()
        
#        print prev,now
        
        
        
        #item = self.mainWindow.multiTrajList.currentItem()
        #item.setFlags(item.flags() | Qt.ItemIsEditable)
        #self.mainWindow.multiTrajList.editItem(item)
                
        #item = self.mainWindow.singleTrajList.currentItem()
        #item.setFlags(item.flags() | Qt.ItemIsEditable)
        #self.mainWindow.singleTrajList.editItem(item)                
                
    def dispTrajectory(self):        
        TD.DispTrajectory(self.getAllPoints(),(0, 0, 255))
        
    # Return the points that form the shape of the Glyph
    def shapeDump(self,sceneGlyph):
        splinePoints = []
        
        for spline in sceneGlyph.items():
            if isinstance(spline,QGraphicsPathItem):
                splinePoints.append(spline.points)
                
        return splinePoints
    
    # Return contents of the screen in String    
    def glyphDump(self,sceneGlyph):
        print sceneGlyph.Nodes
        dumpNodes = [(nd.x(),nd.y()) for nd in sceneGlyph.Nodes]
                    
        dumpBS = [((nst.label.toPlainText(),nst.x(),nst.y()),(nend.label.toPlainText(),nend.x(),nend.y()), map(util.getXY,bs.interimPoints)) for nst,nend,bs in sceneGlyph.Edges]
        
        dumpTrajRnk = [self.mainWindow.rankTrajList.item(i).text() for i in range(self.mainWindow.rankTrajList.count())]
        
        dumpGlyph = {}
        
        dumpGlyph['nodes'] = pickle.dumps(dumpNodes,-1)
        dumpGlyph['bsplines'] = pickle.dumps(dumpBS,-1)
        dumpGlyph['traj'] = pickle.dumps(dumpTrajRnk,-1)
        
        self.glyphTxt = self.mainWindow.glyphIDTxt.text()
        
        self.baseLines = self.mainWindow.traceView.scene().baseLines

        listVariables = ['log','penSubStrokes','penN','disjointN','retraceN','upstrokeN','downstrokeN','prodFeat','baseLines','subStrokesAllA','majorStrokePointListActual','subStrokesAll','glyphTxt','strokeNumFeat','majorStrokePointList','junctionPoints','updStrokes','curvPoints','geoFeat', 'quadDist','quadChange','majorStrokeSpline','strokePropFeat']
        
        for var in listVariables:
            try:
                dumpGlyph[var] = getattr(self,var)
            except AttributeError:
                pass
                    
        return dumpGlyph
    
    # Save Glyph to a file
    def saveGlyph(self):
        saveGlyphName = QFileDialog.getSaveFileName(self.mainWindow, "Save Glyph", "C:\Users\Administrator\Documents\Glyph Files")
        pickle.dump(self.glyphDump(self.mainWindow.glyphView.scene()),open(saveGlyphName[0],"wb"),-1)
        
        self.mainWindow.statusBar().showMessage("Glyph Saved",30000)

    ## Just create the scene from the saved Glyph
    def loadGlyphScene(self, dumpGlyph, sceneGlyph):
        dumpNodes, dumpBS  = pickle.loads(dumpGlyph['nodes']), pickle.loads(dumpGlyph['bsplines'])
                
        for x,y in dumpNodes:
            sceneGlyph.addNode(x,y)
        
        for nodeS,nodeE,bsInt in dumpBS:
            nS = NodePoint(nodeS[0],nodeS[1],nodeS[2],parent=sceneGlyph)
            nE = NodePoint(nodeE[0],nodeE[1],nodeE[2],parent=sceneGlyph)
            
            sceneGlyph.addBSpline(bsInt,nS,nE)
            
        self.createGlyph()
                        
        return sceneGlyph
    
    # Opening glyph from a file
    def loadGlyph(self):
        self.mainWindow.statusBar().showMessage("Loading Glyph... Please wait...",300000)
        
        self.loadGlyphName = QFileDialog.getOpenFileName(self.mainWindow, "Open Glyph", "C:\Users\Administrator\Documents\Glyph Files")
        dumpGlyph = pickle.load(open(self.loadGlyphName[0],"rb"))
        
        self.loadGlyphString(dumpGlyph)
    
    def loadGlyphString(self,dumpGlyph):
        
        self.clearScene()
        self.mainWindow.glyphView.setScene(self.loadGlyphScene(dumpGlyph, self.mainWindow.glyphView.scene()))
        
        #setattr(self,'glyphTxt',dumpGlyph['glyphTxt'])  ### Just for survey
        #return ### Just for survey
        
        self.updateTraceView()
        
        ## if len(>  3)
        
        items = []
                
        if len(dumpGlyph) >= 3:
            for item in pickle.loads(dumpGlyph['traj']):
                self.mainWindow.rankTrajList.addItem(item)    
                
        self.mainWindow.rankTrajList.setCurrentRow(0)        

        listVariables = ['log','penSubStrokes','penN','disjointN','retraceN','upstrokeN','downstrokeN','prodFeat','baseLines','subStrokesAllA','majorStrokePointListActual','subStrokesAll','glyphTxt','strokeNumFeat','majorStrokePointList','junctionPoints','updStrokes','curvPoints','geoFeat','quadDist','quadChange','majorStrokeSpline','strokePropFeat','']
        
        for var in listVariables:
            try:
                setattr(self,var,dumpGlyph[var])
                #print var, "saved"
            except Exception:
                pass
            
        try:
            for i,feat in enumerate(self.strokeNumFeat.iteritems()):
                try:
                    self.mainWindow.strokeNumFeatTbl.setItem(i,0,QTableWidgetItem(str(feat[1])))
                except Exception:
                    pass  
        except Exception:
            pass              
            
        try:            
            for i,feat in enumerate(self.geoFeat.iteritems()):
                try:            
                    self.mainWindow.geoFeatTbl.setItem(i,0,QTableWidgetItem(str(feat[1])))    
                except Exception:
                    pass   
        except Exception:
            pass
        
        try:
            for feature in self.features:
                    feat,value = feature
                    getattr(self.mainWindow,feature+'FeatTbl').setItem(getattr(self,feature+'Pos')[feat],0,QTableWidgetItem(str(value)))   
        except Exception:
            pass     
        
        try:
            for strokes in self.majorStrokePointList:
                self.mainWindow.strokeView.scene().addItem(self.getPathfromSpline(BSpline(strokes),self.colors.pop()))
        except Exception:
            pass                
            
        try:
            for x,y in self.junctionPoints:
                curvNode = QGraphicsEllipseItem(-4,-4,8,8)
                curvNode.setPos(x,y)
                curvNode.setBrush(QColor("#FFFFFF"))
                curvNode.setFlags(QGraphicsItem.ItemIsMovable | QGraphicsItem.ItemSendsGeometryChanges)  
                
                self.mainWindow.strokeView.scene().addItem(curvNode)
        except Exception:
            pass                   
                   
        try: 
            for strokes,type in self.updStrokes:
                if type == 0:
                    self.mainWindow.subStrokeView.scene().addItem(self.returnPath(strokes,'#FE2E2E'))
                else:
                    self.mainWindow.subStrokeView.scene().addItem(self.returnPath(strokes,'#01DF01'))
        except Exception:
            pass   
        
        try:                        
            for x,y in self.curvPoints:
                curvNode = QGraphicsEllipseItem(-4,-4,8,8)
                curvNode.setPos(x,y)
                curvNode.setBrush(QColor("#FFFFFF"))
                curvNode.setFlags(QGraphicsItem.ItemIsMovable | QGraphicsItem.ItemSendsGeometryChanges)  
                
                self.mainWindow.subStrokeView.scene().addItem(curvNode)
        except Exception:
            pass   
        try:
            self.mainWindow.glyphIDTxt.insert(self.glyphTxt)
        except Exception:
            pass
        
        try:
            self.mainWindow.traceView.scene().baseLines = self.baseLines
            for y in self.baseLines:
                #print "Baselines", y
                
                self.mainWindow.traceView.scene().addLine(0, y, self.width(), y, QPen(QColor('#FF0000')))
        except Exception:
            print "Baselines don't exist"
            pass
            
        self.mainWindow.statusBar().showMessage("Glyph Loaded",20000)       
            
    # Getting the Path points of the Spline in the correct order                
    def getPath(self,stroke):
        for ed in self.gl.G.edges(data=True):
            if tuple([ed[0],ed[1]]) == tuple(stroke):
                pnt =  ed[2]['bs'].points
                dirtj = True and self.trajdir[tuple([ed[0],ed[1]])]
            elif tuple(sorted([ed[0],ed[1]])) == tuple(sorted(stroke)):
                pnt =  ed[2]['bs'].points           
                dirtj = True and not self.trajdir[tuple([ed[0],ed[1]])]
                        
        if dirtj:
            return pnt
        else:
            return list(reversed(pnt[:])) 
        
    # Getting the Interim Points of the splines in the correct order     
    def getInterim(self,stroke):
        for ed in self.gl.G.edges(data=True):
            if tuple([ed[0],ed[1]]) == tuple(stroke):
                pnt =  map(util.getXY,ed[2]['bs'].interimPoints)
                dirtj = True and self.trajdir[tuple([ed[0],ed[1]])]
            elif tuple(sorted([ed[0],ed[1]])) == tuple(sorted(stroke)):
                pnt =  map(util.getXY,ed[2]['bs'].interimPoints)           
                dirtj = True and not self.trajdir[tuple([ed[0],ed[1]])]
                        
        if dirtj:
            return pnt
        else:
            return list(reversed(pnt[:]))       
    
    # Return which direction a stroke is
    # A stroke A->B could be internally saved as  (A,B) or (B,A). Checking which way the stroke is saved    
    def getStrokeDir(self,stroke):
        for ed in self.gl.G.edges(data=True):
            if tuple([ed[0],ed[1]]) == tuple(stroke):
                dirtj = True and self.trajdir[tuple([ed[0],ed[1]])]
            elif tuple(sorted([ed[0],ed[1]])) == tuple(sorted(stroke)):
                dirtj = True and not self.trajdir[tuple([ed[0],ed[1]])]
                        
        return dirtj    
            
    def myCloseEvent(self, event):
        #print "Closing"
        event.accept()
        
        
if __name__ == '__main__':
    app = QApplication(sys.argv)
    window = mainWindow()
    window.mainWindow.show()
