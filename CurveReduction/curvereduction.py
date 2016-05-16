import time

from PySide import QtCore, QtGui,QtUiTools

from scipy.interpolate import splev,splprep
from douglas import reduceP

import sys
import matplotlib
matplotlib.use('Qt4Agg')
matplotlib.rcParams['backend.qt4']='PySide'
import pylab
        
from matplotlib.backends.backend_qt4agg import FigureCanvasQTAgg as FigureCanvas
from matplotlib.figure import Figure
       
class ScribbleArea(QtGui.QWidget):
    def __init__(self, parent=None):
        super(ScribbleArea, self).__init__(parent)

        self.setAttribute(QtCore.Qt.WA_StaticContents)
        self.modified = False
        self.scribbling = False
        self.myPenWidth = 1
        self.myPenColor = QtCore.Qt.blue
        self.image = QtGui.QImage()
        self.lastPoint = QtCore.QPoint()
        
        self.pointList = []
        self.pointTime = []
        self.start = time.time()
        
        self.pointListR = []
        
        self.addImage()
        
#        newSize = QtCore.QSize(531, 671)
#        newImage = QtGui.QImage(newSize, QtGui.QImage.Format_RGB32)
#        newImage.fill(QtGui.qRgb(255, 255, 255))
#        painter = QtGui.QPainter(newImage)
#        painter.drawImage(QtCore.QPoint(0, 0), self.image)
#        self.image = newImage          
        
    def addImage(self):
        newSize = QtCore.QSize(531, 671)
        newImage = QtGui.QImage(newSize, QtGui.QImage.Format_RGB32)
        newImage.fill(QtGui.qRgb(255, 255, 255))
        painter = QtGui.QPainter(newImage)
        painter.drawImage(QtCore.QPoint(0, 0), self.image)
        self.image = newImage     
        
    def clearImage(self):
        self.image.fill(QtGui.qRgb(255, 255, 255))
        self.modified = True
        self.update()              
        
    def mousePressEvent(self, event):
        if event.button() == QtCore.Qt.LeftButton:
            self.lastPoint = event.pos()
            self.scribbling = True
            
    def mouseMoveEvent(self, event):
        if (event.buttons() & QtCore.Qt.LeftButton) and self.scribbling:
            self.drawLineTo(event.pos())

    def mouseReleaseEvent(self, event):
        if event.button() == QtCore.Qt.LeftButton and self.scribbling:
            self.drawLineTo(event.pos())
            self.scribbling = False

    def tabletEvent(self,event):
        if event.pressure() > 0:
            print event.pressure(),event.tangentialPressure(),event.xTilt(),event.yTilt(),event.x(),event.y(),event.device() #hiResGlobal
            if self.modified == False:
                self.pointListR.append((QtCore.QPoint(event.x(),event.y()),time.time()-self.start))
                self.lastPoint = QtCore.QPoint(event.x(),event.y())
                self.modified = True
            else:
                self.pointListR.append((QtCore.QPoint(event.x(),event.y()),time.time()-self.start))                
                self.drawLineTo(QtCore.QPoint(event.x(),event.y()))
        elif event.pressure() == 0:
            self.modified = False
        
    def paintEvent(self, event):
        painter = QtGui.QPainter(self)
        painter.drawImage(QtCore.QPoint(0, 0), self.image)

    def drawLineTo(self, endPoint):
        painter = QtGui.QPainter(self.image)
        painter.setPen(QtGui.QPen(self.myPenColor, self.myPenWidth,
                QtCore.Qt.SolidLine, QtCore.Qt.RoundCap, QtCore.Qt.RoundJoin))
        if self.lastPoint != endPoint:
            painter.drawLine(self.lastPoint, endPoint)
            self.modified = True
            
            self.pointList.append(self.lastPoint)
            self.pointTime.append(((self.lastPoint,endPoint),time.time()-self.start))
    
            rad = self.myPenWidth / 2 + 2
            self.update(QtCore.QRect(self.lastPoint, endPoint).normalized().adjusted(-rad, -rad, +rad, +rad))
            self.lastPoint = QtCore.QPoint(endPoint)

class MainWindow(QtGui.QMainWindow):
    def __init__(self):
        super(MainWindow, self).__init__()
        
        Loader = QtUiTools.QUiLoader()
        uiFile = QtCore.QFile("C:/Qt/Qt5.0.1/Tools/QtCreator/bin/ScriptAnalyzerNew/scriptreduce.ui")
        
        uiFile.open(QtCore.QFile.ReadOnly)
        
        self.scribbleWindow = Loader.load(uiFile)
    
        self.scribbleArea = ScribbleArea()
        layout = QtGui.QVBoxLayout()
        layout.addWidget(self.scribbleArea)
        self.scribbleWindow.scribbleArea.setLayout(layout)
        
        self.dpi = 100
        self.fig = Figure((6.0, 4.0), dpi=self.dpi)
        self.axes = self.fig.add_subplot(111)
        self.axes.invert_yaxis()

        self.canvas = FigureCanvas(self.fig)
        layout = QtGui.QVBoxLayout()
        layout.addWidget(self.canvas)
        self.canvas.setParent(self.scribbleWindow.velocityArea)
        
        self.scribbleWindow.velocityArea.setLayout(layout)               
        
        self.scribbleWindow.velocityBtn.clicked.connect(self.reducePnts)
        self.scribbleWindow.clearBtn.clicked.connect(self.clear)
        
        self.scribbleWindow.smoothingTxt.setPlainText('11')
        
    
    def clear(self):
        self.scribbleArea.clearImage()
        self.scribbleArea.pointList = []
        
        self.axes.clear()       
        self.axes.axis('Equal') 
        self.axes.grid(True)
        self.canvas.draw()
    
    def reducePnts(self):
        pointList = [(p.x(),p.y()) for p in self.scribbleArea.pointList]
                
        self.axes.clear()       
        self.axes.axis('Equal') 
        self.axes.grid(True)            
        
        if self.scribbleWindow.smoothingTxt.toPlainText() != "":
            errT = int(self.scribbleWindow.smoothingTxt.toPlainText())
        else:
            errT = 11     
        
        smPnts,tck = reduceP(pointList,errT)
                        
        xRed = [p[0] for p in smPnts]
        yRed = [p[1] for p in smPnts]     
                
        uout = list((float(i) / 300 for i in xrange(300 + 1)))   
        xSp,ySp = splev(uout,tck)            
        
        self.scribbleWindow.minPntLbl.setText(str(len(smPnts)))
        
        self.axes.plot(xRed,yRed,'go')
        self.axes.plot(xSp,ySp,'r')

        self.canvas.draw()        
        
if __name__ == '__main__':
    app = QtGui.QApplication(sys.argv)
    window = MainWindow()
    window.scribbleWindow.show()
    sys.exit(app.exec_())