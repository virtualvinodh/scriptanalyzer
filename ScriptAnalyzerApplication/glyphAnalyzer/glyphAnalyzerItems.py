### Pyside Imports
from PySide.QtCore import *
from PySide.QtGui import *
from PySide.QtUiTools import *

from utilities import util ### Utilities functions that are re-usable
from scipy.interpolate import splprep,splev
import math

# Interiim Point : Movable | Updates Curve
class interimPoint(QGraphicsEllipseItem):

    def __init__(self, x, y, PointRadius, spline, *args, **kwargs):
        super(interimPoint, self).__init__(*args, **kwargs)

        self.setFlags(QGraphicsItem.ItemIsMovable |
                      QGraphicsItem.ItemSendsGeometryChanges)       
        
        #self.angle = QGraphicsTextItem("",self) 
        
        self.spline = spline
        self.PointRadius = PointRadius

        self.setBrush(QColor('#FF7F00'))

        self.setPos(x, y)
        self.setRect(-self.PointRadius, -self.PointRadius, 2 * self.PointRadius, 2 * self.PointRadius)

    # Update BSpline when control points are moved
    def itemChange(self, change, value):
        if change == QGraphicsItem.ItemPositionHasChanged:
            self.spline.updateSpline()

        return super(interimPoint, self).itemChange(change, value)
    
    # Left double click - Add Control Points
    # Right double click - Remove control Points
    def mouseDoubleClickEvent(self,event):
        super(interimPoint,self).mouseDoubleClickEvent(event)
        if str(event.button()) == "PySide.QtCore.Qt.MouseButton.LeftButton":        
            self.spline.addInterimPoints(self)
        else:
            if len(self.spline.interimPoints) > 3:
                self.hide()
                self.spline.removeInterimPoints(self)
        
    def mousePressEvent(self,event):
        pass
        #angle = math.degrees(util.angle(util.getXY(self.spline.interimPoints[0]),util.getXY(self.spline.interimPoints[-1])))
#        self.angle.setParentItem(None)
#        self.angle = QGraphicsTextItem(str(event.scenePos().x())+" "+str(event.scenePos().y()),self)
        
        #print self.angle.toPlainText(), "IP is selected", 
        
        
# Node Point for Glyph Segments
class NodePoint(QGraphicsEllipseItem):
    PointRadius = 5        

    def __init__(self, labelName, x, y, parent, *args, **kwargs):
        super(NodePoint, self).__init__(*args, **kwargs)
        
        self.setFlags(QGraphicsItem.ItemIsMovable |
                      QGraphicsItem.ItemSendsGeometryChanges)
        

        #Label Object
        self.label = QGraphicsTextItem(labelName, self) 
        
        self.parent = parent

        self.setBrush(QColor('#5656CD'))

        self.setPos(x, y)
        self.setRect(-self.PointRadius, -self.PointRadius, 2 * self.PointRadius, 2 * self.PointRadius)
        self.xP, self.yP = x,y #self.scenePos().x(), self.scenePos().y()
        
    def itemChange(self, change, value):
        if change == QGraphicsItem.ItemPositionHasChanged:
            #print value
            for item in self.parent.items():
                try:
                    if isinstance(item,interimPoint) and item.scenePos().x() == self.xP and item.scenePos().y() == self.yP:
                        item.setPos(value.x(),value.y())
                except AttributeError:
                    pass
            
            self.xP, self.yP = value.x(), value.y()

        return value
        
    def mousePressEvent(self,event):
        splines = []
        
        #print self.label.toPlainText(), "is selected", event.scenePos().x(), event.scenePos().y()
        
        for item in self.parent.items():
            try:
                if isinstance(item,interimPoint) and item.scenePos().x() == self.xP and item.scenePos().y() == self.yP:
                    splines.append(item)
            except AttributeError:
                pass
        
        if len(splines) == 2 :        
            s1 =  splines[0].spline.interimPoints.index(splines[0])
            s2 = splines[1].spline.interimPoints.index(splines[1])
            
            if s1==0:
                s1A,s1B = splines[0].spline.controlPoints[0],splines[0].spline.controlPoints[1]                
            else:
                s1A,s1B = splines[0].spline.controlPoints[s1],splines[0].spline.controlPoints[s1-1]
                
            if s2==0:
                s2A,s2B = splines[1].spline.controlPoints[0],splines[1].spline.controlPoints[1]                
            else:
                s2A,s2B = splines[1].spline.controlPoints[s2],splines[1].spline.controlPoints[s2-1]   
                
            m1,m2 = util.slope(s1A,s1B),util.slope(s2A,s2B)
            
            #self.label.setParentItem(None)
            
            #print str(math.degrees(util.angleFromSlope(m1, m2)))
        
    def mouseDoubleClickEvent(self,event):
        if str(event.button()) == "PySide.QtCore.Qt.MouseButton.LeftButton":        
            self.parent.EdgePair.append(self)
            self.parent.addEdge()
            #print self.label.toPlainText(), "is selected for line", event.scenePos().x(),event.scenePos().y()
        else:
            self.parent.removeNode(self)   
                        
