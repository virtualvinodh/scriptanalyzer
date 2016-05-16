### Pyside Imports
from PySide.QtCore import *
from PySide.QtGui import *
from PySide.QtUiTools import *

import imageProcess.ImageProcessing as IP ### Basic Image Processing such as thinning etc.
import numpy,time

from glyphAnalyzerItems import *

# View to create and modify glyphs
class glyphScene(QGraphicsScene):
    GridXStep = 10
    GridYStep = 10
    NodeSeq = 65 # NodeSeq Add
    
    def __init__(self, parent,*args, **kwargs):
        super(glyphScene, self).__init__(*args, **kwargs)

        self.setSceneRect(QRect(0, 0, 500, 330))
        self.setBackgroundBrush(QColor('#FFFFFF'))
        self.addGrid()
        
        self.parent = parent
        
        self.Nodes=[]
        self.Edges=[]
        self.EdgePair=[]  
        self.EdgePairs = []  

    def addGrid(self):
        pen = QPen(QColor('#BFBFBF'))
        x,y = 0,0
        
        while x <= self.width():
            self.addLine(x, 0, x, self.height(), pen)
            x += self.GridXStep

        while y <= self.height():
            self.addLine(0, y, self.width(), y, pen)
            y += self.GridYStep
            
    def addImage(self,imgPath):
        self.imgPath = imgPath[0]
        
        if self.imgPath =="":
            self.imgPath = 'C:\Users\Administrator\Documents\XenoType Brahmi 180\U_01102D.bmp'
    
        IP.ThinImage(self.imgPath)
        
        glyph = QPixmap(self.imgPath)
        self.addPixmap(self.drawTranspImage(glyph,0.1))
        
        thinned = QPixmap("thinned.png")
    
        self.addPixmap(self.drawTranspImage(thinned,0.5))
        
        import Image
        img = Image.open("thinned.png").convert('L')
        self.imgArray = numpy.asarray(img)
        
        #print "here"
        
    def drawTranspImage(self,img,transp):
        imgRes = QPixmap(img.size())
        imgRes.fill(Qt.transparent)
        painter = QPainter()
        painter.begin(imgRes);
        painter.setOpacity(transp);
        painter.drawPixmap(0, 0, img);
        painter.end()
        
        return imgRes
    
    def addNode(self,x,y):
#        print "Adding Node"
        pnt = NodePoint(chr(self.NodeSeq),x,y,parent=self)
        
        nodeExists = False
        
        for p in self.Nodes:
            #print x,y, p.xP, pnt.yP
            if util.dist((p.xP,p.yP),(x,y)) < 10:
                nodeExists = True
                
        if not nodeExists:
            self.Nodes.append(pnt)
            self.addItem(pnt)
            self.NodeSeq = self.NodeSeq+1
        
    def removeSpline(self,bs):
        path = QPainterPath()
        path.addPolygon(QPolygonF([QPointF(0, 0)]))
        bs.setPath(path) 
        
        #print "----------------------------"
        #print bs.notupdate
        bs.notupdate = True
        #print bs.notupdate
        #print "----------------------------"
        
        for tangent in bs.segments:
            tangent.hide()
        
        for point in bs.interimPoints:
            point.hide()
            
    def removeNode(self,node):
        self.Nodes.remove(node)
        self.removeItem(node)
        self.NodeSeq = self.NodeSeq - 1
                
    def mouseDoubleClickEvent(self,event):
        super(glyphScene, self).mouseDoubleClickEvent(event)
        item = self.itemAt(event.pos())
                    
        if item != None:
            self.addNode(event.scenePos().x(),event.scenePos().y())
            
        self.parent.updateTraceView()

    # Updating TraceView everytime an update happens in GlyphView                
    def mouseMoveEvent(self,event):
        super(glyphScene, self).mouseMoveEvent(event)
        self.parent.updateTraceView()            
                                
    # Create BSpline                                
    def addBSpline(self,interimPoints,EP0,EP1):
        BS = BSpline(interimPoints)
        self.addItem(BS)
    
        self.Edges.append((EP0,EP1,BS))
    
        return BS
                    
    def addEdge(self):
        if len(self.EdgePair) == 2:
            interimPoints = []
            interimPoints.append((self.EdgePair[0].scenePos().x(),self.EdgePair[0].scenePos().y()))
            
            MPx = (self.EdgePair[0].scenePos().x() + self.EdgePair[1].scenePos().x()) /2 
            MPy = (self.EdgePair[0].scenePos().y() + self.EdgePair[1].scenePos().y()) / 2
            interimPoints.append((MPx,MPy))
            
            interimPoints.append((self.EdgePair[1].scenePos().x(),self.EdgePair[1].scenePos().y()))
            
            BS = self.addBSpline(interimPoints,self.EdgePair[0],self.EdgePair[1])
            self.EdgePairs.append(self.EdgePair)
            self.EdgePair=[]                


class crossHairLine(QGraphicsLineItem):
    def __init__(self,*args,**kwargs):
        super(crossHairLine,self).__init__(*args,**kwargs)
        pen = QPen(QColor("#C0C0C0"))

        self.setPen(pen)

