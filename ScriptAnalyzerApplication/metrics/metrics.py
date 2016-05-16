import Polygon as pg
import douglas as dg
import numpy as np
from glyphAnalyzer import glyphAnalyzerItems as ga
import collections
import cv2
from utilities import util
import itertools, math

from scipy.spatial import *

## Disjoint Strokes
### updownStrokes
### penStrokes

### Distance between first and last points / between strokes
### Angle between first and last points / between stromes 

#### see how multi-stroke characters behave

### Bounding Box or convex hull.. which to use :-/

### Primary and Secondary Direction

### Closure vs Openness

## Angle between internal strokes ?

## Macro Features... not taking consequent but staggered points

# Input list of points


def crossings(allPoints):
    duplicateP = []
    duplicatediff = []
    for i,p1 in enumerate(allPoints):
        for j,p2 in enumerate(allPoints):
            if util.dist(p1,p2) < 50 and math.fabs(i-j) > 5:
                    #duplicateP.append()
                    print util.dist(p1,p2),math.fabs(i-j)
                
            
    
    #print "The number of intersections are... ",duplicate
    
    return 
    


def boundingBox(x,y):
        
    return (max(x)+1, min(x)+1, max(y)+1, min(y)+1)

def principalAxes():
    
    return 

    ## return Curvature
    
def curvature(strokePoints):
    BS = ga.BSpline(strokePoints)
    x,y = util.coOrd(strokePoints,0),util.coOrd(strokePoints,1)
    if(util.checkLine(x,y)):
        print "This is a line"
        return [0]
                        
    uout = util.u_interval(5000)        
    k = util.calcCurvature(uout, BS.tck)
        
    return k 

    
####### Metrics ##################

### Retrace ? 
def totalLength(strokes):
        
    return sum(map(util.lengthPnts,strokes))

# Area of Convex Hull
def convexHullArea(points):  
    import scipy  
    try:
        hull = ConvexHull(np.asarray(points))
        vertex = [points[v] for v in hull.vertices] 
        hullPolygon = pg.Polygon(vertex)
        area = hullPolygon.area()
    except scipy.spatial.qhull.QhullError:
        area = 0
    
    return area

# Area of the Bounding Box
def boundingArea(points):
    x,y = util.coOrd(points,0), util.coOrd(points,1)    
    
    xMax, xMin, yMax, yMin = boundingBox(x,y)
        
    return (xMax - xMin) * (yMax - yMin)   

def eccentricity(points):
    x,y = util.coOrd(points,0), util.coOrd(points,1)
    
    xMax, xMin, yMax, yMin = boundingBox(x,y)
    
    a,b = xMax - xMin, yMax - yMin
    
    if a > b:
        return (1-(b**2/a**2))**0.5
    else:
        return (1-(a**2/b**2))**0.5
    
# Ratio of Breadth to Length ^^ Ratio of Co-ordinate axes
def breathIndex(points):
    x,y = util.coOrd(points,0), util.coOrd(points,1)
    
    xMax, xMin, yMax, yMin = boundingBox(x,y)
    
    print xMax, xMin, yMax, yMin
        
    return float(xMax - xMin) / (yMax - yMin)

## Length/Dist b/w first and last points :: Similar to Openness
def closure(strokes,points):
    x,y = util.coOrd(points,0), util.coOrd(points,1)
    
    return totalLength(strokes)/util.dist(points[0],points[1])

def circularVariance():
    
    return

def avgCurvature(strokes):
    
    return np.mean(curvature(strokes))

def avgDirections(strokePoints):
    
    direc = [abs(util.angle(strokePoints[i],strokePoints[i+1])) for i in range(len(strokePoints)-1)]
    
    return np.mean(direc)
        

def Perpendicularity(strokePoints):
    k = curvature(strokePoints)
    
    return sum([math.sin(c)**2 for c in k])


def rectangularity(points):
    return convexHullArea(points)/boundingArea(points)

def circularity(points):
    import numpy
    
    x,y = util.coOrd(points,0), util.coOrd(points,1)
    xMax, xMin, yMax, yMin = max(x), min(x), max(y), min(y)
    
    idealRad = numpy.mean([(xMax-xMin),(yMax-yMin)])/2
    
    idealArea = math.pi*(idealRad**2)    
    
    return  convexHullArea(points)/idealArea

