import math, numpy
from scipy.interpolate import splev 

getXY = lambda p:(p.scenePos().x(),p.scenePos().y())

coOrd = lambda lst,cord : [p[cord] for p in lst]

def adjustAngle(x1,y1,x2,y2,ang):
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


def angleStrokes(stroke1,stroke2):
    m1, m2 = slope(stroke1[0],stroke1[-1]), slope(stroke2[0],stroke2[-1])
    ang = math.fabs(math.degrees(angleFromSlope(m1,m2)))
    
    return ang



def transformP(points,first=True):
    coOrd = lambda lst,cord : [p[cord] for p in lst]
    
    if first:
        points = map(lambda x: (points[0][0]-x[0],points[0][1]-x[1]),points)
    else:
        xP ,yP = coOrd(0), coOrd(1)
        points = map(lambda x: (points[0][0]-min(xP),x[1]-points[0][1]-min(yP)),points)
        
    return points

def get_line(x1, y1, x2, y2): #http://www.roguebasin.com/index.php?title=Bresenham%27s_Line_Algorithm
    points = []
    issteep = abs(y2-y1) > abs(x2-x1)
    if issteep:
        x1, y1 = y1, x1
        x2, y2 = y2, x2
    rev = False
    if x1 > x2:
        x1, x2 = x2, x1
        y1, y2 = y2, y1
        rev = True
    deltax = x2 - x1
    deltay = abs(y2-y1)
    error = int(deltax / 2)
    y = y1
    ystep = None
    if y1 < y2:
        ystep = 1
    else:
        ystep = -1
    for x in range(int(x1), int(x2) + 1):
        if issteep:
            points.append((y, x))
        else:
            points.append((x, y))
        error -= deltay
        if error < 0:
            y += ystep
            error += deltax
    # Reverse the list if the coordinates were reversed
    if rev:
        points.reverse()
    return points

        
def directionCodes(stroke):
        p1,p2 = stroke[0], stroke[-1]
        
        x1,y1 = p1
        
        x2,y2 = p2
        
        #print (x1-x2),(y1-y2),"code",
    
        if abs(x1 - x2) < 10 and y1 > y2:
            return "N" #A N
        elif abs(x1 - x2) < 10 and y2 > y1:
            return "S" #E S
        elif abs(y1 - y2) < 10 and x2 > x1:
            return "E" #C E
        elif abs(y1 - y2) < 10 and x1 > x2:
            return "W" #G W
        elif y1 > y2 and x2 > x1:
            return "NE" #B NE
        elif y1 > y2 and x1 > x2:
            return "NW" #H NW
        elif y2 > y1 and x2 > x1:
            return "SE" #D SE
        elif y2 >y1 and x1 >x2:
            return "SW" #F SW    

def UniqueLists(L):
    return [list(x) for x in set(tuple(x) for x in L)]

def uniquelistInd(L):
    L = ["_".join(["".join(m) for m in l]) for l in L]
    
    #print L
    
    known_links = set()
    newlist = []
    
    for d in L:
        link = d
        if link in known_links: 
                continue
        newlist.append(d)
        known_links.add(link)

    L[:] = newlist
    
    newList = [map(list,k.split('_')) for k in newlist]
    
    #print newList
    
    return newList
    


def angle(p1,p2):
    return math.atan(slope(p1,p2))

def lengthPnts(pnts):
     
    return sum([dist(pnts[i],pnts[i+1]) for i in range(len(pnts)-1)])

# Finding the between two points
def slope(p1,p2):
    #print "Calculating Slope", p1,p2
    if p1[0] != p2[0]:
        m = (float(p2[1] - p1[1])) / (p2[0] - p1[0])
    else:
        m = float('inf') 
            
    return m   

# From two Slopes calculate the angle
def angleFromSlope(m1,m2):
    #print "Calculating Angle from slopes", m1, m2
    
    if m1 != float('inf') and m2 != float('inf'):
        ang = (math.atan((m1 - m2) / (1 + (m1 * m2))))
    elif m1 == float('inf'):
        ang = (math.atan(numpy.float64(1) / m2))
    elif m2 == float('inf'):
        ang = (math.atan(numpy.float64(1) / m1)) 
        
    #print "Calculated angle is ", ang
        
    return ang


def u_interval(N):
    return list((float(i) / N for i in xrange(N + 1)))


# Distance between two points
def dist(p1,p2):
    return ((float(p1[0])-p2[0])**2 + (float(p1[1])-p2[1])**2)**0.5

def getclosestpnt(ls,nm):
    dif = sorted([(dist(l,nm),l,i) for i,l in enumerate(ls)])
        #print "Diff", dif
        
        #print "Closest of", nm, "is", dif[0][1]
        
    #print nm, dif 
    
    if dif[0][0] < 5:
        return dif[0][2]
    else:
        return


# Caculating Curvature for BSpline
# uout - Range of value s; tck - bspline parameters (Scipy)
# Return the list of the curvature from each point

def conjoinLists(k,threshold):
    i = 0
    kN = []
    print k
    
    if k == None:
        return []
    
    if len(k) == 1:
        return k
    
    while i < len(k)-1:
        print k[i],k[i+1], dist(k[i],k[i+1])
        if dist(k[i],k[i+1]) > threshold:
            kN.append(k[i])
        else:
            pM = ((k[i][0]+k[i+1][0])/2,(k[i][1]+k[i+1][1])/2)
            kN.append(pM)
            i = i + 1
            
        i=i+1    
        
    #print k , kN
    
    if len(k) > 2 and k[-2] == kN[-1]:
        kN.append(k[-1])
    
    return kN

def calcCurvature(uout,tck):
    dx,dy = splev(uout,tck,der=1)
    d2x,d2y = splev(uout,tck,der=2)
        
    slope = [yd/yx for yd,yx in zip(dx,dy)]
        
    k = abs(((dx*d2y) - (dy*d2x))) / (dx**2 + dy**2)**1.5
        
    return k


## Check if a set of x, y is a line are not
def checkLine(x,y,threshold=10):
#    x = [x[i] for i in range(len(x)) if i%4 ==0]
#    y = [y[i] for i in range(len(y)) if i%4 ==0]
    
    p, residuals, rank, singular_values, rcond = numpy.polyfit(x,y,deg=1,full=True)
    
    dist = lengthPnts(zip(x,y))
    
    print "distance", dist, residuals
    
    if len(residuals) != 0:
        print "Residual", residuals[0]/dist
    else:
        print "No Residual. Perfect Line"
    
    if len(residuals) == 0 or residuals[0]/dist < 5:
        return True
    else:
        return False

#### Check Paper     
def checkCircle(x,y,threshold):
    xMax, xMin, yMax, yMin = max(x), min(x), max(y), min(y)
    
    if dist((x[0],y[0]),(x[-1],y[-1])) > 4:
        return False
    
    idealRad = numpy.mean([(xMax-xMin),(yMax-yMin)])/2
    
    idealArea = math.pi*(idealRad**2)
    
    import Polygon as pg
    
    polygon = pg.Polygon(zip(x,y))
    
    ratio = float(idealArea)/polygon.area()
    
    print abs(1-ratio)
    
    if abs(1-ratio) < threshold:
        return True
    else:
        return False
    
    return 
    
def normalize(listL):
    mn, mx = min(listL), max(listL)
    rangeR = mx - mn
    if rangeR != 0:
        return [float(m - mn) / rangeR for m in listL]
    else:
        return [0 for m in range(0, len(listL))]   
    
    
if __name__ == "__main__":
    print checkCircle([1,3,15],[2,6,10],10)
    
    print lengthPnts([(1,2),(1,4),(1,6)])
    