#Quadratic BSpline Class ;
class BSpline(QGraphicsPathItem):
    
    def __init__(self, interimPoints, *args, **kwargs):
        super(BSpline, self).__init__(*args, **kwargs)
        
        self.degree = 2 # Quadratic Bspline
        self.renderingSteps = 200 # Number of points for defining the curve
                
        self.interimPoints = []
        
        self.segments = []
        self.notupdate = False
     
        self.setPen(QColor('#5656CD'))
        
        for num, pnt in enumerate(interimPoints):
            if num == 0 or num == len(interimPoints)-1 :
                PointRadius = 0
            else:
                PointRadius = 4
                
            self.interimPoints.append(interimPoint(pnt[0], pnt[1], PointRadius, self, parent=self))
            
        self.updateSpline()
        
    def __copy__(self):
        BsGraphPath = QGraphicsPathItem()
        BsPath = QPainterPath()
        BsGraphPath.setPath(self.path)
        
        return BsGraphPath
        
        self.__init__(self.degree, self.interimPointsNumber, self.interimPoints)
    
    def addInterimPoints(self, cpCur):        
        cur = self.interimPoints.index(cpCur)
            
        IpNX = (self.interimPoints[cur-1].x() + cpCur.x())/2
        IpNY = (self.interimPoints[cur-1].y() + cpCur.y())/2
        
        IpN = interimPoint(IpNX, IpNY, 4, self, parent=self)
        
        self.interimPoints.insert(cur,IpN)
        self.updateSpline()    
        
    def removeInterimPoints(self,cpCur):
        self.interimPoints.remove(cpCur)
        self.updateSpline()
        
    def updateSpline(self):       
                         
        if len(self.interimPoints) < 3:
            return
        
        x,y = [p.scenePos().x() for p in self.interimPoints], [p.scenePos().y() for p in self.interimPoints]
        
        self.tck,u = splprep([x,y],s=0.,k=2,per=False)
        
        self.controlPoints = zip(self.tck[1][0],self.tck[1][1])
        
        # Hide Previous Tangent Segments
        for seg in self.segments:
            seg.hide()
            
        self.segments = []
            
        if not self.notupdate:
            for i in range(len(self.controlPoints)-1):
                tangent = QGraphicsLineItem(QLineF(self.controlPoints[i][0], self.controlPoints[i][1], self.controlPoints[i+1][0],self.controlPoints[i+1][1]),self)
                tangent.setPen(QColor('#BFBFBF'))
                self.segments.append(tangent)
        
        uout = list((float(i) / self.renderingSteps for i in xrange(self.renderingSteps + 1)))
        
        x,y = splev(uout,self.tck)
        self.points = zip(x,y)
                                        
        if not self.notupdate:
            #print self.notupdate, "updating path"
            self.path = QPainterPath()
            self.path.addPolygon(QPolygonF([QPointF(x, y) for x, y in self.points]))
            self.setPath(self.path)     
        