# Intial Angle of stroke
def initialAngle(stroke):    
     
    return util.angle(stroke[0],stroke[-1])

def distFirstLastPoint(points):
    x,y = util.coOrd(points,0), util.coOrd(points,1)    
    
    return util.dist((x[0],y[0]), (x[-1],y[-1]))

def angleBetweenFirstLastPoint(points):
    x,y = util.coOrd(points,0), util.coOrd(points,1)
    
    return util.angle((x[0],y[0]), (x[-1],y[-1]))

#def averageCurvature():
#    
#    return


def openness(x,y):
    
    return distFirstLastPoint(x,y)/float(boundingArea(x,y))


### Shows how the pen has moved along arious time
def aspect(points):
    x,y = util.coOrd(points,0), util.coOrd(points,1) 
    
    xMax, xMin, yMax, yMin = boundingBox(x,y)
     
    return util.angle((xMin,yMax), points[0])


##### Call this Compactness
#def densityMetric1(allPoints):
#    
#    
#    
#    return totalLength(strokes)
##
#def densityMetric2():
#    
#    return


def minimumPoints(penStrokes):
    minPoints = 0
    
    for penstroke in penStrokes:
        x,y = util.coOrd(penstroke,0), util.coOrd(penstroke,1)
        
        print x
        print y
        
        if not util.checkLine(x, y):
            smpPnts, tck =  dg.reduceP(penstroke)
            minPoints += len(smpPnts)
        else:
            print "Called once"
            minPoints += 2
    
    return minPoints

def penMoveDistance(penStrokes): # Absolute  : Divide by length
    moveDist = 0
    
    for i in range(len(penStrokes)-1):
        moveDist += util.dist(penStrokes[i][-1],penStrokes[i+1][0])

    return moveDist 

def angleBetweenPenstrokes(penStrokes): ## 
    moveAngle = []
    
    for i in range(len(penStrokes)-1):
        moveAngle.append(util.angle(penStrokes[i][-1],penStrokes[i+1][0]))

    return moveAngle     

#def velocityInversion(updStrokes):
#    
#    
#    return

## Updstrokes/Downstrokes or just strokes
def xMovyMovStrokes(strokes):
    xyDel = []
    
    for stroke in strokes:
        pnt = stroke#.points 
        xyDel.append(((pnt[0][0]-pnt[-1][0]),(pnt[0][1]-pnt[-1][1])))
    
    return xyDel 

def angleinbetweenStrokes(strokes):
    moveAngle = []
    for i in range(len(strokes)-1):
        moveAngle.append(util.angle(strokes[i],strokes[i+1]))
                         
    return moveAngle    

def sharpness():
    
    return 

def curviness():
    
    return 

## Change below to length
def Ascension(aboveLine,pnts):
    return len([pnt for pnt in pnts if aboveLine-pnt[1] <= 0])

def Descendancy(baseLine,pnts):
    
    return len([pnt for pnt in pnts if baseLine-pnt[1] >= 0])

## Todo
def crossigngPoints():
    
    return

### ToDo - Number of Upstrokes and downstrokes ??
def curvaturePoints():
    
    return

def totalAngle():
    
    return 

## Option of returnign the count the ration based on length
def upDownRation(upStrokes,downStrokes,count=False):
    
    if not count:
        return float(len(upStrokes))/len(downStrokes)
    else:
        upLength = [util.lengthPnts(strokes) for strokes in upStrokes]
        downLength = [util.lengthPnts(strokes) for strokes in downStrokes]
        
        return float(upLength)/downLength
    
    return
    
    
### Done Already
    
#def numberofStrokes():
#    
#    return

def velocityInversion(strokes):
    count = 0
    
    for i in range(len(strokes)-1):
        if strokes[i][1] != strokes[i+1][1]:
            count += 1
            
    return count