class traceScene(QGraphicsScene):
    SceneRect = QRect(0, 0, 500, 330)
    GridXStep = 10
    GridYStep = 10
    
    def __init__(self, parent, *args, **kwargs):
        super(traceScene, self).__init__(*args, **kwargs)

        self.setSceneRect(QRect(0, 0, 500, 330))
        self.setBackgroundBrush(QColor('#FFFFFF'))
        
        self.pointList = []
        self.pointTime = []
        self.start = time.time()
        
        self.parent = parent
        
        self.modified = False
        self.scribbling = False        
        
        self.baseLines=[]
        
        #self.addGrid()

        self.pen = QPen(QColor("#FF0000"))     
        
    def addGrid(self):
        pen = QPen(QColor('#BFBFBF'))
        x,y = 0,0
        
        while x <= self.width():
            self.addLine(x, 0, x, self.height(), pen)
            x += self.GridXStep

        while y <= self.height():
            self.addLine(0, y, self.width(), y, pen)
            y += self.GridYStep                 

    # Adding Baselines and Ascender lines
    def mousePressEvent(self, event):
        
        if event.button() == Qt.LeftButton:
            #print event.scenePos()
            self.lastPoint = event.scenePos()
            self.scribbling = True
        else:
            if len(self.baseLines) < 2:
                self.addLine(0, event.scenePos().y(), self.width(), event.scenePos().y(), self.pen)
                self.baseLines.append(event.scenePos().y())
                self.baseLines.sort()
                #print "The baselines are ", self.baseLines

    # MouseMove, MouseRelese, drawLineto to create free drawing

    def mouseMoveEvent(self, event):
        super(traceScene, self).mouseMoveEvent(event)
        
        for item in self.items():
            if isinstance(item,crossHairLine):
                item.hide()
        
        if (event.buttons() & Qt.LeftButton) and self.scribbling:
            self.drawLineTo(event.scenePos())
        else:
            
            self.addItem(crossHairLine(event.scenePos().x(), 0, event.scenePos().x(), self.height()))
            self.addItem(crossHairLine(0, event.scenePos().y(), self.width(), event.scenePos().y()))
            
            
#    def hoverEnterEvent(self,event):
#        #print "hello"

    def mouseReleaseEvent(self, event):
        if event.button() == Qt.LeftButton and self.scribbling:
            self.drawLineTo(event.pos())
            self.scribbling = False
            
            self.parent.writeStroke()               

    def drawLineTo(self, endPoint):
        if (self.lastPoint != endPoint and endPoint) and endPoint != QPointF(0.000000, 0.000000):
            self.addLine(self.lastPoint.x(),self.lastPoint.y(),endPoint.x(),endPoint.y(), self.pen)    
            
            self.pointList.append(self.lastPoint)
            self.pointTime.append(((self.lastPoint,endPoint),time.time()-self.start))
    
            self.lastPoint = QPoint(int(endPoint.x()),int(endPoint.y()))
            
            self.modified = True
            
    def getPointList(self):
        return self.pointList


# View Delineating the Strokes            
class strokeScene(QGraphicsScene):
    GridXStep = 10
    GridYStep = 10
    
    def __init__(self, *args, **kwargs):
        super(strokeScene, self).__init__(*args, **kwargs)

        self.setSceneRect(QRect(0, 0, 500, 330))
        self.setBackgroundBrush(QColor('#FFFFFF'))
        self.baseLines=[]
        
# Creating Curvature Node Class
class CurvPoint(QGraphicsEllipseItem):
    def __init__(self, *args, **kwargs):
        super(CurvPoint, self).__init__(*args, **kwargs)
        print "Here"
        
    def itemChange(self, change, value):
        if change == QGraphicsItem.ItemPositionHasChanged:
            print "Item moved"
            print value.x(), value.y()
        
# View Delineating the Substrokes        
class subStrokeScene(QGraphicsScene):
    BackgroundColor = QColor('#FFFFFF')
    GridColor = QColor('#BFBFBF')
    SceneRect = QRect(0, 0, 500, 330)
    GridXStep = 10
    GridYStep = 10
    
    def __init__(self, *args, **kwargs):
        super(subStrokeScene, self).__init__(*args, **kwargs)

        self.setSceneRect(self.SceneRect)
        self.setBackgroundBrush(self.BackgroundColor)
        self.baseLines=[]
        self.log= ""
        
        self.subStrokePoints = []
        
    def drawNodes(self,xC,yC,color="#FFFFFF"):
        #curvNode = CurvPoint(-4,-4,8,8)
        curvNode = QGraphicsEllipseItem(-4,-4,8,8)
        curvNode.setPos(xC,yC)
        curvNode.setBrush(QColor(color))        
        curvNode.setFlags(QGraphicsItem.ItemIsMovable |
                      QGraphicsItem.ItemSendsGeometryChanges)   
        
        self.addItem(curvNode)   
        
        self.subStrokePoints.append(curvNode)   
        
    def mouseDoubleClickEvent(self,event):
        super(subStrokeScene,self).mouseDoubleClickEvent(event)    
        
        self.drawNodes(event.scenePos().x(),event.scenePos().y()) 
        
        self.log += time.asctime( time.localtime(time.time())) + "\n"
        self.log += "Segmentation Change: New Segmentation Point\n"
        self.log += "Insert at: " + str(event.scenePos().x()) + ", " + str(event.scenePos().y())  + "\n\n"
        print self.log
        
        