### Try getting it for stroeks instead of the individual points
def getQuadrant(point,bbox):
    
    xMax, xMin, yMax, yMin = bbox
    
    midPoint = lambda p1,p2: (float(p1[0]+p2[0])/2, float(p1[1]+p2[1])/2)
    
    topLeft = (xMin,yMin)
    topRight = (xMax,yMin)
    bottomRight = (xMax,yMax)
    bottomLeft = (xMin,yMax)
    
    topHalf = midPoint((xMin,yMin),(xMax,yMin))
    rightHalf = midPoint((xMax,yMin),(xMax,yMax))
    bottomHalf = midPoint((xMin,yMax),(xMax,yMax))
    leftHalf = midPoint((xMin,yMin),(xMin,yMax))
    
#    print topLeft,topRight,bottomRight,bottomLeft
#    print topHalf,rightHalf,bottomHalf,leftHalf
    
    center = midPoint(topHalf,bottomHalf)
    
    q = []
    
    q += [pg.Polygon([topHalf,topRight,center])]
    q += [pg.Polygon([topRight,rightHalf,center])]
    q += [pg.Polygon([rightHalf,bottomRight,center])]
    q += [pg.Polygon([bottomRight,bottomHalf,center])]
    q += [pg.Polygon([bottomHalf,bottomLeft,center])]
    q += [pg.Polygon([bottomLeft,leftHalf,center])]
    q += [pg.Polygon([leftHalf,topLeft,center])]
    q += [pg.Polygon([topLeft,topHalf,center])]
    
    #print q
    
#    q = []
#    
#    q += [pg.Polygon([topHalf,center,rightHalf,topRight])]
#    q += [pg.Polygon([center,rightHalf,bottomRight,bottomHalf])]
#    q += [pg.Polygon([leftHalf,center,bottomHalf,bottomLeft])]
#    q += [pg.Polygon([topRight,topHalf,center,leftHalf])]
    
    for i, quad in enumerate(q):
        if quad.isInside(point[0],point[1]):
            return i+1
        
    return 0


### Use Length instead of points         
def getDirectionDist(points):
    x,y = util.coOrd(points,0), util.coOrd(points,1)
    bbox = boundingBox(x,y)
    
    q = [0 for i in range(0,9)]
    
    for point in points:
        q[getQuadrant(point,bbox)] += 1
        
    return q
    
def getDirectionChange(points):
    x,y = util.coOrd(points,0), util.coOrd(points,1)
    
    bbox = boundingBox(x,y)
    
    transition = []
        
    for i in range(len(points)-1):
        qi, qj = getQuadrant(points[i],bbox), getQuadrant(points[i+1],bbox) 
        if qi != qj:
            transition.append((qi,qj))
            
    return transition

def TotalAngle():
    
    return

#### Number of Stright Lines
#### Number of Curves
#### Number of Cups etc


### Number of Straight Lines
def NumberofCups():
    
    return

#### Is this necessary ??????
def connectedComponent():
    
    return 


### All these ratios whether to use length or area.     

### For writing - lenth makesmore sense

### Visually - Area makes more sense

### Strokes per Area/length - Calculate dynamically - in the Visualization

#def strokesPerLength():
#    
#    return
#
#def angleperLength():
#    
#    return

#def directionStroke():
#    
#    return 
#
#def directionGlyph():
#    
#    return
#
#def directionChange():
#    
#    return

def avgDirection():
    
    return 


def penUppenDownratio():
    
    return 

def inflexionPoints():
    
    return 

#### Visualization of Angle Histogram

### Distribution of points historgram
def Deviation():
    
    return 

def clockWise():
    
    return

def AnitClockwise():
    
    return

def huMoments(points):
    
    ## Can be done using OpenCV
    
    #cv2.moments()
    #cv2.HuMoments() 

    return 


#def fractalDimension():
#    
#    return

#def VisualCmplexity():
#    
#    return 

#def rectangularity():
#    
#    return
#
#def circularness():
#    
#    return 


def directionCodeGlyph(strokes):
    dirCode = [util.directionCodes(stroke) for stroke in strokes]
    
    return dirCode

def Entropy(strokes):
    import math
    
    dirCode = directionCodeGlyph(strokes)
    
    print dirCode
    
    prob = [(dirCode.count(e)/float(len(dirCode))) for e in list(set(dirCode))]
    
    entropy = -sum([p*math.log(p) for p in prob])
    
    return entropy    
    
#print np.asarray([(1,2),(2,4),(4,5),(6,8)])
#
#convexHull([1,2,3,4,2,20],[3,6,7,8,10,30])
